import pandas as pd
import requests
from tqdm import tqdm
import time
import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')
load_dotenv()
DATA_SOURCE = os.getenv("DATA_SOURCE", "NAVER")

def fetch_investor_trend_naver(ticker, pages=10):
    url = f'https://finance.naver.com/item/frgn.naver?code={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    df_list = []
    # page당 20일치, 12페이지 = 최소 240일치 데이터
    import io
    for page in range(1, pages + 1):
        res = requests.get(f'{url}&page={page}', headers=headers)
        if res.status_code == 200:
            tables = pd.read_html(io.StringIO(res.text))
            if len(tables) > 2:
                for idx_t in range(2, len(tables)):
                    df = tables[idx_t]
                    # 테이블 조건 체크 (멀티인덱스 컬럼 등이 있는지)
                    if not df.empty and len(df.columns) >= 7:
                        df = df.dropna(subset=[df.columns[0]])
                        df_list.append(df)
                        break
        time.sleep(0.1)
        
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # 멀티인덱스 처리
    if isinstance(combined_df.columns, pd.MultiIndex):
        combined_df.columns = [col[0] if col[0] == col[1] else f"{col[0]}_{col[1]}" for col in combined_df.columns]
    
    # 컬럼 매핑
    cols = combined_df.columns
    rename_dict = {}
    for c in cols:
        str_c = str(c)
        if '날짜' in str_c: rename_dict[c] = 'Date'
        elif '기관' in str_c and '순매매' in str_c: rename_dict[c] = 'Institution_Net'
        elif '외국인' in str_c and '순매매' in str_c: rename_dict[c] = 'Foreigner_Net'
        
    combined_df = combined_df.rename(columns=rename_dict)
    
    for required in ['Date', 'Institution_Net', 'Foreigner_Net']:
        if required not in combined_df.columns:
            combined_df[required] = 0
            
    res_df = combined_df[['Date', 'Institution_Net', 'Foreigner_Net']].copy()
    res_df['Ticker'] = ticker
    
    res_df['Date'] = pd.to_datetime(res_df['Date'], errors='coerce')
    res_df['Institution_Net'] = pd.to_numeric(res_df['Institution_Net'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    res_df['Foreigner_Net'] = pd.to_numeric(res_df['Foreigner_Net'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    res_df = res_df.dropna(subset=['Date'])
    res_df = res_df.sort_values('Date', ascending=True).reset_index(drop=True)
    return res_df

def fetch_investor_trend_pykrx(ticker, days=240):
    try:
        from pykrx import stock
        from datetime import datetime, timedelta
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days*1.5)
        
        # pykrx 순매수 동향 (기관합계, 외국인)
        df = stock.get_market_trading_volume_by_date(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"), ticker, on="순매수")
        if df.empty:
            return pd.DataFrame()
            
        df = df.reset_index()
        
        # 리네임
        rename_dict = {
            '날짜': 'Date',
            '기관합계': 'Institution_Net',
            '외국인': 'Foreigner_Net'
        }
        df = df.rename(columns=rename_dict)
        
        for required in ['Date', 'Institution_Net', 'Foreigner_Net']:
            if required not in df.columns:
                df[required] = 0
                
        res_df = df[['Date', 'Institution_Net', 'Foreigner_Net']].copy()
        res_df['Ticker'] = ticker
        
        res_df['Date'] = pd.to_datetime(res_df['Date'], errors='coerce')
        res_df = res_df.dropna(subset=['Date'])
        res_df = res_df.sort_values('Date', ascending=True).reset_index(drop=True)
        return res_df.tail(days)
    except ImportError:
        print("pykrx가 설치되어 있지 않습니다.")
        return pd.DataFrame()
    except Exception as e:
        print(f"pykrx 에러 ({ticker}): {e}")
        return pd.DataFrame()

def main():
    print("기관/외국인 수급 데이터 수집 시작...")
    if not os.path.exists('korean_stocks_list.csv'):
        print("korean_stocks_list.csv 파일이 없습니다.")
        return
        
    stocks = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
    
    all_data = []
    print(f"[{DATA_SOURCE} 모드] 데이터 수집을 시작합니다.")
    for idx, row in tqdm(stocks.iterrows(), total=len(stocks)):
        ticker = row['ticker'].strip().zfill(6)
        
        if DATA_SOURCE == 'PYKRX':
            df = fetch_investor_trend_pykrx(ticker, days=240)
            time.sleep(0.5)
        else:
            df = fetch_investor_trend_naver(ticker, pages=13)
            
        if not df.empty:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('all_institutional_trend_data.csv', index=False)
        print("데이터 저장 완료: all_institutional_trend_data.csv")
    else:
        print("데이터를 수집하지 못했습니다.")

if __name__ == "__main__":
    main()
