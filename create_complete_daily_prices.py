import pandas as pd
import requests
from tqdm import tqdm
import time
import os

def fetch_daily_prices_naver(ticker, pages=20):
    url = f'https://finance.naver.com/item/sise_day.naver?code={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    df_list = []
    # page당 10일치, 25페이지 = 최소 250일치(약 1년) 데이터
    import io
    for page in range(1, pages + 1):
        res = requests.get(f'{url}&page={page}', headers=headers)
        if res.status_code == 200:
            df = pd.read_html(io.StringIO(res.text))[0]
            df = df.dropna()
            df_list.append(df)
        time.sleep(0.1)  # 네이버 차단 회피용 딜레이
        
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, ignore_index=True)
    
    combined_df = combined_df.rename(columns={
        '날짜': 'Date',
        '종가': 'Close',
        '시가': 'Open',
        '고가': 'High',
        '저가': 'Low',
        '거래량': 'Volume'
    })
    
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    for col in ['Close', 'Open', 'High', 'Low', 'Volume']:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        
    combined_df['Ticker'] = ticker
    combined_df = combined_df.sort_values('Date', ascending=True).reset_index(drop=True)
    return combined_df

def main():
    print("일별 주가 데이터 수집 시작...")
    
    if not os.path.exists('korean_stocks_list.csv'):
        print("korean_stocks_list.csv 파일이 없습니다. 종목 리스트를 생성해 주세요.")
        return
        
    stocks = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
    
    all_data = []
    for idx, row in tqdm(stocks.iterrows(), total=len(stocks)):
        ticker = row['ticker'].strip().zfill(6)
        df = fetch_daily_prices_naver(ticker, pages=25)
        if not df.empty:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('daily_prices.csv', index=False)
        print("데이터 저장 완료: daily_prices.csv")
    else:
        print("데이터를 수집하지 못했습니다.")

if __name__ == "__main__":
    main()
