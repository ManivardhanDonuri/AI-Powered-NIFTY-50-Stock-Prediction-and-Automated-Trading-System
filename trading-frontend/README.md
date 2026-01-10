# NIFTY 50 ML Trading System - Frontend

A modern, responsive React frontend for the NIFTY 50 ML Trading System built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

### 🎨 Modern UI/UX
- Beautiful landing page with smooth animations
- Dark/light theme support with seamless switching
- Responsive design optimized for all devices
- Professional trading interface design

### 📊 Live Trading Data
- Real-time stock price updates via WebSocket
- Interactive TradingView charts with multiple timeframes
- Live market status indicators
- Trading signals visualization with confidence levels

### 🤖 ML Model Management
- Complete model training interface with real-time progress
- Model performance metrics and comparison tools
- Training parameter configuration
- Model management (view, retrain, delete)

### 📈 Trading Analytics
- Comprehensive trading history with advanced filtering
- Signal tracking and analysis
- Data export in multiple formats (CSV, Excel, JSON)
- Portfolio performance tracking

### ⚙️ System Management
- Complete system configuration interface
- Real-time system monitoring and performance metrics
- Service status tracking
- System logs and error monitoring

### 🔔 Notifications
- Telegram bot integration for real-time alerts
- Configurable notification types
- System status notifications

### 📱 Progressive Web App (PWA)
- Installable on mobile devices
- Offline functionality for critical features
- Native app-like experience

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: TradingView Lightweight Charts
- **Animations**: Framer Motion
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Real-time**: Socket.IO
- **Theme**: next-themes
- **Icons**: Lucide React
- **UI Components**: Headless UI, Radix UI

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Python trading system backend (running on port 3001)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trading-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

4. Update the environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

5. Start the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard page
│   ├── train-model/       # Model training page
│   ├── history/           # Trading history page
│   ├── portfolio/         # Portfolio management page
│   ├── settings/          # System settings page
│   └── system/            # System control page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── charts/           # Chart components
│   ├── features/         # Feature-specific components
│   └── layout/           # Layout components
├── hooks/                # Custom React hooks
├── services/             # API and external services
├── stores/               # Zustand state stores
├── types/                # TypeScript type definitions
├── utils/                # Utility functions
└── styles/               # Global styles
```

## Key Components

### Landing Page
- Professional hero section with project branding
- Feature showcase with animations
- Smooth navigation to dashboard

### Dashboard
- Real-time portfolio statistics
- Live stock price charts
- Recent trading signals
- Stock selector with search functionality

### Model Training
- Training configuration interface
- Real-time progress monitoring
- Model performance metrics
- Existing model management

### Trading History
- Comprehensive signal history
- Advanced filtering and search
- Data export functionality
- Performance analytics

### Portfolio Management
- Holdings overview with P&L tracking
- Portfolio allocation visualization
- Recent trades history
- Performance metrics

### System Control
- Real-time system monitoring
- Performance metrics (CPU, memory, disk)
- Service status tracking
- System logs viewer

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:3001/api` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:3001` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `NIFTY 50 ML Trading System` |
| `NEXT_PUBLIC_ENABLE_TELEGRAM` | Enable Telegram integration | `true` |
| `NEXT_PUBLIC_ENABLE_PWA` | Enable PWA features | `true` |

### Telegram Integration

1. Create a Telegram bot via @BotFather
2. Get your chat ID by messaging @userinfobot
3. Configure in Settings > Telegram Notifications
4. Test the connection

### PWA Installation

The app can be installed as a PWA on supported devices:
1. Open the app in a supported browser
2. Look for the "Install" prompt or "Add to Home Screen" option
3. Follow the installation prompts

## API Integration

The frontend communicates with the Python trading system backend through:

- **REST API**: For CRUD operations and configuration
- **WebSocket**: For real-time data updates
- **File Upload**: For model imports and exports

### API Endpoints

- `GET /api/stocks` - Get stock list
- `GET /api/signals` - Get trading signals
- `GET /api/models` - Get ML models
- `POST /api/models/train` - Start model training
- `GET /api/portfolio` - Get portfolio data
- `GET /api/system/status` - Get system status

## Deployment

### Production Build

```bash
npm run build
npm run start
```

### Environment Setup

For production deployment:

1. Set `NODE_ENV=production`
2. Update API URLs to production endpoints
3. Configure proper CORS settings on the backend
4. Set up SSL certificates for HTTPS
5. Configure reverse proxy (nginx/Apache)

## Performance Optimization

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Use `npm run analyze`
- **Caching**: Static assets and API responses
- **Lazy Loading**: Components and charts loaded on demand

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information

---

Built with ❤️ using Next.js and TypeScript