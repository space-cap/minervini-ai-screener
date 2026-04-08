import os
import pandas as pd
from duckduckgo_search import DDGS
from newspaper import Article
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import time

load_dotenv()

# Select LLM client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

use_openai = False
if OPENAI_API_KEY:
    use_openai = True
    client = OpenAI(api_key=OPENAI_API_KEY)
elif GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    print("Warning: No OpenAI or Gemini API key found. AI analysis will not work.")

def search_news_duckduckgo(query, max_results=3):
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, region="kr-kr", safesearch="off", timelimit="m", max_results=max_results):
                results.append(r)
    except Exception as e:
        print(f"DuckDuckGo Search error: {e}")
    return results

def fetch_article_text(url):
    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()
        text = article.text
        return text[:2000] # Limit length
    except Exception as e:
        print(f"Newspaper3k error {url}: {e}")
        return ""

def generate_ai_report(ticker, name, score, stage, articles):
    context = ""
    for idx, article in enumerate(articles):
        context += f"\n[뉴스 {idx+1}] 제목: {article['title']}\n요약: {article['body']}\n본문: {article['text']}\n"
        
    prompt = f"""
당신은 한국 주식 시장의 전문 애널리스트입니다.
아래는 기술적/수급 분석을 통해 발굴한 종목 '{name}({ticker})'의 정보와 최근 관련 뉴스입니다.

- 기술적/수급 총합 점수: {score}점
- 기술적 판정 단계: {stage}

최근 뉴스 전문/요약 정보:
{context}

이 종목에 대해 투자자가 참고할 수 있는 리포트를 작성해 주세요.
반드시 마크다운 형식으로 작성하고, 다음 내용을 포함해 주세요:
1. 종목 핫이슈 (뉴스를 기반으로 한 상승/하락 모멘텀 및 핵심 이슈)
2. 현재 기술적 위치 (점수와 단계를 언급하며)
3. 향후 1~2주 단기적인 매수/매도/관망 의견 및 그 이유

짧고 간결하면서 투자자에게 실질적 도움이 될 수 있게 3~4문단 이내로 요약해 주십시오.
"""

    try:
        if use_openai:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            return response.choices[0].message.content
        elif GOOGLE_API_KEY:
            response = model.generate_content(prompt)
            return response.text
        else:
            return "API Key가 없어 리포트를 생성할 수 없습니다."
    except Exception as e:
        return f"AI 생성 중 오류가 발생했습니다: {e}"

def main():
    print("AI 뉴스 분석 및 리포트 작성 시작...")
    
    if not os.path.exists('wave_transition_analysis_results.csv'):
        print("분석 결과 파일(wave_transition_analysis_results.csv)이 없습니다.")
        return
        
    df = pd.read_csv('wave_transition_analysis_results.csv')
    df['Ticker'] = df['Ticker'].astype(str).str.zfill(6)
    
    # 상위 5개 종목 대상
    top_stocks = df.head(5)
    
    for idx, row in top_stocks.iterrows():
        ticker = row['Ticker']
        name = row['Name']
        score = row['Total_Score']
        stage = row['Stage']
        
        print(f"\n[{name}] 뉴스 검색 중...")
        news_results = search_news_duckduckgo(f"{name} 주가", max_results=3)
        
        articles_data = []
        for n in news_results:
            text = fetch_article_text(n.get('url', ''))
            articles_data.append({
                'title': n.get('title', ''),
                'body': n.get('body', ''),
                'text': text
            })
            
        print(f"[{name}] 리포트 생성 중...")
        report_text = generate_ai_report(ticker, name, score, stage, articles_data)
        
        report_filename = f'ai_analysis_report_{ticker}.md'
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 {name} ({ticker}) AI 분석 리포트\n\n")
            f.write(report_text)
            
        print(f"[{name}] 리포트 저장 완료: {report_filename}")
        time.sleep(2) # API Rate limit 방지

if __name__ == "__main__":
    main()
