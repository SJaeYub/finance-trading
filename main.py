import yfinance as yf
import pandas as pd
import requests
import urllib3

# SSL 경고 메시지 숨기기 (깔끔한 출력을 위해)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_futures_daily_data():
    tickers = {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Crude Oil': 'CL=F'
    }

    print("--- [일봉] 선물 가격 데이터 수집 시작 (SSL 우회 적용) ---\n")
    
    # 1. SSL 인증서 검증을 끄는 세션 생성
    session = requests.Session()
    session.verify = False  # 핵심: 보안 인증서 검사 비활성화
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    })

    all_data = []

    for name, ticker_symbol in tickers.items():
        try:
            # 2. yfinance에 우리가 만든 세션(SSL 끈 것)을 전달
            ticker = yf.Ticker(ticker_symbol, session=session)
            
            # 3. 일봉 데이터 가져오기
            # period='1y' (1년치), 'max' (전체), '1mo' (1달)
            # interval='1d' (일봉)
            df = ticker.history(period='1y', interval='1d')
            
            if not df.empty:
                # 날짜가 인덱스로 되어있으므로 컬럼으로 뺌
                df = df.reset_index()
                
                # 어떤 상품인지 구분하기 위해 컬럼 추가
                df['Symbol'] = name
                
                # 필요한 컬럼만 정리 (날짜, 시가, 고가, 저가, 종가, 거래량, 상품명)
                # yfinance 버전에 따라 날짜 컬럼명이 'Date' 또는 'Datetime'일 수 있음
                cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']
                # 데이터에 있는 컬럼만 선택 (Volume이 없는 경우 방지)
                available_cols = [c for c in cols if c in df.columns]
                df = df[available_cols]
                
                # 날짜 형식 깔끔하게 변경 (YYYY-MM-DD)
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                
                all_data.append(df)
                print(f"[{name}] {len(df)}일치 데이터 수집 완료")
            else:
                print(f"[{name}] 데이터가 없습니다.")

        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # 4. 모든 데이터를 하나의 표(DataFrame)로 합치기
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    result = get_futures_daily_data()
    
    if not result.empty:
        print("\n--- 수집 결과 (상위 5개) ---")
        print(result.head())
        print("\n--- 수집 결과 (하위 5개) ---")
        print(result.tail())
        
        # 엑셀로 저장하고 싶으면 아래 주석 해제
        # result.to_excel("futures_daily_data.xlsx", index=False)
        # print("\n엑셀 파일로 저장되었습니다.")
    else:
        print("데이터를 가져오지 못했습니다.")
