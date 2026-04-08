import pandas as pd
import plotly.graph_objects as go
import os

def load_data():
    prices_df = pd.DataFrame()
    trend_df = pd.DataFrame()
    results_df = pd.DataFrame()
    
    if os.path.exists('daily_prices.csv'):
        prices_df = pd.read_csv('daily_prices.csv')
        prices_df['Date'] = pd.to_datetime(prices_df['Date'])
        prices_df['Ticker'] = prices_df['Ticker'].astype(str).str.zfill(6)
        
    if os.path.exists('all_institutional_trend_data.csv'):
        trend_df = pd.read_csv('all_institutional_trend_data.csv')
        trend_df['Date'] = pd.to_datetime(trend_df['Date'])
        trend_df['Ticker'] = trend_df['Ticker'].astype(str).str.zfill(6)
        
    if os.path.exists('wave_transition_analysis_results.csv'):
        results_df = pd.read_csv('wave_transition_analysis_results.csv')
        results_df['Ticker'] = results_df['Ticker'].astype(str).str.zfill(6)
        
    return prices_df, trend_df, results_df

def create_candlestick_chart(ticker, prices_df):
    df = prices_df[prices_df['Ticker'] == ticker].sort_values('Date').copy()
    if df.empty:
        return None
        
    # 이동평균선
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # 봉 차트 자르기 (최근 100일)
    df = df.tail(100)
    
    fig = go.Figure()
    
    # 캔들스틱 추가
    fig.add_trace(go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='주가',
        increasing_line_color='red', decreasing_line_color='blue'
    ))
    
    # 이평선 추가
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], line=dict(color='orange', width=2), name='20일선'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], line=dict(color='green', width=2), name='50일선'))
    
    fig.update_layout(
        title=f"{ticker} 최근 주가 흐름",
        yaxis_title="가격",
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def read_markdown_report(ticker):
    filename = f"ai_analysis_report_{ticker}.md"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return "해당 종목의 AI 분석 리포트가 존재하지 않습니다."
