import logging
import json
import os
from datetime import datetime
import pandas as pd
import numpy as np

from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators
from ml_feature_engineer import MLFeatureEngineer
from ml_models import MLModels

class MLTrainer:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.data_fetcher = DataFetcher(config_file)
        self.indicators = TechnicalIndicators(config_file)
        self.feature_engineer = MLFeatureEngineer(config_file)
        self.ml_models = MLModels(config_file)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        os.makedirs('models', exist_ok=True)
        os.makedirs('scalers', exist_ok=True)

    def prepare_training_data(self):
        self.logger.info("Preparing training data...")

        stock_data = self.data_fetcher.fetch_all_stocks_data()
        if not stock_data:
            self.logger.error("No stock data fetched")
            return None

        indicators_data = self.indicators.calculate_all_indicators(stock_data)
        if not indicators_data:
            self.logger.error("No indicators calculated")
            return None

        training_data = {}

        for symbol, data in indicators_data.items():
            self.logger.info(f"Preparing training data for {symbol}")

            engineered_data = self.feature_engineer.engineer_features(data)
            if engineered_data is None:
                self.logger.warning(f"Failed to engineer features for {symbol}")
                continue

            X, y, features = self.feature_engineer.prepare_sequences(engineered_data, symbol)
            if X is not None and y is not None:
                training_data[symbol] = (X, y, features)
                self.logger.info(f"Prepared {len(X)} sequences for {symbol}")
            else:
                self.logger.warning(f"Failed to prepare sequences for {symbol}")

        self.logger.info(f"Training data prepared for {len(training_data)} symbols")
        return training_data

    def train_all_models(self, training_data=None):
        if training_data is None:
            training_data = self.prepare_training_data()

        if not training_data:
            self.logger.error("No training data available")
            return None

        self.logger.info("Starting model training...")

        trained_models = self.ml_models.train_all_models(training_data)

        self._generate_training_report(trained_models)

        return trained_models

    def _generate_training_report(self, trained_models):
        try:
            report = {
                'training_date': datetime.now().isoformat(),
                'total_symbols': len(trained_models),
                'models_trained': [],
                'summary': {}
            }

            all_accuracies = {'LSTM': [], 'GRU': []}
            all_f1_scores = {'LSTM': [], 'GRU': []}

            for symbol, models in trained_models.items():
                for model_type, model_data in models.items():
                    model_info = model_data['info']

                    report['models_trained'].append({
                        'symbol': symbol,
                        'model_type': model_type,
                        'accuracy': model_info['accuracy'],
                        'precision': model_info['precision'],
                        'recall': model_info['recall'],
                        'f1_score': model_info['f1_score']
                    })

                    all_accuracies[model_type].append(model_info['accuracy'])
                    all_f1_scores[model_type].append(model_info['f1_score'])

            for model_type in ['LSTM', 'GRU']:
                if all_accuracies[model_type]:
                    report['summary'][model_type] = {
                        'avg_accuracy': np.mean(all_accuracies[model_type]),
                        'std_accuracy': np.std(all_accuracies[model_type]),
                        'avg_f1_score': np.mean(all_f1_scores[model_type]),
                        'std_f1_score': np.std(all_f1_scores[model_type]),
                        'models_count': len(all_accuracies[model_type])
                    }

            report_path = f"models/training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            self._print_training_summary(report)

        except Exception as e:
            self.logger.error(f"Error generating training report: {str(e)}")

    def _print_training_summary(self, report):
        print("\n" + "="*60)
        print("ML MODEL TRAINING SUMMARY")
        print("="*60)

        print(f"Training Date: {report['training_date']}")
        print(f"Total Symbols: {report['total_symbols']}")
        print(f"Total Models Trained: {len(report['models_trained'])}")

        for model_type, summary in report['summary'].items():
            print(f"\n{model_type} Models:")
            print(f"  Count: {summary['models_count']}")
            print(f"  Average Accuracy: {summary['avg_accuracy']:.4f} ± {summary['std_accuracy']:.4f}")
            print(f"  Average F1 Score: {summary['avg_f1_score']:.4f} ± {summary['std_f1_score']:.4f}")

        print(f"\n📊 INDIVIDUAL MODEL PERFORMANCE:")
        for model in report['models_trained']:
            print(f"  {model['symbol']} ({model['model_type']}): "
                  f"Acc={model['accuracy']:.3f}, F1={model['f1_score']:.3f}")

        print("\n" + "="*60)

    def retrain_model(self, symbol, model_type='LSTM'):
        self.logger.info(f"Retraining {model_type} model for {symbol}")

        stock_data = self.data_fetcher.fetch_stock_data(symbol)
        if stock_data is None:
            self.logger.error(f"Failed to fetch data for {symbol}")
            return None

        indicators_data = self.indicators.calculate_indicators(stock_data)
        if indicators_data is None:
            self.logger.error(f"Failed to calculate indicators for {symbol}")
            return None

        engineered_data = self.feature_engineer.engineer_features(indicators_data)
        if engineered_data is None:
            self.logger.error(f"Failed to engineer features for {symbol}")
            return None

        X, y, features = self.feature_engineer.prepare_sequences(engineered_data, symbol)
        if X is None or y is None:
            self.logger.error(f"Failed to prepare sequences for {symbol}")
            return None

        model, model_info = self.ml_models.train_model(X, y, symbol, model_type)

        if model is not None:
            self.logger.info(f"Successfully retrained {model_type} model for {symbol}")
            return model, model_info
        else:
            self.logger.error(f"Failed to retrain {model_type} model for {symbol}")
            return None

    def validate_models(self):
        self.logger.info("Validating trained models...")

        model_summary = self.ml_models.get_model_summary()

        validation_results = {}
        for model_key, model_info in model_summary.items():
            symbol, model_type = model_key.split('_', 1)

            model_path = model_info.get('model_path')
            if model_path and os.path.exists(model_path):
                validation_results[model_key] = {
                    'status': 'valid',
                    'accuracy': model_info.get('accuracy', 0),
                    'f1_score': model_info.get('f1_score', 0),
                    'trained_date': model_info.get('trained_date')
                }
            else:
                validation_results[model_key] = {
                    'status': 'missing',
                    'error': 'Model file not found'
                }

        print("\n" + "="*50)
        print("MODEL VALIDATION RESULTS")
        print("="*50)

        valid_models = 0
        missing_models = 0

        for model_key, result in validation_results.items():
            if result['status'] == 'valid':
                valid_models += 1
                print(f"✅ {model_key}: Acc={result['accuracy']:.3f}, F1={result['f1_score']:.3f}")
            else:
                missing_models += 1
                print(f"❌ {model_key}: {result['error']}")

        print(f"\nSummary: {valid_models} valid, {missing_models} missing")
        print("="*50)

        return validation_results

def main():
    print("🤖 NIFTY 50 ML Model Training")
    print("="*50)

    trainer = MLTrainer()

    trained_models = trainer.train_all_models()

    if trained_models:
        print("\n✅ ML model training completed successfully!")

        trainer.validate_models()
    else:
        print("\n❌ ML model training failed!")

if __name__ == "__main__":
    main()