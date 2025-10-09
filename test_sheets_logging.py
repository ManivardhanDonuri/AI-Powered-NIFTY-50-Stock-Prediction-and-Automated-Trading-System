"""
Test Google Sheets logging functionality
"""

from ml_signal_generator_enhanced import EnhancedMLSignalGenerator
from datetime import datetime
import json

def test_sheets_logging():
    """Test logging signals to Google Sheets."""
    print("🧪 Testing Google Sheets logging...")
    
    try:
        # Initialize enhanced signal generator
        generator = EnhancedMLSignalGenerator()
        
        # Create sample signals for testing
        test_signals = {
            'RELIANCE.NS': [
                {
                    'type': 'BUY',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'price': 2450.50,
                    'confidence': 0.85,
                    'ml_probability': 0.78,
                    'reason': 'Test signal - RSI oversold and SMA crossover bullish',
                    'rsi': 28.5,
                    'sma_20': 2440.0,
                    'sma_50': 2420.0
                }
            ],
            'TCS.NS': [
                {
                    'type': 'SELL',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'price': 3850.75,
                    'confidence': 0.72,
                    'ml_probability': 0.25,
                    'reason': 'Test signal - RSI overbought and bearish divergence',
                    'rsi': 75.2,
                    'sma_20': 3860.0,
                    'sma_50': 3870.0
                }
            ]
        }
        
        # Test logging signals to sheets
        if generator.sheets_logging_enabled:
            generator._log_signals_to_sheets(test_signals)
            print("✅ Successfully logged test signals to Google Sheets!")
            
            # Also test current signals logging
            current_signals = {
                'HDFCBANK.NS': {
                    'type': 'BUY',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'price': 1650.25,
                    'confidence': 0.90,
                    'ml_probability': 0.82,
                    'reason': 'Test current signal - Strong bullish momentum',
                    'rsi': 45.0
                }
            }
            
            generator._log_current_signals_to_sheets(current_signals)
            print("✅ Successfully logged test current signals to Google Sheets!")
            
        else:
            print("⚠️ Google Sheets logging is not enabled")
        
        # Test notifications
        if generator.notifications_enabled:
            generator.notification_manager.send_alert(
                'success',
                '🧪 Google Sheets logging test completed successfully!',
                'normal'
            )
            print("✅ Test notification sent!")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_sheets_logging()