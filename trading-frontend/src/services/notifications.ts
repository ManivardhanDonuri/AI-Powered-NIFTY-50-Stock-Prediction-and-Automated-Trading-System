import axios from 'axios';

export interface NotificationData {
  type: 'signal' | 'trade' | 'error' | 'training' | 'system';
  title: string;
  message: string;
  symbol?: string;
  price?: number;
  timestamp: Date;
  severity: 'info' | 'success' | 'warning' | 'error';
}

export interface TelegramMessage {
  symbol?: string;
  type: string;
  price?: number;
  change?: number;
  reasoning?: string;
  confidence?: number;
}

class NotificationService {
  private notifications: NotificationData[] = [];
  private listeners: ((notifications: NotificationData[]) => void)[] = [];
  private telegramConfig = {
    botToken: '',
    chatId: '',
    enabled: false,
  };

  // Configure Telegram
  configureTelegram(botToken: string, chatId: string) {
    this.telegramConfig = {
      botToken,
      chatId,
      enabled: !!(botToken && chatId),
    };
  }

  // Add notification
  addNotification(notification: NotificationData) {
    this.notifications.unshift({
      ...notification,
      timestamp: new Date(),
    });

    // Keep only last 100 notifications
    if (this.notifications.length > 100) {
      this.notifications = this.notifications.slice(0, 100);
    }

    this.notifyListeners();

    // Send to Telegram if configured
    if (this.telegramConfig.enabled) {
      this.sendTelegramNotification(notification);
    }
  }

  // Subscribe to notifications
  subscribe(listener: (notifications: NotificationData[]) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  // Get all notifications
  getNotifications() {
    return this.notifications;
  }

  // Clear notifications
  clearNotifications() {
    this.notifications = [];
    this.notifyListeners();
  }

  // Mark notification as read
  markAsRead(index: number) {
    if (this.notifications[index]) {
      this.notifications[index] = {
        ...this.notifications[index],
        // Add read status if needed
      };
      this.notifyListeners();
    }
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.notifications));
  }

  // Send Telegram notification
  private async sendTelegramNotification(notification: NotificationData) {
    if (!this.telegramConfig.enabled) return;

    try {
      const message = this.formatTelegramMessage(notification);
      const url = `https://api.telegram.org/bot${this.telegramConfig.botToken}/sendMessage`;
      
      await axios.post(url, {
        chat_id: this.telegramConfig.chatId,
        text: message,
        parse_mode: 'Markdown',
      });
    } catch (error) {
      console.error('Failed to send Telegram notification:', error);
    }
  }

  // Format message for Telegram
  private formatTelegramMessage(notification: NotificationData): string {
    const timestamp = notification.timestamp.toLocaleString();
    const emoji = this.getEmojiForType(notification.type, notification.severity);
    
    let message = `${emoji} *${notification.title}*\n\n${notification.message}`;
    
    if (notification.symbol) {
      message += `\n📊 Symbol: ${notification.symbol}`;
    }
    
    if (notification.price) {
      message += `\n💰 Price: ₹${notification.price.toFixed(2)}`;
    }
    
    message += `\n🕐 Time: ${timestamp}`;
    
    return message;
  }

  private getEmojiForType(type: string, severity: string): string {
    switch (type) {
      case 'signal':
        return severity === 'success' ? '🟢' : '🔴';
      case 'trade':
        return '💼';
      case 'error':
        return '❌';
      case 'training':
        return '🧠';
      case 'system':
        return '⚙️';
      default:
        return '📢';
    }
  }

  // Predefined notification methods
  signalGenerated(data: TelegramMessage) {
    this.addNotification({
      type: 'signal',
      title: `${data.type} Signal Generated`,
      message: `${data.type} signal for ${data.symbol} at ₹${data.price?.toFixed(2)}. Confidence: ${(data.confidence || 0 * 100).toFixed(1)}%`,
      symbol: data.symbol,
      price: data.price,
      timestamp: new Date(),
      severity: data.type === 'BUY' ? 'success' : 'warning',
    });
  }

  tradeExecuted(data: TelegramMessage) {
    this.addNotification({
      type: 'trade',
      title: 'Trade Executed',
      message: `${data.type} order executed for ${data.symbol} at ₹${data.price?.toFixed(2)}`,
      symbol: data.symbol,
      price: data.price,
      timestamp: new Date(),
      severity: 'success',
    });
  }

  systemError(message: string) {
    this.addNotification({
      type: 'error',
      title: 'System Error',
      message,
      timestamp: new Date(),
      severity: 'error',
    });
  }

  trainingComplete(model: string, accuracy: number) {
    this.addNotification({
      type: 'training',
      title: 'Model Training Complete',
      message: `${model} training completed with ${(accuracy * 100).toFixed(1)}% accuracy`,
      timestamp: new Date(),
      severity: 'success',
    });
  }

  systemStatus(status: string, message: string) {
    this.addNotification({
      type: 'system',
      title: `System ${status}`,
      message,
      timestamp: new Date(),
      severity: status === 'Online' ? 'success' : 'warning',
    });
  }

  // Test Telegram connection
  async testTelegramConnection(): Promise<boolean> {
    if (!this.telegramConfig.enabled) return false;

    try {
      const testMessage = '🧪 *Test Message*\n\nTelegram integration is working correctly!';
      const url = `https://api.telegram.org/bot${this.telegramConfig.botToken}/sendMessage`;
      
      await axios.post(url, {
        chat_id: this.telegramConfig.chatId,
        text: testMessage,
        parse_mode: 'Markdown',
      });
      
      return true;
    } catch (error) {
      console.error('Telegram test failed:', error);
      return false;
    }
  }
}

export const notificationService = new NotificationService();

// Simulate some notifications for demo
setTimeout(() => {
  notificationService.signalGenerated({
    type: 'BUY',
    symbol: 'NIFTY 50',
    price: 25046.15,
    confidence: 0.85,
    reasoning: 'RSI oversold + MA crossover'
  });
}, 2000);

setTimeout(() => {
  notificationService.tradeExecuted({
    type: 'BUY',
    symbol: 'RELIANCE',
    price: 2847.50,
  });
}, 5000);

setTimeout(() => {
  notificationService.trainingComplete('LSTM_NIFTY_v1', 0.847);
}, 8000);