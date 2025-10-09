import { TelegramConfig } from '@/types/config';
import { TradingSignal } from '@/types/trading';

export interface TelegramMessage {
    text: string;
    parse_mode?: 'HTML' | 'Markdown';
}

class TelegramService {
    private config: TelegramConfig | null = null;

    setConfig(config: TelegramConfig) {
        this.config = config;
    }

    async testConnection(): Promise<boolean> {
        if (!this.config?.botToken || !this.config?.chatId) {
            throw new Error('Bot token and chat ID are required');
        }

        try {
            const response = await fetch(`https://api.telegram.org/bot${this.config.botToken}/getMe`);
            const data = await response.json();

            if (data.ok) {
                // Test sending a message
                await this.sendMessage({
                    text: '🤖 Trading System Connected!\n\nTelegram notifications are now active.',
                });
                return true;
            }
            return false;
        } catch (error) {
            console.error('Telegram connection test failed:', error);
            return false;
        }
    }

    async sendMessage(message: TelegramMessage): Promise<boolean> {
        if (!this.config?.botToken || !this.config?.chatId) {
            console.warn('Telegram not configured');
            return false;
        }

        try {
            const response = await fetch(`https://api.telegram.org/bot${this.config.botToken}/sendMessage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chat_id: this.config.chatId,
                    text: message.text,
                    parse_mode: message.parse_mode || 'HTML',
                }),
            });

            const data = await response.json();
            return data.ok;
        } catch (error) {
            console.error('Failed to send Telegram message:', error);
            return false;
        }
    }

    async sendSignalNotification(signal: TradingSignal): Promise<boolean> {
        if (!this.config?.notifications.signals) return false;

        const emoji = signal.type === 'BUY' ? '🟢' : signal.type === 'SELL' ? '🔴' : '🟡';
        const message = {
            text: `${emoji} <b>Trading Signal</b>

📊 <b>Symbol:</b> ${signal.symbol}
📈 <b>Type:</b> ${signal.type}
💰 <b>Price:</b> ₹${signal.price.toFixed(2)}
🎯 <b>Confidence:</b> ${Math.round(signal.confidence * 100)}%
📝 <b>Reason:</b> ${signal.reasoning}

🕐 <b>Time:</b> ${signal.timestamp.toLocaleString()}`,
            parse_mode: 'HTML' as const,
        };

        return this.sendMessage(message);
    }

    async sendTradeNotification(trade: {
        symbol: string;
        type: 'BUY' | 'SELL';
        price: number;
        quantity: number;
        pnl?: number;
    }): Promise<boolean> {
        if (!this.config?.notifications.trades) return false;

        const emoji = trade.type === 'BUY' ? '✅' : '❌';
        const pnlText = trade.pnl !== undefined
            ? `\n💸 <b>P&L:</b> ${trade.pnl >= 0 ? '+' : ''}₹${trade.pnl.toFixed(2)}`
            : '';

        const message = {
            text: `${emoji} <b>Trade Executed</b>

📊 <b>Symbol:</b> ${trade.symbol}
📈 <b>Action:</b> ${trade.type}
💰 <b>Price:</b> ₹${trade.price.toFixed(2)}
📦 <b>Quantity:</b> ${trade.quantity}${pnlText}

🕐 <b>Time:</b> ${new Date().toLocaleString()}`,
            parse_mode: 'HTML' as const,
        };

        return this.sendMessage(message);
    }

    async sendErrorNotification(error: {
        type: string;
        message: string;
        details?: string;
    }): Promise<boolean> {
        if (!this.config?.notifications.errors) return false;

        const message = {
            text: `🚨 <b>System Error</b>

⚠️ <b>Type:</b> ${error.type}
📝 <b>Message:</b> ${error.message}
${error.details ? `\n🔍 <b>Details:</b> ${error.details}` : ''}

🕐 <b>Time:</b> ${new Date().toLocaleString()}`,
            parse_mode: 'HTML' as const,
        };

        return this.sendMessage(message);
    }

    async sendTrainingNotification(training: {
        symbol: string;
        modelType: string;
        status: 'STARTED' | 'COMPLETED' | 'FAILED';
        accuracy?: number;
        duration?: number;
    }): Promise<boolean> {
        if (!this.config?.notifications.training) return false;

        let emoji = '🧠';
        let statusText = training.status;

        if (training.status === 'COMPLETED') {
            emoji = '✅';
            statusText = 'COMPLETED';
        } else if (training.status === 'FAILED') {
            emoji = '❌';
            statusText = 'FAILED';
        } else if (training.status === 'STARTED') {
            emoji = '🚀';
            statusText = 'STARTED';
        }

        const accuracyText = training.accuracy
            ? `\n🎯 <b>Accuracy:</b> ${(training.accuracy * 100).toFixed(1)}%`
            : '';

        const durationText = training.duration
            ? `\n⏱️ <b>Duration:</b> ${Math.round(training.duration / 60)} minutes`
            : '';

        const message = {
            text: `${emoji} <b>Model Training ${statusText}</b>

📊 <b>Symbol:</b> ${training.symbol}
🤖 <b>Model:</b> ${training.modelType}${accuracyText}${durationText}

🕐 <b>Time:</b> ${new Date().toLocaleString()}`,
            parse_mode: 'HTML' as const,
        };

        return this.sendMessage(message);
    }

    async sendSystemNotification(system: {
        type: 'STARTED' | 'STOPPED' | 'RESTARTED' | 'WARNING';
        message: string;
    }): Promise<boolean> {
        let emoji = '🔧';

        switch (system.type) {
            case 'STARTED':
                emoji = '🟢';
                break;
            case 'STOPPED':
                emoji = '🔴';
                break;
            case 'RESTARTED':
                emoji = '🔄';
                break;
            case 'WARNING':
                emoji = '⚠️';
                break;
        }

        const message = {
            text: `${emoji} <b>System ${system.type}</b>

📝 ${system.message}

🕐 <b>Time:</b> ${new Date().toLocaleString()}`,
            parse_mode: 'HTML' as const,
        };

        return this.sendMessage(message);
    }
}

// Create singleton instance
const telegramService = new TelegramService();

export default telegramService;