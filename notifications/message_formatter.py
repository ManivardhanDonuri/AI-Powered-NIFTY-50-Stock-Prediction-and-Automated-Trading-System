"""
Message formatting for trading notifications

Creates platform-specific formatted messages for trading signals and portfolio updates.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import math

from .base_service import SignalNotificationData
from .logger import get_notification_logger

class MessageFormatter:
    """Formats trading messages for different notification platforms."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize message formatter."""
        self.config = config or {}
        self.logger = get_notification_logger('formatter')
        
        # Platform-specific message limits
        self.platform_limits = {
            'telegram': 4096,  # Telegram message limit
            'whatsapp': 1024   # WhatsApp practical limit
        }
        
        # Emoji mappings
        self.signal_emojis = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }
        
        self.confidence_emojis = {
            0.9: '⭐⭐⭐⭐⭐',
            0.8: '⭐⭐⭐⭐',
            0.7: '⭐⭐⭐',
            0.6: '⭐⭐',
            0.5: '⭐'
        }
    
    def format_signal_message(
        self, 
        signal_data: SignalNotificationData, 
        platform: str = 'telegram'
    ) -> str:
        """
        Format a trading signal message for the specified platform.
        
        Args:
            signal_data: Signal notification data
            platform: Target platform ('telegram' or 'whatsapp')
            
        Returns:
            str: Formatted message
        """
        try:
            if platform == 'telegram':
                return self._format_signal_telegram(signal_data)
            elif platform == 'whatsapp':
                return self._format_signal_whatsapp(signal_data)
            else:
                return self._format_signal_plain(signal_data)
                
        except Exception as e:
            self.logger.error(f"Error formatting signal message: {str(e)}")
            return self._format_signal_plain(signal_data)
    
    def _format_signal_telegram(self, signal_data: SignalNotificationData) -> str:
        """Format signal message for Telegram with HTML formatting."""
        emoji = self.signal_emojis.get(signal_data.signal_type, '📊')
        confidence_stars = self._get_confidence_stars(signal_data.confidence)
        
        # Format timestamp
        time_str = signal_data.timestamp.strftime('%H:%M:%S')
        date_str = signal_data.timestamp.strftime('%d/%m/%Y')
        
        # Calculate suggested levels
        stop_loss, target = self._calculate_levels(signal_data.price, signal_data.signal_type)
        
        message = f"""
{emoji} <b>{signal_data.signal_type} SIGNAL</b>

📈 <b>Stock:</b> {signal_data.symbol}
💰 <b>Price:</b> ₹{signal_data.price:.2f}
🎯 <b>Confidence:</b> {confidence_stars} ({signal_data.confidence:.1%})
🤖 <b>ML Probability:</b> {signal_data.ml_probability:.1%}

📊 <b>Suggested Levels:</b>
• Target: ₹{target:.2f}
• Stop Loss: ₹{stop_loss:.2f}

💡 <b>Reason:</b> {signal_data.reason}

🕐 <b>Time:</b> {time_str} | {date_str}
        """.strip()
        
        # Add model predictions if available
        if signal_data.model_predictions:
            predictions_text = "\n\n🔬 <b>Model Predictions:</b>\n"
            for model, prediction in signal_data.model_predictions.items():
                predictions_text += f"• {model}: {prediction:.1%}\n"
            message += predictions_text
        
        return message
    
    def _format_signal_whatsapp(self, signal_data: SignalNotificationData) -> str:
        """Format signal message for WhatsApp with simple formatting."""
        emoji = self.signal_emojis.get(signal_data.signal_type, '📊')
        confidence_stars = self._get_confidence_stars(signal_data.confidence)
        
        # Format timestamp
        time_str = signal_data.timestamp.strftime('%H:%M')
        
        # Calculate suggested levels
        stop_loss, target = self._calculate_levels(signal_data.price, signal_data.signal_type)
        
        message = f"""
{emoji} *{signal_data.signal_type} SIGNAL*

📈 *Stock:* {signal_data.symbol}
💰 *Price:* ₹{signal_data.price:.2f}
🎯 *Confidence:* {confidence_stars}
🤖 *ML Prob:* {signal_data.ml_probability:.1%}

📊 *Levels:*
Target: ₹{target:.2f}
Stop: ₹{stop_loss:.2f}

💡 {signal_data.reason}

🕐 {time_str}
        """.strip()
        
        return message
    
    def _format_signal_plain(self, signal_data: SignalNotificationData) -> str:
        """Format signal message in plain text."""
        confidence_pct = signal_data.confidence * 100
        ml_pct = signal_data.ml_probability * 100
        time_str = signal_data.timestamp.strftime('%H:%M:%S')
        
        return (
            f"{signal_data.signal_type} SIGNAL: {signal_data.symbol} "
            f"at ₹{signal_data.price:.2f} "
            f"(Confidence: {confidence_pct:.1f}%, ML: {ml_pct:.1f}%) "
            f"- {signal_data.reason} [{time_str}]"
        )
    
    def format_portfolio_summary(
        self, 
        portfolio_data: Dict[str, Any], 
        platform: str = 'telegram'
    ) -> str:
        """
        Format portfolio summary message.
        
        Args:
            portfolio_data: Portfolio performance data
            platform: Target platform
            
        Returns:
            str: Formatted portfolio summary
        """
        try:
            if platform == 'telegram':
                return self._format_portfolio_telegram(portfolio_data)
            elif platform == 'whatsapp':
                return self._format_portfolio_whatsapp(portfolio_data)
            else:
                return self._format_portfolio_plain(portfolio_data)
                
        except Exception as e:
            self.logger.error(f"Error formatting portfolio summary: {str(e)}")
            return "Portfolio summary unavailable"
    
    def _format_portfolio_telegram(self, portfolio_data: Dict[str, Any]) -> str:
        """Format portfolio summary for Telegram."""
        total_pnl = portfolio_data.get('total_pnl', 0)
        win_rate = portfolio_data.get('win_rate', 0)
        total_trades = portfolio_data.get('total_trades', 0)
        sharpe_ratio = portfolio_data.get('sharpe_ratio', 0)
        
        # Determine overall performance emoji
        if total_pnl > 0:
            performance_emoji = '📈'
            pnl_color = '🟢'
        elif total_pnl < 0:
            performance_emoji = '📉'
            pnl_color = '🔴'
        else:
            performance_emoji = '➡️'
            pnl_color = '🟡'
        
        message = f"""
{performance_emoji} <b>PORTFOLIO SUMMARY</b>

💰 <b>Total P&L:</b> {pnl_color} ₹{total_pnl:.2f}
📊 <b>Win Rate:</b> {win_rate:.1f}%
🔢 <b>Total Trades:</b> {total_trades}
📈 <b>Sharpe Ratio:</b> {sharpe_ratio:.2f}

📅 <b>Generated:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
        
        # Add individual stock performance if available
        if 'symbols_traded' in portfolio_data:
            message += "\n\n📋 <b>Active Stocks:</b>\n"
            for symbol in portfolio_data['symbols_traded'][:5]:  # Limit to 5 stocks
                message += f"• {symbol}\n"
        
        return message
    
    def _format_portfolio_whatsapp(self, portfolio_data: Dict[str, Any]) -> str:
        """Format portfolio summary for WhatsApp."""
        total_pnl = portfolio_data.get('total_pnl', 0)
        win_rate = portfolio_data.get('win_rate', 0)
        total_trades = portfolio_data.get('total_trades', 0)
        
        # Determine performance emoji
        if total_pnl > 0:
            performance_emoji = '📈'
        elif total_pnl < 0:
            performance_emoji = '📉'
        else:
            performance_emoji = '➡️'
        
        message = f"""
{performance_emoji} *PORTFOLIO SUMMARY*

