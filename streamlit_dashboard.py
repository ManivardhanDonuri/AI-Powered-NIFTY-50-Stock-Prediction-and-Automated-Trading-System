import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import logging

# Import our modules
from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators
from ml_signal_generator import MLSignalGenerator
from ml_models import MLModels
from ml_feature_engineer import MLFeatureEngineer
from backtester import Backtester

# Configure page
st.set_page_config(
    page_title="NIFTY 50 ML Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .signal-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #28a745;
    }
    .signal-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #dc3545;
    }
    .signal-neutral {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_config():
    """Load configuration."""
    with open('config.json', 'r') as f:
        return json.load(f)

@st.cache_data(ttl=300)
def fetch_stock_data(symbol, days=365):
    """Fetch and cache stock data."""
    try:
        data_fetcher = DataFetcher()
        # Temporarily modify config for single stock
        data_fetcher.stocks = [symbol]
        data_fetcher.lookback_days = days
        
        stock_data = data_fetcher.fetch_stock_data(symbol)
        return stock_data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

@st.cache_data(ttl=300)
def calculate_indicators(stock_data):
    """Calculate technical indicators."""
    try:
        indicators = TechnicalIndicators()
        return indicators.calculate_indicators(stock_data)
    except Exception as e:
        st.error(f"Error calculating indicators: {str(e)}")
        return None

def get_ml_prediction(symbol, indicators_data):
    """Get ML model predictions."""
    try:
        feature_engineer = MLFeatureEngineer()
        ml_models = MLModels()
        
        # Engineer features
        engineered_data = feature_engineer.engineer_features(indicators_data)
        if engineered_data is None:
            return None
        
        # Prepare prediction data
        pred_data = feature_engineer.prepare_prediction_data(engineered_data, symbol)
        if pred_data is None:
            return None
        
        # Get predictions
        predictions = {}
        config = load_config()
        
        for model_type in config['ml']['models']:
            pred = ml_models.predict(pred_data, symbol, model_type)
            if pred is not None:
                predictions[model_type] = pred
        
        return predictions
    except Exception as e:
        st.error(f"Error getting ML predictions: {str(e)}")
        return None

def create_price_chart(data, signals=None):
    """Create interactive price chart with signals."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxis=True,
        vertical_spacing=0.1,
        subplot_titles=('Price & Moving Averages', 'RSI'),
        row_heights=[0.7, 0.3]
    )
    
    # Price and moving averages
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
    
    # Add signals if provided
    if signals:
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        if buy_signals:
            buy_dates = [datetime.strptime(s['date'], '%Y-%m-%d') for s in buy_signals]
            buy_prices = [s['price'] for s in buy_signals]
            fig.add_trace(
                go.Scatter(x=buy_dates, y=buy_prices, mode='markers',
                          name='Buy Signal', marker=dict(color='green', size=10, symbol='triangle-up')),
                row=1, col=1
            )
        
        if sell_signals:
            sell_dates = [datetime.strptime(s['date'], '%Y-%m-%d') for s in sell_signals]
            sell_prices = [s['price'] for s in sell_signals]
            fig.add_trace(
                go.Scatter(x=sell_dates, y=sell_prices, mode='markers',
                          name='Sell Signal', marker=dict(color='red', size=10, symbol='triangle-down')),
                row=1, col=1
            )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=data.index, y=data['RSI'], name='RSI', 
                  line=dict(color='purple', width=2)),
        row=2, col=1
    )
    
    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7, row=2, col=1)
    
    # Fill RSI zones
    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.2, row=2, col=1)
    
    fig.update_layout(
        title="Stock Price Analysis with Trading Signals",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        height=600,
        showlegend=True
    )
    
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    
    return fig

def create_ml_prediction_chart(predictions):
    """Create ML prediction visualization."""
    if not predictions:
        return None
    
    models = list(predictions.keys())
    probs = list(predictions.values())
    
    fig = go.Figure(data=[
        go.Bar(x=models, y=probs, 
               marker_color=['green' if p > 0.5 else 'red' for p in probs])
    ])
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="black", opacity=0.7)
    
    fig.update_layout(
        title="ML Model Predictions",
        xaxis_title="Model",
        yaxis_title="Probability (Buy Direction)",
        yaxis=dict(range=[0, 1]),
        height=300
    )
    
    return fig

def main():
    """Main dashboard function."""
    st.title("📈 NIFTY 50 ML Trading Dashboard")
    st.markdown("---")
    
    # Load configuration
    config = load_config()
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # Stock selection
    available_stocks = config['trading']['stocks']
    selected_stock = st.sidebar.selectbox("Select Stock", available_stocks)
    
    # Model selection
    available_models = config['ml']['models']
    selected_models = st.sidebar.multiselect("Select ML Models", available_models, default=available_models)
    
    # Signal mode
    signal_modes = ['rule', 'ml', 'hybrid']
    selected_mode = st.sidebar.selectbox("Signal Mode", signal_modes, index=2)
    
    # Time period
    time_periods = {
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730
    }
    selected_period = st.sidebar.selectbox("Time Period", list(time_periods.keys()), index=2)
    days = time_periods[selected_period]
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Main content
    if selected_stock:
        # Fetch data
        with st.spinner(f"Fetching data for {selected_stock}..."):
            stock_data = fetch_stock_data(selected_stock, days)
        
        if stock_data is not None and not stock_data.empty:
            # Calculate indicators
            with st.spinner("Calculating technical indicators..."):
                indicators_data = calculate_indicators(stock_data)
            
            if indicators_data is not None:
                # Current metrics
                latest = indicators_data.iloc[-1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"₹{latest['Close']:.2f}",
                        delta=f"{((latest['Close'] - indicators_data.iloc[-2]['Close']) / indicators_data.iloc[-2]['Close'] * 100):.2f}%"
                    )
                
                with col2:
                    st.metric(
                        label="SMA 20",
                        value=f"₹{latest['SMA_20']:.2f}",
                        delta=f"{((latest['SMA_20'] - latest['SMA_50']) / latest['SMA_50'] * 100):.2f}%" if latest['SMA_50'] > 0 else "0%"
                    )
                
                with col3:
                    st.metric(
                        label="SMA 50",
                        value=f"₹{latest['SMA_50']:.2f}"
                    )
                
                with col4:
                    rsi_color = "normal"
                    if latest['RSI'] > 70:
                        rsi_color = "inverse"
                    elif latest['RSI'] < 30:
                        rsi_color = "normal"
                    
                    st.metric(
                        label="RSI",
                        value=f"{latest['RSI']:.2f}",
                        delta="Overbought" if latest['RSI'] > 70 else "Oversold" if latest['RSI'] < 30 else "Neutral"
                    )
                
                # ML Predictions
                st.subheader("🤖 ML Model Predictions")
                
                with st.spinner("Getting ML predictions..."):
                    predictions = get_ml_prediction(selected_stock, indicators_data)
                
                if predictions:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Prediction metrics
                        avg_prediction = np.mean(list(predictions.values()))
                        confidence = 1 - np.std(list(predictions.values()))
                        
                        if avg_prediction > 0.6:
                            signal_class = "signal-buy"
                            signal_text = "🟢 BUY SIGNAL"
                        elif avg_prediction < 0.4:
                            signal_class = "signal-sell"
                            signal_text = "🔴 SELL SIGNAL"
                        else:
                            signal_class = "signal-neutral"
                            signal_text = "🟡 NEUTRAL"
                        
                        st.markdown(f"""
                        <div class="{signal_class}">
                            <h4>{signal_text}</h4>
                            <p>Probability: {avg_prediction:.3f}</p>
                            <p>Confidence: {confidence:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Individual model predictions
                        st.write("**Individual Model Predictions:**")
                        for model, pred in predictions.items():
                            st.write(f"- {model}: {pred:.3f}")
                    
                    with col2:
                        # ML prediction chart
                        ml_chart = create_ml_prediction_chart(predictions)
                        if ml_chart:
                            st.plotly_chart(ml_chart, use_container_width=True)
                else:
                    st.warning("ML predictions not available. Please train models first.")
                
                # Generate signals
                st.subheader("📊 Trading Signals & Analysis")
                
                try:
                    # Update config temporarily for selected mode
                    temp_config = config.copy()
                    temp_config['signals']['mode'] = selected_mode
                    
                    with open('temp_config.json', 'w') as f:
                        json.dump(temp_config, f)
                    
                    # Generate signals
                    signal_generator = MLSignalGenerator('temp_config.json')
                    signals = signal_generator.generate_signals({selected_stock: indicators_data})
                    
                    # Clean up temp config
                    import os
                    if os.path.exists('temp_config.json'):
                        os.remove('temp_config.json')
                    
                    stock_signals = signals.get(selected_stock, [])
                    
                    # Price chart with signals
                    price_chart = create_price_chart(indicators_data, stock_signals)
                    st.plotly_chart(price_chart, use_container_width=True)
                    
                    # Recent signals
                    if stock_signals:
                        st.subheader("📋 Recent Trading Signals")
                        
                        # Show last 10 signals
                        recent_signals = stock_signals[-10:]
                        
                        signal_df = pd.DataFrame([{
                            'Date': s['date'],
                            'Type': s['type'],
                            'Price': f"₹{s['price']:.2f}",
                            'Reason': s['reason'][:100] + "..." if len(s['reason']) > 100 else s['reason']
                        } for s in recent_signals])
                        
                        st.dataframe(signal_df, use_container_width=True)
                    else:
                        st.info("No trading signals generated for the selected period.")
                    
                    # Backtest results
                    if stock_signals:
                        st.subheader("📈 Backtest Performance")
                        
                        with st.spinner("Running backtest..."):
                            backtester = Backtester()
                            backtest_results = backtester._backtest_stock(
                                selected_stock, indicators_data, stock_signals
                            )
                        
                        if backtest_results:
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Trades", backtest_results['total_trades'])
                            
                            with col2:
                                st.metric("Win Rate", f"{backtest_results['win_rate']:.1f}%")
                            
                            with col3:
                                st.metric("Total P&L", f"₹{backtest_results['total_pnl']:.2f}")
                            
                            with col4:
                                st.metric("Sharpe Ratio", f"{backtest_results['sharpe_ratio']:.2f}")
                            
                            # Cumulative returns chart
                            if backtest_results['cumulative_returns']:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=list(range(1, len(backtest_results['cumulative_returns']) + 1)),
                                    y=backtest_results['cumulative_returns'],
                                    mode='lines+markers',
                                    name='Cumulative P&L'
                                ))
                                
                                fig.update_layout(
                                    title="Cumulative P&L Over Time",
                                    xaxis_title="Trade Number",
                                    yaxis_title="Cumulative P&L (₹)",
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error generating signals: {str(e)}")
            
            else:
                st.error("Failed to calculate technical indicators")
        else:
            st.error(f"Failed to fetch data for {selected_stock}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>NIFTY 50 ML Trading Dashboard | Built with Streamlit</p>
        <p><small>⚠️ This is for educational purposes only. Not financial advice.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()