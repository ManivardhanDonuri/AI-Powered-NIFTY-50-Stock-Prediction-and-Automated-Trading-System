import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from datetime import datetime
import json
from visualizer import Visualizer

class MLVisualizer(Visualizer):
    def __init__(self, config_file='config.json'):
        """Initialize ML-enhanced visualizer."""
        super().__init__(config_file)
        
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.ml_config = self.config.get('ml', {})
    
    def plot_ml_predictions(self, symbol, data, predictions, save_path=None):
        """Plot ML model predictions over time."""
        try:
            if not predictions:
                self.logger.warning("No ML predictions to plot")
                return
            
            fig, axes = plt.subplots(3, 1, figsize=(15, 12), height_ratios=[2, 1, 1])
            
            # Plot 1: Price with ML predictions
            axes[0].plot(data.index, data['Close'], label='Close Price', linewidth=2, color='black')
            axes[0].plot(data.index, data['SMA_20'], label='20-DMA', linewidth=1.5, color='blue', alpha=0.7)
            axes[0].plot(data.index, data['SMA_50'], label='50-DMA', linewidth=1.5, color='red', alpha=0.7)
            
            # Add prediction confidence bands
            if 'prediction_dates' in predictions and 'probabilities' in predictions:
                pred_dates = predictions['prediction_dates']
                probabilities = predictions['probabilities']
                
                # Create confidence bands
                upper_band = [p + 0.1 if p > 0.5 else p for p in probabilities]
                lower_band = [p - 0.1 if p > 0.5 else p for p in probabilities]
                
                # Normalize to price scale for visualization
                price_range = data['Close'].max() - data['Close'].min()
                price_min = data['Close'].min()
                
                upper_prices = [price_min + (p * price_range) for p in upper_band]
                lower_prices = [price_min + (p * price_range) for p in lower_band]
                
                axes[0].fill_between(pred_dates, lower_prices, upper_prices, 
                                   alpha=0.3, color='green', label='ML Confidence Band')
            
            axes[0].set_title(f'{symbol} - Price Chart with ML Predictions', fontsize=14, fontweight='bold')
            axes[0].set_ylabel('Price (₹)', fontsize=12)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # Plot 2: ML Probabilities
            if 'prediction_dates' in predictions and 'probabilities' in predictions:
                pred_dates = predictions['prediction_dates']
                probabilities = predictions['probabilities']
                
                axes[1].plot(pred_dates, probabilities, label='ML Probability', 
                           linewidth=2, color='purple')
                axes[1].axhline(y=0.5, color='black', linestyle='--', alpha=0.7, label='Neutral (0.5)')
                axes[1].axhline(y=0.7, color='green', linestyle='--', alpha=0.7, label='Buy Threshold')
                axes[1].axhline(y=0.3, color='red', linestyle='--', alpha=0.7, label='Sell Threshold')
                
                axes[1].fill_between(pred_dates, 0.7, 1.0, alpha=0.3, color='green')
                axes[1].fill_between(pred_dates, 0.0, 0.3, alpha=0.3, color='red')
                
                axes[1].set_title('ML Model Predictions', fontsize=12, fontweight='bold')
                axes[1].set_ylabel('Probability', fontsize=12)
                axes[1].legend()
                axes[1].grid(True, alpha=0.3)
                axes[1].set_ylim(0, 1)
            
            # Plot 3: Model Comparison
            if 'model_predictions' in predictions:
                model_preds = predictions['model_predictions']
                
                for model_name, model_probs in model_preds.items():
                    if len(model_probs) == len(pred_dates):
                        axes[2].plot(pred_dates, model_probs, label=f'{model_name}', 
                                   linewidth=1.5, alpha=0.8)
                
                axes[2].axhline(y=0.5, color='black', linestyle='--', alpha=0.7)
                axes[2].set_title('Individual Model Predictions', fontsize=12, fontweight='bold')
                axes[2].set_ylabel('Probability', fontsize=12)
                axes[2].set_xlabel('Date', fontsize=12)
                axes[2].legend()
                axes[2].grid(True, alpha=0.3)
                axes[2].set_ylim(0, 1)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"ML predictions chart saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error plotting ML predictions: {str(e)}")
    
    def plot_model_performance_comparison(self, model_results, save_path=None):
        """Plot comparison of different model performances."""
        try:
            if not model_results:
                self.logger.warning("No model results to plot")
                return
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Extract data
            symbols = []
            lstm_acc = []
            gru_acc = []
            lstm_f1 = []
            gru_f1 = []
            
            for symbol, models in model_results.items():
                symbols.append(symbol)
                
                lstm_info = models.get('LSTM', {}).get('info', {})
                gru_info = models.get('GRU', {}).get('info', {})
                
                lstm_acc.append(lstm_info.get('accuracy', 0))
                gru_acc.append(gru_info.get('accuracy', 0))
                lstm_f1.append(lstm_info.get('f1_score', 0))
                gru_f1.append(gru_info.get('f1_score', 0))
            
            x = np.arange(len(symbols))
            width = 0.35
            
            # Plot 1: Accuracy Comparison
            ax1.bar(x - width/2, lstm_acc, width, label='LSTM', alpha=0.8, color='blue')
            ax1.bar(x + width/2, gru_acc, width, label='GRU', alpha=0.8, color='orange')
            ax1.set_title('Model Accuracy Comparison', fontweight='bold')
            ax1.set_ylabel('Accuracy')
            ax1.set_xticks(x)
            ax1.set_xticklabels(symbols, rotation=45)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: F1 Score Comparison
            ax2.bar(x - width/2, lstm_f1, width, label='LSTM', alpha=0.8, color='blue')
            ax2.bar(x + width/2, gru_f1, width, label='GRU', alpha=0.8, color='orange')
            ax2.set_title('Model F1 Score Comparison', fontweight='bold')
            ax2.set_ylabel('F1 Score')
            ax2.set_xticks(x)
            ax2.set_xticklabels(symbols, rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Average Performance
            avg_lstm_acc = np.mean(lstm_acc) if lstm_acc else 0
            avg_gru_acc = np.mean(gru_acc) if gru_acc else 0
            avg_lstm_f1 = np.mean(lstm_f1) if lstm_f1 else 0
            avg_gru_f1 = np.mean(gru_f1) if gru_f1 else 0
            
            models = ['LSTM', 'GRU']
            avg_acc = [avg_lstm_acc, avg_gru_acc]
            avg_f1 = [avg_lstm_f1, avg_gru_f1]
            
            ax3.bar(models, avg_acc, alpha=0.8, color=['blue', 'orange'])
            ax3.set_title('Average Accuracy', fontweight='bold')
            ax3.set_ylabel('Average Accuracy')
            ax3.grid(True, alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(avg_acc):
                ax3.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
            
            # Plot 4: Average F1 Score
            ax4.bar(models, avg_f1, alpha=0.8, color=['blue', 'orange'])
            ax4.set_title('Average F1 Score', fontweight='bold')
            ax4.set_ylabel('Average F1 Score')
            ax4.grid(True, alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(avg_f1):
                ax4.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Model performance comparison saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error plotting model performance comparison: {str(e)}")
    
    def create_interactive_ml_dashboard(self, symbol, data, predictions, signals):
        """Create interactive dashboard with ML predictions."""
        try:
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxis=True,
                vertical_spacing=0.08,
                subplot_titles=(
                    f'{symbol} - Price & Signals',
                    'ML Model Predictions',
                    'RSI Indicator'
                ),
                row_heights=[0.5, 0.3, 0.2]
            )
            
            # Price chart
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Close Price',
                          line=dict(color='black', width=2)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20',
                          line=dict(color='blue', width=1.5)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50',
                          line=dict(color='red', width=1.5)),
                row=1, col=1
            )
            
            # Add signals
            if signals:
                buy_signals = [s for s in signals if s['type'] == 'BUY']
                sell_signals = [s for s in signals if s['type'] == 'SELL']
                
                if buy_signals:
                    buy_dates = [datetime.strptime(s['date'], '%Y-%m-%d') for s in buy_signals]
                    buy_prices = [s['price'] for s in buy_signals]
                    fig.add_trace(
                        go.Scatter(x=buy_dates, y=buy_prices, mode='markers',
                                  name='Buy Signal', 
                                  marker=dict(color='green', size=10, symbol='triangle-up')),
                        row=1, col=1
                    )
                
                if sell_signals:
                    sell_dates = [datetime.strptime(s['date'], '%Y-%m-%d') for s in sell_signals]
                    sell_prices = [s['price'] for s in sell_signals]
                    fig.add_trace(
                        go.Scatter(x=sell_dates, y=sell_prices, mode='markers',
                                  name='Sell Signal',
                                  marker=dict(color='red', size=10, symbol='triangle-down')),
                        row=1, col=1
                    )
            
            # ML Predictions
            if predictions and 'probabilities' in predictions:
                pred_dates = predictions['prediction_dates']
                probabilities = predictions['probabilities']
                
                fig.add_trace(
                    go.Scatter(x=pred_dates, y=probabilities, name='ML Probability',
                              line=dict(color='purple', width=2)),
                    row=2, col=1
                )
                
                # Add threshold lines
                fig.add_hline(y=0.5, line_dash="dash", line_color="black", opacity=0.7, row=2, col=1)
                fig.add_hline(y=0.7, line_dash="dash", line_color="green", opacity=0.7, row=2, col=1)
                fig.add_hline(y=0.3, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
                
                # Fill zones
                fig.add_hrect(y0=0.7, y1=1.0, fillcolor="green", opacity=0.2, row=2, col=1)
                fig.add_hrect(y0=0.0, y1=0.3, fillcolor="red", opacity=0.2, row=2, col=1)
            
            # RSI
            fig.add_trace(
                go.Scatter(x=data.index, y=data['RSI'], name='RSI',
                          line=dict(color='orange', width=2)),
                row=3, col=1
            )
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7, row=3, col=1)
            
            # Update layout
            fig.update_layout(
                title=f"ML-Enhanced Trading Analysis - {symbol}",
                height=800,
                showlegend=True,
                hovermode='x unified'
            )
            
            fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
            fig.update_yaxes(title_text="Probability", row=2, col=1, range=[0, 1])
            fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
            fig.update_xaxes(title_text="Date", row=3, col=1)
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating interactive ML dashboard: {str(e)}")
            return None
    
    def plot_signal_mode_comparison(self, backtest_results, save_path=None):
        """Compare performance across different signal modes."""
        try:
            if not backtest_results:
                self.logger.warning("No backtest results to compare")
                return
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Assuming backtest_results contains results for different modes
            modes = list(backtest_results.keys())
            
            # Extract metrics for each mode
            total_pnl = []
            win_rates = []
            sharpe_ratios = []
            total_trades = []
            
            for mode in modes:
                mode_results = backtest_results[mode]
                
                # Aggregate across all symbols
                total_pnl.append(sum(r['total_pnl'] for r in mode_results.values()))
                win_rates.append(np.mean([r['win_rate'] for r in mode_results.values()]))
                sharpe_ratios.append(np.mean([r['sharpe_ratio'] for r in mode_results.values()]))
                total_trades.append(sum(r['total_trades'] for r in mode_results.values()))
            
            # Plot comparisons
            colors = ['blue', 'green', 'orange']
            
            # Total P&L
            bars1 = ax1.bar(modes, total_pnl, color=colors[:len(modes)], alpha=0.7)
            ax1.set_title('Total P&L by Signal Mode', fontweight='bold')
            ax1.set_ylabel('Total P&L (₹)')
            
            for bar, pnl in zip(bars1, total_pnl):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{pnl:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
            
            # Win Rate
            bars2 = ax2.bar(modes, win_rates, color=colors[:len(modes)], alpha=0.7)
            ax2.set_title('Average Win Rate by Signal Mode', fontweight='bold')
            ax2.set_ylabel('Win Rate (%)')
            ax2.set_ylim(0, 100)
            
            for bar, rate in zip(bars2, win_rates):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{rate:.1f}%', ha='center', va='bottom')
            
            # Sharpe Ratio
            bars3 = ax3.bar(modes, sharpe_ratios, color=colors[:len(modes)], alpha=0.7)
            ax3.set_title('Average Sharpe Ratio by Signal Mode', fontweight='bold')
            ax3.set_ylabel('Sharpe Ratio')
            
            for bar, ratio in zip(bars3, sharpe_ratios):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{ratio:.2f}', ha='center', va='bottom')
            
            # Total Trades
            bars4 = ax4.bar(modes, total_trades, color=colors[:len(modes)], alpha=0.7)
            ax4.set_title('Total Trades by Signal Mode', fontweight='bold')
            ax4.set_ylabel('Number of Trades')
            
            for bar, trades in zip(bars4, total_trades):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{trades}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Signal mode comparison saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error plotting signal mode comparison: {str(e)}")

if __name__ == "__main__":
    # Test the ML visualizer
    import yfinance as yf
    from datetime import datetime, timedelta
    from technical_indicators import TechnicalIndicators
    
    # Get sample data
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=365), end=datetime.now())
    
    # Calculate indicators
    indicators = TechnicalIndicators()
    indicators_data = indicators.calculate_indicators(data)
    
    # Create sample predictions
    sample_predictions = {
        'prediction_dates': indicators_data.index[-100:],
        'probabilities': np.random.random(100),
        'model_predictions': {
            'LSTM': np.random.random(100),
            'GRU': np.random.random(100)
        }
    }
    
    # Test visualization
    ml_visualizer = MLVisualizer()
    ml_visualizer.plot_ml_predictions("RELIANCE.NS", indicators_data, sample_predictions)