💰 *P&L:* ₹{total_pnl:.2f}
📊 *Win Rate:* {win_rate:.1f}%
🔢 *Trades:* {total_trades}

📅 {datetime.now().strftime('%d/%m %H:%M')}
        """.strip()
        
        return message
    
    def _format_portfolio_plain(self, portfolio_data: Dict[str, Any]) -> str:
        """Format portfolio summary in plain text."""
        total_pnl = portfolio_data.get('total_pnl', 0)
        win_rate = portfolio_data.get('win_rate', 0)
        total_trades = portfolio_data.get('total_trades', 0)
        
        return (
            f"Portfolio Summary: P&L ₹{total_pnl:.2f}, "
            f"Win Rate {win_rate:.1f}%, "
            f"Trades {total_trades}"
        )
    
    def format_alert_message(
        self, 
        alert_type: str, 
        message: str, 
        platform: str = 'telegram'
    ) -> str:
        """
        Format system alert message.
        
        Args:
            alert_type: Type of alert ('error', 'warning', 'info')
            message: Alert message
            platform: Target platform
            
        Returns:
            str: Formatted alert message
        """
        alert_emojis = {
            'error': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        emoji = alert_emojis.get(alert_type, '📢')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if platform == 'telegram':
            return f"{emoji} <b>{alert_type.upper()}</b>\n\n{message}\n\n🕐 {timestamp}"
        elif platform == 'whatsapp':
            return f"{emoji} *{alert_type.upper()}*\n\n{message}\n\n🕐 {timestamp}"
        else:
            return f"{alert_type.upper()}: {message} [{timestamp}]"
    
    def truncate_message(self, message: str, platform: str) -> str:
        """
        Truncate message to platform limits.
        
        Args:
            message: Message to truncate
            platform: Target platform
            
        Returns:
            str: Truncated message
        """
        limit = self.platform_limits.get(platform, 1000)
        
        if len(message) <= limit:
            return message
        
        # Truncate with ellipsis, preserving important information
        truncated = message[:limit - 20]  # Leave space for truncation notice
        
        # Try to truncate at a line break
        last_newline = truncated.rfind('\n')
        if last_newline > limit * 0.7:  # If we can save at least 30% of content
            truncated = truncated[:last_newline]
        
        truncated += "\n\n... (message truncated)"
        
        return truncated
    
    def _get_confidence_stars(self, confidence: float) -> str:
        """Get star rating for confidence level."""
        for threshold in sorted(self.confidence_emojis.keys(), reverse=True):
            if confidence >= threshold:
                return self.confidence_emojis[threshold]
        return '⭐'
    
    def _calculate_levels(self, price: float, signal_type: str) -> tuple:
        """
        Calculate suggested target and stop-loss levels.
        
        Args:
            price: Current price
            signal_type: BUY or SELL
            
        Returns:
            tuple: (stop_loss, target) prices
        """
        if signal_type == 'BUY':
            # For buy signals: target 3% up, stop loss 2% down
            target = price * 1.03
            stop_loss = price * 0.98
        else:  # SELL
            # For sell signals: target 3% down, stop loss 2% up
            target = price * 0.97
            stop_loss = price * 1.02
        
        return stop_loss, target
    
    def add_visual_indicators(self, signal_type: str, confidence: float) -> str:
        """
        Add visual indicators for signal strength.
        
        Args:
            signal_type: Signal type
            confidence: Confidence level
            
        Returns:
            str: Visual indicator string
        """
        emoji = self.signal_emojis.get(signal_type, '📊')
        stars = self._get_confidence_stars(confidence)
        
        return f"{emoji} {stars}"