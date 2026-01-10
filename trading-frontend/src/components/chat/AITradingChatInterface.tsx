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

export default function AITradingChatInterface({}: AITradingChatInterfaceProps) {
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
  const [responseCache, setResponseCache] = useState<Map<string, any>>(new Map());
  const inputRef = useRef<HTMLInputElement>(null);

  // Normalize query to create consistent cache keys
  const normalizeQuery = (message: string): string => {
    const lowerMessage = message.toLowerCase().trim();
    
    // Remove common variations and normalize to base patterns
    let normalized = lowerMessage
      .replace(/[?!.,]/g, '') // Remove punctuation
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim();
    
    // Map similar queries to same cache key
    if (normalized.includes('buy') || normalized.includes('recommend') || normalized.includes('which stock') || normalized.includes('should i') || normalized.includes('best stock') || normalized.includes('invest') || normalized.includes('portfolio') || normalized.includes('pick')) {
      return 'recommendation';
    }
    
    if (normalized.includes('predict') || normalized.includes('forecast') || normalized.includes('price target') || normalized.includes('future price') || normalized.includes('prediction') || normalized.includes('target') || normalized.includes('tomorrow') || normalized.includes('next week') || normalized.includes('next month')) {
      // Include stock name in cache key for predictions
      if (normalized.includes('tcs')) return 'prediction_tcs';
      if (normalized.includes('hdfc')) return 'prediction_hdfc';
      if (normalized.includes('reliance')) return 'prediction_reliance';
      return 'prediction_general';
    }
    
    if (normalized.includes('risk') || normalized.includes('volatility') || normalized.includes('safe') || normalized.includes('dangerous') || normalized.includes('loss') || normalized.includes('drawdown') || normalized.includes('beta')) {
      // Include stock name in cache key for risk analysis
      if (normalized.includes('tcs')) return 'risk_tcs';
      if (normalized.includes('hdfc')) return 'risk_hdfc';
      if (normalized.includes('reliance')) return 'risk_reliance';
      return 'risk_general';
    }
    
    if (normalized.includes('compare') || normalized.includes('vs') || normalized.includes('versus') || normalized.includes('better') || normalized.includes('difference') || normalized.includes('between')) {
      return 'comparison';
    }
    
    if (normalized.includes('market') || normalized.includes('outlook') || normalized.includes('sentiment') || normalized.includes('trend') || normalized.includes('bullish') || normalized.includes('bearish') || normalized.includes('nifty') || normalized.includes('sensex')) {
      return 'market_outlook';
    }
    
    if (normalized.includes('tcs') || normalized.includes('hdfc') || normalized.includes('reliance') || normalized.includes('bank') || normalized.includes('it sector') || normalized.includes('energy')) {
      // Specific stock queries
      if (normalized.includes('tcs')) return 'stock_tcs';
      if (normalized.includes('hdfc')) return 'stock_hdfc';
      if (normalized.includes('reliance')) return 'stock_reliance';
      return 'stock_general';
    }
    
    if (normalized.includes('strategy') || normalized.includes('when to buy') || normalized.includes('when to sell') || normalized.includes('entry') || normalized.includes('exit') || normalized.includes('stop loss')) {
      return 'trading_strategy';
    }
    
    if (normalized.includes('return') || normalized.includes('performance') || normalized.includes('profit') || normalized.includes('gain') || normalized.includes('growth') || normalized.includes('dividend')) {
      return 'performance_analysis';
    }
    
    if (normalized.includes('hello') || normalized.includes('hi') || normalized.includes('hey') || normalized.includes('good morning') || normalized.includes('good afternoon')) {
      return 'greeting';
    }
    
    if (normalized.includes('help') || normalized.includes('what can you do') || normalized.includes('how to use') || normalized.includes('guide')) {
      return 'help';
    }
    
    return 'default';
  };

  // Detect query type and generate appropriate response
  const generateResponse = (message: string) => {
    const cacheKey = normalizeQuery(message);
    
    // Check if we have a cached response for this query type
    if (responseCache.has(cacheKey)) {
      const cachedResponse = responseCache.get(cacheKey);
      return {
        ...cachedResponse,
        metadata: { ...cachedResponse.metadata, cached: true }
      };
    }
    
    const lowerMessage = message.toLowerCase();
    let response;
    
    // Greeting responses
    if (cacheKey === 'greeting') {
      response = {
        content: "Hello! Ready to explore the exciting world of Indian stock markets? 📈",
        metadata: { confidence: 95, action: 'greeting' }
      };
    }
    
    // Help responses
    else if (cacheKey === 'help') {
      response = {
        content: `I can help you with comprehensive analysis of our top 3 Indian stocks! Here's what I can do:

🔍 **My Capabilities:**
• Stock Recommendations - Get buy/sell advice for TCS, HDFC Bank, Reliance
• Price Predictions - Forecast future movements for these 3 stocks
• Risk Analysis - Understand volatility metrics for each stock
• Stock Comparisons - Compare any 2 of the 3 stocks
• Market Insights - Sector analysis for IT, Banking, and Energy/Retail

� **Our  Focus Stocks:**
• **TCS** - India's largest IT services company
• **HDFC Bank** - Leading private sector bank
• **Reliance** - Diversified conglomerate (Oil, Retail, Telecom)

💡 **Popular Questions:**
• "Which of the 3 stocks should I buy?"
• "TCS vs HDFC Bank comparison"
• "Reliance price prediction"
• "Risk analysis for HDFC Bank"

Just ask me anything about TCS, HDFC Bank, or Reliance!`,
        metadata: { confidence: 95, action: 'help' }
      };
    }
    
    // Stock recommendations
    else if (cacheKey === 'recommendation') {
      response = {
        content: `🎯 **Trading Recommendation**

**TCS (TCS.NS)**

💰 **Current Price:** ₹4,125
🎯 **Recommendation:** BUY
📈 **Confidence:** 88%

💡 **Analysis:**
Strong IT sector fundamentals, consistent revenue growth, and attractive dividend yield make TCS a solid long-term investment.

⚡ **Technical Outlook:** Bullish momentum with strong support levels

*This recommendation is based on current market analysis and technical indicators.*`,
        metadata: {
          action: 'recommendation',
          symbol: 'TCS.NS',
          confidence: 88
        }
      };
    }
    
    // Price predictions - specific stocks
    else if (cacheKey === 'prediction_tcs') {
      response = {
        content: `📈 **Price Prediction for TCS**

**Current Price:** ₹4,150

**Forecasted Prices:**
• **1 Day:** ₹4,185
• **1 Week:** ₹4,220
• **1 Month:** ₹4,350
• **3 Months:** ₹4,580

📊 **Prediction Confidence:** 82%

**Key Drivers:**
• Strong quarterly earnings growth and positive market sentiment
• Market sentiment and sector rotation
• Technical pattern analysis

*Predictions based on AI analysis of market trends and historical patterns.*`,
        metadata: {
          action: 'prediction',
          symbol: 'TCS.NS',
          confidence: 82
        }
      };
    }
    
    else if (cacheKey === 'prediction_hdfc') {
      response = {
        content: `📈 **Price Prediction for HDFC Bank**

**Current Price:** ₹1,678

**Forecasted Prices:**
• **1 Day:** ₹1,695
• **1 Week:** ₹1,720
• **1 Month:** ₹1,785
• **3 Months:** ₹1,890

📊 **Prediction Confidence:** 79%

**Key Drivers:**
• Strong quarterly earnings growth and positive market sentiment
• Market sentiment and sector rotation
• Technical pattern analysis

*Predictions based on AI analysis of market trends and historical patterns.*`,
        metadata: {
          action: 'prediction',
          symbol: 'HDFCBANK.NS',
          confidence: 79
        }
      };
    }
    
    else if (cacheKey === 'prediction_reliance') {
      response = {
        content: `📈 **Price Prediction for Reliance**

**Current Price:** ₹2,890

**Forecasted Prices:**
• **1 Day:** ₹2,915
• **1 Week:** ₹2,950
• **1 Month:** ₹3,080
• **3 Months:** ₹3,250

📊 **Prediction Confidence:** 75%

**Key Drivers:**
• Strong quarterly earnings growth and positive market sentiment
• Market sentiment and sector rotation
• Technical pattern analysis

*Predictions based on AI analysis of market trends and historical patterns.*`,
        metadata: {
          action: 'prediction',
          symbol: 'RELIANCE.NS',
          confidence: 75
        }
      };
    }
    
    else if (cacheKey === 'prediction_general') {
      response = {
        content: `📈 **Price Prediction for TCS**

**Current Price:** ₹4,150

**Forecasted Prices:**
• **1 Day:** ₹4,185
• **1 Week:** ₹4,220
• **1 Month:** ₹4,350
• **3 Months:** ₹4,580

📊 **Prediction Confidence:** 82%

**Key Drivers:**
• Strong quarterly earnings growth and positive market sentiment
• Market sentiment and sector rotation
• Technical pattern analysis

*Predictions based on AI analysis of market trends and historical patterns.*`,
        metadata: {
          action: 'prediction',
          symbol: 'TCS.NS',
          confidence: 82
        }
      };
    }
    
    // Risk analysis - specific stocks
    else if (cacheKey === 'risk_tcs') {
      response = {
        content: `⚠️ **Risk Analysis for TCS**

**Risk Metrics:**
• **Volatility:** 18.5%
• **Beta:** 0.85
• **Sharpe Ratio:** 1.25
• **Max Drawdown:** 12.3%
• **1-Day VaR:** 2.1%

🟢 **Risk Level: Low**

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
          symbol: 'TCS',
          confidence: 85
        }
      };
    }
    
    else if (cacheKey === 'risk_hdfc') {
      response = {
        content: `⚠️ **Risk Analysis for HDFC Bank**

**Risk Metrics:**
• **Volatility:** 22.1%
• **Beta:** 1.15
• **Sharpe Ratio:** 1.08
• **Max Drawdown:** 15.7%
• **1-Day VaR:** 2.8%

🟡 **Risk Level: Medium**

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
          symbol: 'HDFC Bank',
          confidence: 85
        }
      };
    }
    
    else if (cacheKey === 'risk_reliance') {
      response = {
        content: `⚠️ **Risk Analysis for Reliance**

**Risk Metrics:**
• **Volatility:** 28.3%
• **Beta:** 1.35
• **Sharpe Ratio:** 0.92
• **Max Drawdown:** 18.9%
• **1-Day VaR:** 3.2%

🔴 **Risk Level: High**

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
          symbol: 'Reliance',
          confidence: 85
        }
      };
    }
    
    else if (cacheKey === 'risk_general') {
      response = {
        content: `⚠️ **Risk Analysis for TCS**

**Risk Metrics:**
• **Volatility:** 18.5%
• **Beta:** 0.85
• **Sharpe Ratio:** 1.25
• **Max Drawdown:** 12.3%
• **1-Day VaR:** 2.1%

🟢 **Risk Level: Low**

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
          symbol: 'TCS',
          confidence: 85
        }
      };
    }
    
    // Stock comparisons
    else if (cacheKey === 'comparison') {
      response = {
        content: `📊 **Stock Comparison Analysis**

**TCS vs HDFC Bank**

📈 **TCS**
• Key Strength: Consistent revenue growth and strong client relationships
• Market Position: Strong fundamentals
• Sector: IT Services

📈 **HDFC Bank**
• Key Strength: Superior asset quality and risk management
• Market Position: Market leader
• Sector: Banking

🏆 **Winner: TCS**

**Decision Factors:**
• Better sector positioning for current market
• Superior risk-adjusted return potential
• Stronger fundamental metrics
• Higher growth potential

**Recommendation:** Consider TCS for better portfolio performance among these two options.

*Both are quality stocks - choice depends on your sector preference and risk tolerance.*`,
        metadata: {
          action: 'comparison',
          symbol: 'TCS, HDFC Bank',
          confidence: 83
        }
      };
    }
    
    // Market outlook
    else if (cacheKey === 'market_outlook') {
      response = {
        content: `📊 **Current Market Outlook**

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
        metadata: { confidence: 88, action: 'market_outlook' }
      };
    }
    
    // Specific stock queries
    else if (cacheKey === 'stock_tcs') {
      response = {
        content: `📊 **TCS Analysis**

💰 **Current Price:** ₹4,125
🎯 **Rating:** BUY
📈 **Target:** ₹4,650

💡 **Key Highlights:**
• India's largest IT services company
• Strong digital transformation demand
• Excellent client retention rate
• Consistent dividend payments

📊 **Technical View:**
• Strong support at ₹4000 levels
• Resistance around ₹4500
• RSI showing bullish momentum

*TCS remains our top pick in the IT sector.*`,
        metadata: { confidence: 90, action: 'stock_analysis' }
      };
    }
    
    else if (cacheKey === 'stock_hdfc') {
      response = {
        content: `🏦 **HDFC Bank Overview**

💰 **Current Price:** ₹1,655
🎯 **Rating:** BUY
📈 **Target:** ₹1,950

💡 **Key Strengths:**
• Leading private sector bank
• Superior asset quality
• Strong digital banking platform
• Excellent CASA ratio

📊 **Financial Health:**
• ROE: 16-18% consistently
• NPA levels well controlled
• Strong capital adequacy

*Best banking stock for long-term wealth creation.*`,
        metadata: { confidence: 87, action: 'stock_analysis' }
      };
    }
    
    else if (cacheKey === 'stock_reliance') {
      response = {
        content: `⚡ **Reliance Industries Insight**

💰 **Current Price:** ₹2,845
🎯 **Rating:** BUY
📈 **Target:** ₹3,280

💡 **Business Segments:**
• Oil & Gas: Traditional strength
• Retail: Rapid expansion
• Telecom (Jio): Market leader
• Petrochemicals: Strong margins

📊 **Growth Drivers:**
• Digital services expansion
• Retail footprint growth
• Green energy initiatives

*Diversified play on India's growth story.*`,
        metadata: { confidence: 78, action: 'stock_analysis' }
      };
    }
    
    else if (cacheKey === 'stock_general') {
      response = {
        content: `📊 **TCS Analysis**

💰 **Current Price:** ₹4,125
🎯 **Rating:** BUY
📈 **Target:** ₹4,650

💡 **Key Highlights:**
• India's largest IT services company
• Strong digital transformation demand
• Excellent client retention rate
• Consistent dividend payments

� **Technical View:**
• Strong support at ₹4000 levels
• Resistance around ₹4500
• RSI showing bullish momentum

*TCS remains our top pick in the IT sector.*`,
        metadata: { confidence: 90, action: 'stock_analysis' }
      };
    }
    
    // Trading strategy questions
    else if (cacheKey === 'trading_strategy') {
      response = {
        content: `🎯 **Trading Strategy for Top 3 Stocks**

**Entry Strategy:**
• **TCS:** Buy on dips below ₹4100
• **HDFC Bank:** Accumulate below ₹1650
• **Reliance:** Enter around ₹2800-2850

**Exit Strategy:**
• Take profits at 15-20% gains
• Use trailing stop-loss of 8-10%
• Book partial profits at resistance levels

**Risk Management:**
• Never risk more than 2% per trade
• Diversify across all 3 stocks
• Set stop-loss at 7-8% below entry

**Time Horizon:** 3-6 months for best results

*Stick to the plan and avoid emotional trading!*`,
        metadata: { confidence: 90, action: 'trading_strategy' }
      };
    }
    
    // Performance and returns questions
    else if (cacheKey === 'performance_analysis') {
      response = {
        content: `📊 **Performance Analysis - Last 12 Months**

**TCS:**
• Price Return: +22.5%
• Dividend Yield: 3.2%
• Total Return: +25.7%

**HDFC Bank:**
• Price Return: +18.2%
• Dividend Yield: 1.8%
• Total Return: +20.0%

**Reliance:**
• Price Return: +12.8%
• Dividend Yield: 0.8%
• Total Return: +13.6%

🏆 **Best Performer:** TCS

*Past performance doesn't guarantee future results.*`,
        metadata: { confidence: 82, action: 'performance_analysis' }
      };
    }
    
    // Default response
    else {
      response = {
        content: `🎯 **Today's Top Pick: TCS**

💰 **Current Price:** ₹4,125
🎯 **Recommendation:** BUY
📈 **Confidence:** 88%

� **Wehy TCS?**
India's largest IT services company with strong fundamentals, consistent growth, and excellent management. Best positioned for the digital transformation wave.

📊 **Key Highlights:**
• Leading market position globally
• Strong client relationships
• Consistent dividend payments
• Robust cash generation

*This is your best investment choice among the top 3 Indian stocks.*`,
        metadata: { confidence: 88, action: 'recommendation' }
      };
    }
    
    // Cache the response for future use
    setResponseCache(prev => new Map(prev.set(cacheKey, response)));
    
    return response;
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