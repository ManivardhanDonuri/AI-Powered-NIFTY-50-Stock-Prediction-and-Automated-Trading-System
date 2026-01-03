
import sys
from trading_system import TradingSystem


def main():
    print("🤖 NIFTY 50 ML-Enhanced Trading System")
    print("="*50)

    trading_system = TradingSystem()

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == 'daily':
            print("Running daily monitoring...")
            success = trading_system.run_daily_monitoring()
        elif mode == 'analysis':
            print("Running complete analysis...")
            success = trading_system.run_complete_analysis()
        elif mode == 'train':
            print("Training ML models...")
            success = trading_system.train_ml_models()
        elif mode == 'dashboard':
            print("Launching dashboard...")
            success = trading_system.run_dashboard()
        elif mode == 'test-notifications':
            print("Testing notifications...")
            success = trading_system.test_notifications()
        else:
            print("Invalid mode. Use 'daily', 'analysis', 'train', 'dashboard', or 'test-notifications'")
            return
    else:
        print("Running complete analysis...")
        success = trading_system.run_complete_analysis()

    if success:
        print("\n✅ Trading system completed successfully!")
    else:
        print("\n❌ Trading system encountered errors. Check logs for details.")

if __name__ == "__main__":
    main()