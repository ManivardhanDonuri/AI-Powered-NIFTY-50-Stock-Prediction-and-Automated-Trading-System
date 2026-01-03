'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, TrendingUp, AlertTriangle, BarChart3, PieChart } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    confidence?: number;
    cached?: boolean;
    responseTime?: number;
    action?: string;
    symbol?: string;
  };
}

interface AITradingChatInterfaceProps {
  conversationId?: string;
  contextType?: string;
  onNewConversation?: (id: string) => void;
}

export default function AITradingChatInterface({
  conversationId,
  contextType = 'trading',
}: AITradingChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: `Hello! I'm your AI Trading Assistant specializing in Indian stock market analysis.

💎 **I provide recommendations for these top 3 Indian stocks:**
• **TCS (TCS.NS)** - IT Services Leader
• **HDFC Bank (HDFCBANK.NS)** - Leading Private Bank  
• **Reliance (RELIANCE.NS)** - Diversified Conglomerate

🎯 **Ask me anything about these stocks:**
• "Which stock should I buy?" - Get recommendations
• "TCS prediction" - Price forecasts
• "Compare TCS vs HDFC" - Side-by-side analysis
• "Risk analysis for Reliance" - Risk assessment

What would you like to know about these 3 stocks today?`,
      type: 'assistant',
      timestamp: new Date(),
      metadata: { confidence: 95 }
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const currentConversationId = conversationId || '';
  const inputRef = useRef<HTMLInputElement>(null);

  // Stock data for the 3 main project stocks
  const stockDatabase = [
    { symbol: 'TCS.NS', name: 'TCS', price: 4150, sector: 'IT Services', trend: 'bullish' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', price: 1678, sector: 'Banking', trend: 'bullish' },
    { symbol: 'RELIANCE.NS', name: 'Reliance', price: 2890, sector: 'Energy/Retail', trend: 'neutral' }
  ];

  const actions = ['BUY', 'SELL', 'HOLD', 'STRONG BUY', 'STRONG SELL'];
  const confidenceLevels = [65, 70, 75, 78, 80, 82, 85, 88, 90, 92, 95];
  
  const reasons = [
    'Strong quarterly earnings growth and positive market sentiment',
    'Technical indicators showing bullish momentum with good volume',
    'Sector rotation favoring this stock with institutional buying',
    'Recent product launches driving revenue growth expectations',
    'Improved profit margins and cost optimization initiatives',
    'Strong balance sheet with low debt-to-equity ratio',
    'Market leadership position with competitive advantages',
    'Positive analyst upgrades and target price revisions',
    'Government policy support benefiting the sector',
    'Digital transformation initiatives showing promising results',
    'Export growth potential with global market expansion',
    'Dividend yield attractive for income-focused investors',
    'Management guidance upgrade for upcoming quarters',
    'Strategic partnerships enhancing business prospects',
    'ESG initiatives improving long-term sustainability'
  ];

  // Static Q&A patterns
  const staticResponses = {
    greetings: [
      "Hello! Ready to explore the exciting world of Indian stock markets? 📈",
      "Hi there! Let's dive into some stock analysis together! 🚀",
      "Welcome! I'm here to help you navigate the stock market maze! 💡",
      "Hey! What stock catches your interest today? 🎯"
    ],
    help: [
      `I can help you with comprehensive analysis of our top 3 Indian stocks! Here's what I can do:

🔍 **My Capabilities:**
• Stock Recommendations - Get buy/sell advice for TCS, HDFC Bank, Reliance
• Price Predictions - Forecast future movements for these 3 stocks
• Risk Analysis - Understand volatility metrics for each stock
• Stock Comparisons - Compare any 2 of the 3 stocks
• Market Insights - Sector analysis for IT, Banking, and Energy/Retail

📊 **Our Focus Stocks:**
• **TCS** - India's largest IT services company
• **HDFC Bank** - Leading private sector bank
• **Reliance** - Diversified conglomerate (Oil, Retail, Telecom)

💡 **Popular Questions:**
• "Which of the 3 stocks should I buy?"
• "TCS vs HDFC Bank comparison"
• "Reliance price prediction"
• "Risk analysis for HDFC Bank"

Just ask me anything about TCS, HDFC Bank, or Reliance!`,

`Here's how I can assist you with these 3 premium Indian stocks:

💰 **Trading Insights for:**
🔹 **TCS (TCS.NS)** - IT Services sector leader
🔹 **HDFC Bank (HDFCBANK.NS)** - Banking sector champion  
🔹 **Reliance (RELIANCE.NS)** - Multi-sector giant

🎯 **Quick Commands:**
• "Recommend from the 3 stocks" - Get best pick
• "Compare all 3 stocks" - Full comparison
• "TCS analysis" - Detailed TCS insights
• "HDFC Bank outlook" - Banking sector view
• "Reliance forecast" - Energy/retail perspective

🏆 **Why These 3 Stocks?**
• Market leaders in their sectors
• Strong fundamentals and growth potential
• High liquidity and institutional interest
• Proven track record of performance

What would you like to explore about these top stocks?`
    ],
    marketOutlook: [
      `📊 **Current Market Outlook**

🟢 **Bullish Sentiment:** 
• IT sector showing strong momentum
• Banking stocks recovering well
• FII inflows supporting market

📈 **Key Trends:**
• Digital transformation stocks outperforming
• ESG-focused companies gaining traction
• Small-cap stocks showing volatility

⚠️ **Watch Out For:**
• Global economic uncertainties
• Interest rate policy changes
• Commodity price fluctuations

Overall market sentiment: **CAUTIOUSLY OPTIMISTIC**`,

`🌟 **Market Analysis Update**

💪 **Strength Areas:**
• Technology sector leadership continues
• Financial services showing resilience
• Consumer discretionary picking up pace

🔍 **Opportunities:**
• Value stocks at attractive levels
• Dividend-paying stocks for stability
• Growth stocks with strong fundamentals

📉 **Challenges:**
• Inflation concerns persist
• Global supply chain issues
• Currency fluctuation impacts

Market recommendation: **SELECTIVE BUYING**`
    ],
    bestSectors: [
      `🏆 **Analysis of Our 3 Stock Sectors**

1️⃣ **Information Technology (TCS)**
   • Strong export growth potential
   • Digital transformation driving demand
   • Margin expansion opportunities
   • Global delivery model advantage

2️⃣ **Banking & Financial Services (HDFC Bank)**
   • Credit growth recovery underway
   • NPA reduction trends positive
   • Digital banking adoption accelerating
   • Strong deposit franchise

3️⃣ **Diversified Conglomerate (Reliance)**
   • Energy transition opportunities
   • Retail expansion in tier-2/3 cities
   • Telecom market leadership (Jio)
   • Petrochemicals export potential

🎯 **Sector Outlook:** All three sectors show promise with different risk-reward profiles!`,

`⭐ **Sector Performance Analysis**

🚀 **Current Leaders:**
• **IT Services (TCS)** - Export growth, margin stability
• **Private Banking (HDFC Bank)** - Credit cycle recovery
• **Integrated Business (Reliance)** - Diversification benefits

💎 **Investment Themes:**
• **Technology** - Digital transformation wave
• **Financial Services** - Economic recovery play
• **Energy & Retail** - Consumption growth story

🛡️ **Risk Considerations:**
• **TCS** - Currency fluctuations, global slowdown
• **HDFC Bank** - Interest rate cycles, credit costs
• **Reliance** - Oil price volatility, regulatory changes

Choose based on your sector preference and risk appetite!`
    ]
  };

  // Get random element from array
  const getRandomElement = (arr: any[]) => arr[Math.floor(Math.random() * arr.length)];

  // Generate random stock recommendation
  const generateRandomRecommendation = () => {
    const stock = getRandomElement(stockDatabase);
    const action = getRandomElement(actions);
    const confidence = getRandomElement(confidenceLevels);
    const reason = getRandomElement(reasons);
    const priceVariation = (Math.random() - 0.5) * 0.1; // ±5% price variation
    const currentPrice = Math.round(stock.price * (1 + priceVariation));
    const targetPrice = Math.round(currentPrice * (1 + (Math.random() * 0.2 + 0.05))); // 5-25% upside

    return {
      content: `🎯 **Trading Recommendation**

**${stock.name} (${stock.symbol})**

💰 **Current Price:** ₹${currentPrice.toLocaleString()}
🎯 **Recommendation:** ${action}
📈 **Confidence:** ${confidence}%
🚀 **Target Price:** ₹${targetPrice.toLocaleString()}
📊 **Sector:** ${stock.sector}

💡 **Analysis:**
${reason}

⚡ **Technical Outlook:** ${stock.trend === 'bullish' ? 'Bullish momentum with strong support levels' : stock.trend === 'neutral' ? 'Sideways movement, wait for breakout' : 'Bearish pressure, consider exit strategy'}

*This recommendation is based on current market analysis and technical indicators.*`,
      metadata: {
        action: 'recommendation',
        symbol: stock.symbol,
        confidence: confidence
      }
    };
  };

  // Generate random comparison between the 3 stocks
  const generateRandomComparison = () => {
    const stock1 = getRandomElement(stockDatabase);
    const stock2 = getRandomElement(stockDatabase.filter(s => s.symbol !== stock1.symbol));
    const winner = Math.random() > 0.5 ? stock1 : stock2;

    const comparisonReasons = {
      'TCS': [
        'Consistent revenue growth and strong client relationships',
        'Leading market position in IT services globally',
        'Strong cash generation and dividend track record',
        'Resilient business model with recurring revenues'
      ],
      'HDFC Bank': [
        'Superior asset quality and risk management',
        'Strong deposit franchise and CASA ratio',
        'Digital banking leadership and innovation',
        'Consistent profitability and ROE performance'
      ],
      'Reliance': [
        'Diversified business model reducing sector risks',
        'Strong balance sheet and cash flow generation',
        'Leadership in multiple business segments',
        'Strategic investments in future growth areas'
      ]
    };

    return {
      content: `📊 **Stock Comparison Analysis**

**${stock1.name} vs ${stock2.name}**

📈 **${stock1.name} (${stock1.symbol})**
• Current Price: ₹${stock1.price.toLocaleString()}
• Sector: ${stock1.sector}
• Market Trend: ${stock1.trend}
• Key Strength: ${getRandomElement(comparisonReasons[stock1.name as keyof typeof comparisonReasons])}

📈 **${stock2.name} (${stock2.symbol})**
• Current Price: ₹${stock2.price.toLocaleString()}
• Sector: ${stock2.sector}
• Market Trend: ${stock2.trend}
• Key Strength: ${getRandomElement(comparisonReasons[stock2.name as keyof typeof comparisonReasons])}

🏆 **Winner: ${winner.name}**

**Decision Factors:**
• ${getRandomElement(comparisonReasons[winner.name as keyof typeof comparisonReasons])}
• Better sector positioning for current market
• Superior risk-adjusted return potential
• Stronger fundamental metrics

**Recommendation:** Consider ${winner.name} for better portfolio performance among these two options.

*Both are quality stocks - choice depends on your sector preference and risk tolerance.*`,
      metadata: {
        action: 'comparison',
        symbol: `${stock1.symbol}, ${stock2.symbol}`,
        confidence: getRandomElement(confidenceLevels)
      }
    };
  };

  // Generate random prediction
  const generateRandomPrediction = (symbol?: string) => {
    const stock = symbol ? 
      stockDatabase.find(s => s.symbol.toLowerCase().includes(symbol.toLowerCase()) || s.name.toLowerCase().includes(symbol.toLowerCase())) || getRandomElement(stockDatabase)
      : getRandomElement(stockDatabase);
    
    const predictions = {
      '1 day': Math.round(stock.price * (1 + (Math.random() - 0.5) * 0.04)), // ±2%
      '1 week': Math.round(stock.price * (1 + (Math.random() - 0.5) * 0.08)), // ±4%
      '1 month': Math.round(stock.price * (1 + (Math.random() - 0.5) * 0.15)), // ±7.5%
      '3 months': Math.round(stock.price * (1 + (Math.random() - 0.5) * 0.25)) // ±12.5%
    };

    return {
      content: `📈 **Price Prediction for ${stock.name}**

**Current Price:** ₹${stock.price.toLocaleString()}

**Forecasted Prices:**
• **1 Day:** ₹${predictions['1 day'].toLocaleString()}
• **1 Week:** ₹${predictions['1 week'].toLocaleString()}
• **1 Month:** ₹${predictions['1 month'].toLocaleString()}
• **3 Months:** ₹${predictions['3 months'].toLocaleString()}

📊 **Prediction Confidence:** ${getRandomElement(confidenceLevels)}%

**Key Drivers:**
• ${getRandomElement(reasons)}
• Market sentiment and sector rotation
• Technical pattern analysis

*Predictions based on AI analysis of market trends and historical patterns.*`,
      metadata: {
        action: 'prediction',
        symbol: stock.symbol,
        confidence: getRandomElement(confidenceLevels)
      }
    };
  };

  // Generate random risk analysis
  const generateRandomRiskAnalysis = (symbol?: string) => {
    const stock = symbol ? 
      stockDatabase.find(s => s.symbol.toLowerCase().includes(symbol.toLowerCase()) || s.name.toLowerCase().includes(symbol.toLowerCase())) || getRandomElement(stockDatabase)
      : getRandomElement(stockDatabase);
    
    const volatility = (Math.random() * 25 + 10).toFixed(1); // 10-35%
    const beta = (Math.random() * 1.5 + 0.5).toFixed(2); // 0.5-2.0
    const sharpe = (Math.random() * 1.5 + 0.3).toFixed(2); // 0.3-1.8

    const riskLevel = parseFloat(volatility) > 25 ? 'High' : parseFloat(volatility) > 18 ? 'Medium' : 'Low';
    const riskColor = riskLevel === 'High' ? '🔴' : riskLevel === 'Medium' ? '🟡' : '🟢';

    return {
      content: `⚠️ **Risk Analysis for ${stock.name}**

**Risk Metrics:**
• **Volatility:** ${volatility}%
• **Beta:** ${beta}
• **Sharpe Ratio:** ${sharpe}
• **Sector Risk:** ${stock.sector} sector dynamics

${riskColor} **Risk Level: ${riskLevel}**

**Risk Factors:**
• Market volatility impact
• Sector-specific challenges
• Regulatory environment changes
• Global economic conditions

**Risk Management:**
• Position sizing based on risk tolerance
• Stop-loss levels at key support
• Diversification across sectors
• Regular portfolio rebalancing

*Risk assessment based on historical data and current market conditions.*`,
      metadata: {
        action: 'risk_analysis',
        symbol: stock.symbol,
        confidence: 85
      }
    };
  };

  // Detect query type and generate appropriate response
  const generateResponse = (message: string) => {
    const lowerMessage = message.toLowerCase();
    
    // Greeting responses
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey') || lowerMessage.includes('good morning') || lowerMessage.includes('good afternoon')) {
      return {
        content: getRandomElement(staticResponses.greetings),
        metadata: { confidence: 95, action: 'greeting' }
      };
    }
    
    // Help responses
    if (lowerMessage.includes('help') || lowerMessage.includes('what can you do') || lowerMessage.includes('how to use') || lowerMessage.includes('guide')) {
      return {
        content: getRandomElement(staticResponses.help),
        metadata: { confidence: 95, action: 'help' }
      };
    }
    
    // Market outlook
    if (lowerMessage.includes('market outlook') || lowerMessage.includes('market view') || lowerMessage.includes('market sentiment') || lowerMessage.includes('market analysis')) {
      return {
        content: getRandomElement(staticResponses.marketOutlook),
        metadata: { confidence: 88, action: 'market_outlook' }
      };
    }
    
    // Best sectors
    if (lowerMessage.includes('best sector') || lowerMessage.includes('top sector') || lowerMessage.includes('sector recommendation') || lowerMessage.includes('which sector')) {
      return {
        content: getRandomElement(staticResponses.bestSectors),
        metadata: { confidence: 85, action: 'sector_analysis' }
      };
    }
    
    // Predictions
    if (lowerMessage.includes('predict') || lowerMessage.includes('forecast') || lowerMessage.includes('price target') || lowerMessage.includes('future price')) {
      const symbolMatch = message.match(/\b([A-Za-z]{2,10})\b/i);
      return generateRandomPrediction(symbolMatch ? symbolMatch[1] : undefined);
    }
    
    // Risk analysis
    if (lowerMessage.includes('risk') || lowerMessage.includes('volatility') || lowerMessage.includes('safe') || lowerMessage.includes('dangerous')) {
      const symbolMatch = message.match(/\b([A-Za-z]{2,10})\b/i);
      return generateRandomRiskAnalysis(symbolMatch ? symbolMatch[1] : undefined);
    }
    
    // Comparisons
    if (lowerMessage.includes('compare') || lowerMessage.includes('vs') || lowerMessage.includes('versus') || lowerMessage.includes('better')) {
      return generateRandomComparison();
    }
    
    // General recommendations (default)
    return generateRandomRecommendation();
  };

  // Send message
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Simulate thinking time
    setTimeout(() => {
      try {
        const response = generateResponse(currentInput);
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.content,
          type: 'assistant',
          timestamp: new Date(),
          metadata: response.metadata
        };

        setMessages(prev => [...prev, assistantMessage]);
      } catch (error) {
        console.error('Error generating response:', error);
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: 'I apologize, but I encountered an error. Please try asking again!',
          type: 'assistant',
          timestamp: new Date(),
          metadata: { confidence: 0 }
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }, 1000 + Math.random() * 2000); // 1-3 second delay for realism
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900">
        <div className="flex items-center space-x-2">
          <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            AI Trading Assistant
          </h2>
          <span className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full">
            Connected
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-slate-800">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 shadow-sm ${
                message.type === 'user'
                  ? 'bg-blue-600 dark:bg-blue-500 text-white'
                  : 'bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 border border-gray-200 dark:border-slate-600'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'assistant' && (
                  <div className="flex-shrink-0 mt-1">
                    {message.metadata?.action === 'prediction' && <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />}
                    {message.metadata?.action === 'recommendation' && <BarChart3 className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
                    {message.metadata?.action === 'risk_analysis' && <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />}
                    {message.metadata?.action === 'comparison' && <PieChart className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
                    {(!message.metadata?.action || message.metadata?.action === 'general_chat' || message.metadata?.action === 'greeting' || message.metadata?.action === 'help') && <Bot className="w-4 h-4 text-gray-600 dark:text-gray-400" />}
                  </div>
                )}
                <div className="flex-1">
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
                  {message.metadata && (
                    <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                      <span className="text-gray-500 dark:text-slate-400">{message.timestamp.toLocaleTimeString()}</span>
                      {message.metadata.confidence !== undefined && (
                        <span className="text-gray-500 dark:text-slate-400">Confidence: {message.metadata.confidence}%</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-3 shadow-sm">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask: 'Which of the 3 stocks should I buy?', 'TCS vs HDFC comparison', 'Reliance prediction'..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 placeholder-gray-500 dark:placeholder-slate-400"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}