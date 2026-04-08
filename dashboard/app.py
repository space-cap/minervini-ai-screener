import streamlit as st
import pandas as pd
from utils import load_data, create_candlestick_chart, read_markdown_report

st.set_page_config(page_title="StockAI", page_icon="📈", layout="wide")

def main():
    st.title("🥝 StockAI: Intelligent Korean Stock Analysis System")
    st.markdown("매일 갱신되는 데이터를 기반으로 최적의 투자 종목을 탐색합니다.")
    
    # 데이터 로드
    prices_df, trend_df, results_df = load_data()
    
    if results_df.empty:
        st.warning("분석 결과 데이터가 없습니다. `run_analysis.py`를 먼저 실행해주세요.")
        return
        
    st.sidebar.header("📊 StockAI Menu")
    menu = st.sidebar.radio("원하시는 메뉴를 선택하세요:", ["투자 요약 대시보드", "종목별 상승 파동 분석", "AI 투자 리포트"])
    
    if menu == "투자 요약 대시보드":
        st.subheader("🔥 오늘의 Top 추천 종목")
        
        # 상위 5종목 하이라이트
        top_stocks_disp = results_df.head(5)
        cols = st.columns(5)
        for i, (idx, row) in enumerate(top_stocks_disp.iterrows()):
            with cols[i]:
                st.metric(label=f"🏆 {i+1}위: {row['Name']}", value=f"{int(row['Total_Score'])}점", delta=row['Stage'])
                st.caption(f"종가: {row['Close']:,.0f}원")
                
        st.divider()
        st.subheader("📋 전체 파동 분석 결과표")
        st.dataframe(
            results_df[['Ticker', 'Name', 'Total_Score', 'Wave_Score', 'Supply_Score', 'Stage', 'Close']],
            use_container_width=True,
            hide_index=True
        )
        
    elif menu == "종목별 상승 파동 분석":
        st.subheader("📈 종목 차트 및 수급 분석")
        
        target_stock = st.selectbox("종목을 선택하세요:", results_df['Name'].tolist())
        ticker = results_df[results_df['Name'] == target_stock]['Ticker'].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = create_candlestick_chart(ticker, prices_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("차트 데이터가 없습니다.")
                
        with col2:
            st.write("### 기술적/수급 점수")
            stock_info = results_df[results_df['Ticker'] == ticker].iloc[0]
            st.metric("총합 투자 점수", f"{stock_info['Total_Score']}점")
            st.metric("파동 점수", f"{stock_info['Wave_Score']}점")
            st.metric("현재 단계", stock_info['Stage'])
            st.metric("52주 고점대비 위치", f"{stock_info['Pos_52w']:.1f}%")
            
    elif menu == "AI 투자 리포트":
        st.subheader("🤖 AI 기반 뉴스 심층 분석")
        st.info("파동 분석 상위 종목에 대한 최신 뉴스 요약 및 AI 투자 의견입니다.")
        
        # 상위 종목 목록
        top_stocks_ai = results_df.head(5)
        selected_ai_stock = st.selectbox("분석 리포트가 생성된 종목:", top_stocks_ai['Name'].tolist())
        ticker = top_stocks_ai[top_stocks_ai['Name'] == selected_ai_stock]['Ticker'].iloc[0]
        
        report = read_markdown_report(ticker)
        with st.expander(f"{selected_ai_stock} AI 리포트 보기", expanded=True):
            st.markdown(report)

if __name__ == "__main__":
    main()
