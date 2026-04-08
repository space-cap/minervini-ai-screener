import subprocess
import sys
import time

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"🚀 실행 중: {script_name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        # Use sys.executable to run with the current environment's Python
        result = subprocess.run([sys.executable, script_name], check=True, text=True)
        elapsed_time = time.time() - start_time
        print(f"✅ {script_name} 완료 (소요 시간: {elapsed_time:.2f}초)")
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} 실행 중 오류 발생: {e}")
        sys.exit(1)

def main():
    print("🌟 StockAI 전체 파이프라인 실행 시작 🌟")
    total_start = time.time()
    
    # 1. 시세 데이터 수집
    run_script("create_complete_daily_prices.py")
    
    # 2. 투자자별 수급 데이터 수집
    run_script("all_institutional_trend_data.py")
    
    # 3. 파동 및 수급 분석 (점수 산출)
    run_script("analysis2.py")
    
    # 4. 상위 종목 AI 리포트 생성
    run_script("investigate_top_stocks.py")
    
    total_elapsed = time.time() - total_start
    print(f"\n🎉 전체 파이프라인 무사통과 완료! (총 소요 시간: {total_elapsed:.2f}초)")
    print("대시보드를 확인하려면 다음 명령어를 입력하세요:")
    print("   uv run streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()
