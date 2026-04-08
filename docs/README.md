# 🥝 StockAI: Intelligent Korean Stock Analysis System

**StockAI**는 한국 주식 시장을 위한 **올인원 자동 분석 및 투자 지원 시스템**입니다.
기술적 분석(파동 이론), 수급 분석(기관/외국인), 그리고 **Generative AI(Gemini)** 기반의 뉴스 분석을 결합하여 최적의 투자 기회를 발굴합니다.

---

## � 목차 (Table of Contents)
1.  [프로젝트 소개](#-프로젝트-소개)
2.  [설치 및 설정](#-설치-및-설정-installation)
3.  [시스템 구조](#-시스템-구조-architecture)
4.  [사용 방법](#-사용-방법-usage)
5.  [개발자 가이드](#-개발자-가이드-developer-guide)
6.  [트러블슈팅](#-트러블슈팅-troubleshooting)

---

## 🚀 프로젝트 소개

이 프로젝트는 개인 투자자가 시장의 소음을 걸러내고 데이터에 기반한 의사결정을 내릴 수 있도록 돕기 위해 개발되었습니다.

*   **핵심 철학**: "가격은 모든 것을 반영한다(Price Discounts Everything)" + "수급은 재료에 우선한다"
*   **주요 기능**:
    *   **자동화된 데이터 파이프라인**: 매일 장 마감 후 클릭 한 번으로 전 종목 데이터 수집 및 분석.
    *   **파동 전환 알고리즘**: 하락 추세에서 상승 추세로 전환되는 '변곡점' 포착.
    *   **AI 애널리스트**: Gemini Pro가 수집된 종목의 뉴스를 분석하여 '매수/매도' 의견 제시.
    *   **인터랙티브 대시보드**: 웹 기반(Streamlit)의 시각화 도구 제공.

---

## 🛠 설치 및 설정 (Installation)

### 1. 필수 요구사항 (Prerequisites)
*   Python 3.13 이상
*   Google Gemini API Key 또는 OpenAI API Key (취향에 맞게 선택)
*   `uv` 패키지 관리자 (참고: [uv 공식 문서](https://docs.astral.sh/uv/getting-started/installation/))

### 2. 라이브러리 설치
`uv`를 사용하여 프로젝트를 초기화하고 실행에 필요한 패키지들을 추가합니다.
```bash
# Python 3.13 버전으로 프로젝트 초기화 (pyproject.toml 생성)
uv init --python 3.13

# 필수 패키지 설치 (자동으로 가상 환경(.venv)이 구성되고 패키지가 추가됩니다)
uv add pandas numpy requests tqdm python-dotenv plotly streamlit google-generativeai openai duckduckgo-search newspaper3k lxml_html_clean
```

### 3. 환경 변수 설정 (.env)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 사용할 AI 모델에 맞춰 내용을 입력하세요. (둘 다 입력해도 무방합니다)
```ini
# Google Gemini를 사용할 경우
GOOGLE_API_KEY=your_gemini_api_key_here

# OpenAI(ChatGPT)를 사용할 경우
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 종목 리스트 준비
`korean_stocks_list.csv` 파일이 루트 디렉토리에 있어야 합니다. (형식: `ticker,name` 컬럼 필수)

---

## 🏗 시스템 구조 (Architecture)

### 디렉토리 구조
```
📦 StockAI
 ┣ 📂 dashboard              # 대시보드 관련 코드
 ┃ ┣ 📜 app.py              # [메인] Streamlit 대시보드 실행 파일
 ┃ ┗ 📜 utils.py            # 대시보드 유틸리티 함수
 ┣ 📜 run_analysis.py        # [메인] 전체 분석 파이프라인 실행 스크립트
 ┣ 📜 create_complete_daily_prices.py  # 일별 시세 수집 (네이버 금융)
 ┣ 📜 all_institutional_trend_data.py  # 기관/외국인 수급 분석
 ┣ 📜 analysis2.py           # 파동 분석 및 투자 등급 산출 엔진
 ┣ 📜 investigate_top_stocks.py # AI 뉴스 심층 분석
 ┣ 📜 daily_prices.csv       # [Data] 수집된 일별 시세 (증분 저장)
 ┣ 📜 wave_transition_analysis_results.csv # [Data] 최종 분석 결과
 ┗ 📜 ai_analysis_report_*.md # [Report] 생성된 AI 리포트
```

### 데이터 파이프라인 흐름
1.  **Data Collection**: `create_complete_daily_prices.py`가 네이버 금융 크롤링 → `daily_prices.csv` 저장.
2.  **Trend Analysis**: `all_institutional_trend_data.py`가 수급 데이터 분석 → `all_institutional_trend_data.csv` 저장.
3.  **Core Analysis**: `analysis2.py`가 위 두 데이터를 결합하여 파동 분석 수행 → `wave_transition_analysis_results.csv` 생성.
4.  **AI Insight**: `investigate_top_stocks.py`가 상위 종목 뉴스 검색 및 LLM 분석 → `.md` 리포트 생성.
5.  **Visualization**: `dashboard/app.py`가 결과 데이터를 시각화.

---

## 🌊 파동 분석 방법론 (Wave Analysis Methodology)

StockAI의 핵심 엔진인 `analysis2.py`는 주가 파동의 단계를 4가지로 분류하여 점수를 산출합니다.

### 1. 2단계 중기 (Strong Uptrend) - 90점
가장 강력한 상승 추세 구간입니다.
*   **이동평균선**: 정배열 (20일 > 50일 > 200일)
*   **52주 위치**: 60% ~ 90% (신고가 근처)
*   **거래량**: 평소 대비 1.3배 이상 급증
*   **RSI**: 55 ~ 75 (과열되지 않은 강세)
*   **수익률**: 최근 20일간 10% 이상 상승

### 2. 2단계 초기 (Early Uptrend) - 80점
상승 추세가 막 시작되는 구간으로, 가장 이상적인 진입 시점 중 하나입니다.
*   **이동평균선**: 20일선이 50일선 위에 위치 (골든크로스 이후)
*   **52주 위치**: 40% ~ 75%
*   **가격**: 20일 이동평균선 지지
*   **거래량**: 평소 대비 1.2배 이상 증가

### 3. 1단계 → 2단계 전환 (Transition) - 70점
바닥을 다지고 상승으로 전환하려는 시도 구간입니다.
*   **이동평균선**: 20일선과 50일선이 수렴하거나 교차 직전
*   **52주 위치**: 25% ~ 60% (바닥권 탈출 시도)
*   **가격**: 20일선 근처에서 횡보 또는 소폭 상승
*   **RSI**: 45 ~ 65 (중립 이상)

### 4. 일반 상승 추세 (General Uptrend) - 60점
기본적인 상승 흐름을 유지하고 있는 상태입니다.
*   **이동평균선**: 20일선 > 50일선
*   **52주 위치**: 30% ~ 70%
*   **거래량**: 평소의 80% 수준 유지

> **참고**: 최종 투자 점수는 위 파동 점수에 **펀더멘털(PER, PBR, ROE)** 및 **수급(기관/외국인 매집)** 점수를 가중 합산하여 결정됩니다.

---

## 💻 사용 방법 (Usage)

### 1. 매일 장 마감 후 분석 실행
터미널에서 아래 명령어를 실행하면 모든 과정이 자동으로 진행됩니다.
```bash
uv run run_analysis.py
```
> **소요 시간**: 약 3~5분 (네이버 서버 응답 속도에 따라 상이)

### 2. 대시보드 실행
분석이 완료되면 대시보드를 띄워 결과를 확인합니다.
```bash
uv run streamlit run dashboard/app.py
```
*   브라우저가 자동으로 열리며 `http://localhost:8501`로 접속됩니다.

---

## �‍💻 개발자 가이드 (Developer Guide)

새로운 기능을 추가하고 싶은 개발자를 위한 가이드입니다.

### Q: 새로운 보조지표를 추가하고 싶다면?
1.  `analysis2.py` 파일을 엽니다.
2.  `EnhancedWaveTransitionAnalyzerV3` 클래스 내의 `_calculate_technical_indicators` 메서드를 찾습니다.
3.  해당 메서드 안에 새로운 지표 계산 로직(예: Bollinger Bands)을 추가합니다.
4.  `calculate_final_investment_scores` 메서드에서 해당 지표를 점수 산출 로직에 반영합니다.

### Q: AI 분석 프롬프트를 수정하거나 모델을 변경하고 싶다면?
1.  `investigate_top_stocks.py` 파일을 엽니다.
2.  프롬프트 수정: 실행 함수 내의 `prompt` 변수를 찾아 원하는 지시사항을 추가하세요.
3.  모델 변경: 개발자 본인의 취향 및 설정에 맞춰 코드 내의 API 호출 객체를 OpenAI 혹은 Gemini로 수정 및 전환하여 사용할 수 있습니다.

### Q: 대시보드에 새로운 탭을 만들고 싶다면?
1.  `dashboard/app.py`를 엽니다.
2.  `main()` 함수의 `menu_labels` 딕셔너리에 새 메뉴를 추가합니다.
3.  `render_new_tab()` 같은 함수를 새로 만들고, `main()` 함수의 조건문(`if page == ...`)에 연결합니다.

---

## ❓ 트러블슈팅 (Troubleshooting)

**Q. `KeyError: 'open'` 오류가 발생해요.**
*   A. `daily_prices.csv`의 컬럼명이 변경되었을 수 있습니다. `create_complete_daily_prices.py`를 실행하여 데이터를 다시 수집해 보세요.

**Q. AI 분석이 실행되지 않아요.**
*   A. `.env` 파일에 사용 중인 모델의 API 키(`GOOGLE_API_KEY` 또는 `OPENAI_API_KEY`)가 올바르게 설정되어 있는지 확인하세요. API 키가 만료되었거나 할당량/크레딧이 초과되었을 수 있습니다.

**Q. 대시보드 차트가 안 보여요.**
*   A. 데이터 파일(`daily_prices.csv`)이 비어있거나 손상되었을 수 있습니다. `run_analysis.py`를 다시 실행하여 데이터를 복구하세요.

---
*Created by Antigravity Agent*
