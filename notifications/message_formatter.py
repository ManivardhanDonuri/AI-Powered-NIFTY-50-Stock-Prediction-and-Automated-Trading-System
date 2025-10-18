
from typing import Dict, Any, Optional
from datetime import datetime
import math

from .base_service import SignalNotificationData
from .logger import get_notification_logger

class MessageFormatter:

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_notification_logger('formatter')

        self.platform_limits = {
            'telegram': 4096,
            'whatsapp': 1024
        }

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
        emoji = self.signal_emojis.get(signal_data.signal_type, '📊')

        # Simple message format with only essential information
        message = f"{emoji} <b>{signal_data.signal_type}</b>\n\n"
        message += f"📈 <b>{signal_data.symbol}</b>\n"
        message += f"💰 <b>₹{signal_data.price:.2f}</b>\n"
        message += f"📝 {signal_data.reason}"

        return message

    def _format_signal_whatsapp(self, signal_data: SignalNotificationData) -> str:
        emoji = self.signal_emojis.get(signal_data.signal_type, '📊')

        # Simple message format with only essential information
        message = f"{emoji} *{signal_data.signal_type}*\n\n"
        message += f"📈 *{signal_data.symbol}*\n"
        message += f"💰 *₹{signal_data.price:.2f}*\n"
        message += f"📝 {signal_data.reason}"

        return message

    def _format_signal_plain(self, signal_data: SignalNotificationData) -> str:
        return (
            f"{signal_data.signal_type}: {signal_data.symbol} "
            f"at ₹{signal_data.price:.2f} - {signal_data.reason}"
        )

    def format_portfolio_summary(
        self,
        portfolio_data: Dict[str, Any],
        platform: str = 'telegram'
    ) -> str:

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
        total_pnl = portfolio_data.get('total_pnl', 0)
        win_rate = portfolio_data.get('win_rate', 0)
        total_trades = portfolio_data.get('total_trades', 0)
        sharpe_ratio = portfolio_data.get('sharpe_ratio', 0)

        if total_pnl > 0:
            performance_emoji = '📈'
            pnl_color = '🟢'
        elif total_pnl < 0:
            performance_emoji = '📉'
            pnl_color = '🔴'
        else:
            performance_emoji = '➡️'
            pnl_color = '🟡'

        message = f"{performance_emoji} <b>Portfolio Summary</b>\n\n"
        message += f"{pnl_color} <b>Total P&L:</b> ₹{total_pnl:.2f}\n"
        message += f"📊 <b>Win Rate:</b> {win_rate:.1f}%\n"
        message += f"🔢 <b>Total Trades:</b> {total_trades}\n"
        message += f"📈 <b>Sharpe Ratio:</b> {sharpe_ratio:.2f}\n"

        if 'symbols_traded' in portfolio_data:
            message += "\n\n📋 <b>Active Stocks:</b>\n"
            for symbol in portfolio_data['symbols_traded'][:5]:
                message += f"• {symbol}\n"

        return message

    def _format_portfolio_whatsapp(self, portfolio_data: Dict[str, Any]) -> str:
        total_pnl = portfolio_data.get('total_pnl', 0)
        win_rate = portfolio_data.get('win_rate', 0)
        total_trades = portfolio_data.get('total_trades', 0)

        if total_pnl > 0:
            performance_emoji = '📈'
        elif total_pnl < 0:
            performance_emoji = '📉'
        else:
            performance_emoji = '➡️'

        message = f"{performance_emoji} *Portfolio Summary*\n\n"
        message += f"💰 *Total P&L:* ₹{total_pnl:.2f}\n"
        message += f"📊 *Win Rate:* {win_rate:.1f}%\n"
        message += f"🔢 *Total Trades:* {total_trades}\n"

        return message

    def _format_portfolio_plain(self, portfolio_data: Dict[str, Any]) -> str:
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

        limit = self.platform_limits.get(platform, 1000)

        if len(message) <= limit:
            return message

        truncated = message[:limit - 20]

        last_newline = truncated.rfind('\n')
        if last_newline > limit * 0.7:
            truncated = truncated[:last_newline]

        truncated += "\n\n... (message truncated)"

        return truncated

    def _get_confidence_stars(self, confidence: float) -> str:
        for threshold in sorted(self.confidence_emojis.keys(), reverse=True):
            if confidence >= threshold:
                return self.confidence_emojis[threshold]
        return '⭐'

    def _calculate_levels(self, price: float, signal_type: str) -> tuple:

        if signal_type == 'BUY':
            target = price * 1.03
            stop_loss = price * 0.98
        else:
            target = price * 0.97
            stop_loss = price * 1.02

        return stop_loss, target

    def add_visual_indicators(self, signal_type: str, confidence: float) -> str:

        emoji = self.signal_emojis.get(signal_type, '📊')
        stars = self._get_confidence_stars(confidence)

        return f"{emoji} {stars}"