import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

class EnhancedWaveTransitionAnalyzer:
    def __init__(self, prices_df, trend_df, stocks_info):
        self.prices_df = prices_df
        self.trend_df = trend_df
        self.stocks_info = stocks_info
        
    def _calculate_technical_indicators(self, df):
        df = df.sort_values('Date').copy()
        
        # 이동평균선
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # 52주 고점/저점 (250 영업일 기준)
        df['High_52w'] = df['Close'].rolling(window=250, min_periods=100).max()
        df['Low_52w'] = df['Close'].rolling(window=250, min_periods=100).min()
        
        # 52주 위치 퍼센트 (100 = 최고가, 0 = 최저가)
        df['Pos_52w'] = (df['Close'] - df['Low_52w']) / (df['High_52w'] - df['Low_52w']).replace(0, np.nan) * 100
        
        # 거래량 증가율
        df['Vol_5d'] = df['Volume'].rolling(window=5).mean()
        df['Vol_20d'] = df['Volume'].shift(5).rolling(window=20).mean()
        df['Vol_Ratio'] = df['Vol_5d'] / df['Vol_20d'].replace(0, np.nan)
        
        # RSI 14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 최근 20일 수익률
        df['Return_20d'] = df['Close'].pct_change(periods=20) * 100
        
        return df
        
    def _calculate_wave_score(self, row):
        if pd.isna(row['MA200']) or pd.isna(row['MA50']) or pd.isna(row['MA20']):
            return 0, "Data Insufficient"
            
        c = row['Close']
        m20, m50, m200 = row['MA20'], row['MA50'], row['MA200']
        pos52 = row['Pos_52w']
        vol_ratio = row['Vol_Ratio']
        rsi = row['RSI']
        ret20 = row['Return_20d']
        
        # 안전장치 (nan 처리)
        pos52 = 0 if pd.isna(pos52) else pos52
        vol_ratio = 1 if pd.isna(vol_ratio) else vol_ratio
        rsi = 50 if pd.isna(rsi) else rsi
        ret20 = 0 if pd.isna(ret20) else ret20
        
        # 1. 2단계 중기 (90점)
        if (m20 > m50 > m200) and (60 <= pos52 <= 95) and (vol_ratio >= 1.3) and (55 <= rsi <= 75) and (ret20 >= 10):
            return 90, "Stage 2 (Strong Uptrend)"
            
        # 2. 2단계 초기 (80점)
        if (m20 > m50) and (c > m20) and (40 <= pos52 <= 80) and (vol_ratio >= 1.2):
            return 80, "Stage 2 (Early Uptrend)"
            
        # 3. 전환기 (70점) - MA20과 MA50의 수렴
        dist_20_50 = abs(m20 - m50) / m50
        if dist_20_50 < 0.05 and (25 <= pos52 <= 65) and (45 <= rsi <= 65) and c >= m20:
            return 70, "Transition to Stage 2"
            
        # 4. 일반 상승 추세 (60점)
        if m20 > m50 and (30 <= pos52 <= 80):
            return 60, "General Uptrend"
            
        return 20, "Down/Sideways"
        
    def calculate_final_investment_scores(self):
        results = []
        
        grouped_prices = self.prices_df.groupby('Ticker')
        
        for ticker, group in grouped_prices:
            df = group.copy()
            df = self._calculate_technical_indicators(df)
            
            # 최소 데이터 길이 확인
            if len(df) < 50:
                continue
                
            last_row = df.iloc[-1]
            wave_score, wave_stage = self._calculate_wave_score(last_row)
            
            # 수급 점수 계산
            supply_score = 0
            if not self.trend_df.empty and ticker in self.trend_df['Ticker'].values:
                t_df = self.trend_df[self.trend_df['Ticker'] == ticker].sort_values('Date').tail(10)
                inst_sum = t_df['Institution_Net'].sum()
                for_sum = t_df['Foreigner_Net'].sum()
                
                if inst_sum > 0 and for_sum > 0:
                    supply_score = 10
                elif inst_sum > 0 or for_sum > 0:
                    supply_score = 5
                elif inst_sum < 0 and for_sum < 0:
                    supply_score = -5
            
            final_score = wave_score + supply_score
            
            results.append({
                'Ticker': ticker,
                'Name': self.stocks_info.get(ticker, ticker),
                'Date': last_row['Date'],
                'Close': last_row['Close'],
                'Wave_Score': wave_score,
                'Supply_Score': supply_score,
                'Total_Score': final_score,
                'Stage': wave_stage,
                'MA20': last_row['MA20'],
                'MA50': last_row['MA50'],
                'MA200': last_row['MA200'],
                'Pos_52w': last_row['Pos_52w'],
                'RSI': last_row['RSI'],
                'Vol_Ratio': last_row['Vol_Ratio']
            })
            
        res_df = pd.DataFrame(results)
        if not res_df.empty:
            res_df = res_df.sort_values(['Total_Score', 'Wave_Score'], ascending=[False, False])
        return res_df

def main():
    print("파동 분석 및 투자 등급 산출 시작...")
    
    if not os.path.exists('daily_prices.csv'):
        print("에러: daily_prices.csv 파일이 없습니다.")
        return
        
    prices_df = pd.read_csv('daily_prices.csv')
    prices_df['Date'] = pd.to_datetime(prices_df['Date'])
    prices_df['Ticker'] = prices_df['Ticker'].astype(str).str.zfill(6)
    
    trend_df = pd.DataFrame()
    if os.path.exists('all_institutional_trend_data.csv'):
        trend_df = pd.read_csv('all_institutional_trend_data.csv')
        trend_df['Date'] = pd.to_datetime(trend_df['Date'])
        trend_df['Ticker'] = trend_df['Ticker'].astype(str).str.zfill(6)
        
    stocks_info = {}
    if os.path.exists('korean_stocks_list.csv'):
        sdf = pd.read_csv('korean_stocks_list.csv', dtype=str)
        stocks_info = dict(zip(sdf['ticker'].str.zfill(6), sdf['name']))
        
    analyzer = EnhancedWaveTransitionAnalyzer(prices_df, trend_df, stocks_info)
    results_df = analyzer.calculate_final_investment_scores()
    
    if not results_df.empty:
        results_df.to_csv('wave_transition_analysis_results.csv', index=False)
        print("분석 완료: wave_transition_analysis_results.csv")
        print("상위 3개 종목:")
        print(results_df[['Ticker', 'Name', 'Total_Score', 'Stage']].head(3))
    else:
        print("분석 결과가 없습니다.")

if __name__ == "__main__":
    main()
