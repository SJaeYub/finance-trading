import yfinance as yf
import pandas as pd
from curl_cffi import requests as curl_requests
import os

def get_futures_data(interval='1d', period='1y', verify_ssl=True, use_proxy=True):
    """
    선물 가격 데이터를 수집하는 함수

    Parameters:
    -----------
    interval : str
        데이터 수집 단위
        - '1m', '2m', '5m', '15m', '30m' (분봉)
        - '1h' (1시간봉)
        - '1d' (1일봉, 기본값)
        - '1wk' (주봉)
        - '1mo' (월봉)

    period : str
        데이터 수집 기간
        - '1d', '5d', '1mo', '3mo', '6mo', '1y' (기본값), '2y', '5y', '10y', 'ytd', 'max'

    verify_ssl : bool
        SSL 인증서 검증 여부 (기본값: True)
        SSL 인증서 오류 발생 시 False로 설정

    use_proxy : bool
        프록시 사용 여부 (기본값: True)
        프록시 연결 오류 발생 시 False로 설정
    """
    tickers = {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Crude Oil': 'CL=F'
    }

    # interval에 따른 한글 표시
    interval_korean = {
        '1m': '1분봉', '2m': '2분봉', '5m': '5분봉', '15m': '15분봉', '30m': '30분봉',
        '1h': '1시간봉',
        '1d': '일봉',
        '1wk': '주봉',
        '1mo': '월봉'
    }
    interval_display = interval_korean.get(interval, interval)

    print(f"--- [{interval_display}] 선물 가격 데이터 수집 시작 (기간: {period}) ---\n")

    # SSL 인증서 검증 비활성화 처리
    if not verify_ssl:
        # 환경 변수를 통해 SSL 검증 비활성화
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        print("SSL 인증서 검증이 비활성화되었습니다.")

    # 프록시 비활성화 처리
    if not use_proxy:
        os.environ['NO_PROXY'] = '*'
        os.environ['no_proxy'] = '*'
        print("프록시가 비활성화되었습니다.")

    print()

    # curl_cffi 세션 생성 (브라우저 모방)
    proxies = {} if not use_proxy else None
    try:
        session = curl_requests.Session(impersonate="chrome", proxies=proxies)
    except:
        # impersonate 실패 시 기본 세션 사용
        session = curl_requests.Session(proxies=proxies)

    if not verify_ssl:
        session.verify = False

    all_data = []

    for name, ticker_symbol in tickers.items():
        try:
            # curl_cffi 세션을 사용하여 ticker 생성
            ticker = yf.Ticker(ticker_symbol, session=session)

            # 지정된 interval과 period로 데이터 가져오기
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                # 날짜가 인덱스로 되어있으므로 컬럼으로 뺌
                df = df.reset_index()

                # 어떤 상품인지 구분하기 위해 컬럼 추가
                df['Symbol'] = name

                # yfinance는 interval에 따라 'Date' 또는 'Datetime' 컬럼을 사용
                # Datetime이 있으면 Date로 변경하여 통일
                if 'Datetime' in df.columns:
                    df['Date'] = df['Datetime']
                    df = df.drop('Datetime', axis=1)

                # 필요한 컬럼만 정리 (날짜, 시가, 고가, 저가, 종가, 거래량, 상품명)
                cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']
                # 데이터에 있는 컬럼만 선택 (Volume이 없는 경우 방지)
                available_cols = [c for c in cols if c in df.columns]
                df = df[available_cols]

                # 날짜 형식 설정: interval에 따라 다르게 표시
                if interval in ['1m', '2m', '5m', '15m', '30m', '1h']:
                    # 분봉/시간봉은 날짜와 시간을 모두 표시
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 일봉 이상은 날짜만 표시
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                
                all_data.append(df)
                print(f"[{name}] {len(df)}개 데이터 수집 완료")
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
    # 사용 예시:
    # 1일봉 데이터 (기본값)
    # SSL 인증서 오류가 발생하면 verify_ssl=False로 설정하세요
    # 프록시 연결 오류가 발생하면 use_proxy=False로 설정하세요
    print("=" * 60)
    result_daily = get_futures_data(interval='1d', period='1mo', verify_ssl=False, use_proxy=True)

    if not result_daily.empty:
        print("\n--- [일봉] 수집 결과 (상위 5개) ---")
        print(result_daily.head())
        print("\n--- [일봉] 수집 결과 (하위 5개) ---")
        print(result_daily.tail())
    else:
        print("일봉 데이터를 가져오지 못했습니다.")

    # 1시간봉 데이터 예시 (주석 해제하여 사용)
    # print("\n" + "=" * 60)
    # result_hourly = get_futures_data(interval='1h', period='5d')
    # if not result_hourly.empty:
    #     print("\n--- [1시간봉] 수집 결과 (상위 5개) ---")
    #     print(result_hourly.head())
    #     print("\n--- [1시간봉] 수집 결과 (하위 5개) ---")
    #     print(result_hourly.tail())

    # 엑셀로 저장하고 싶으면 아래 주석 해제
    # result_daily.to_excel("futures_daily_data.xlsx", index=False)
    # result_hourly.to_excel("futures_hourly_data.xlsx", index=False)
    # print("\n엑셀 파일로 저장되었습니다.")
