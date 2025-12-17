import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
from curl_cffi import requests as curl_requests


class BollingerBandTrading:
    """
    볼린저 밴드 기반 트레이딩 시스템
    """

    def __init__(self, symbol, sma_period=20, std_multiplier=2, check_interval='1h',
                 verify_ssl=True, use_proxy=True):
        """
        Parameters:
        -----------
        symbol : str
            거래할 심볼 (예: 'GC=F', 'SI=F', 'CL=F')
        sma_period : int
            SMA 계산 기간 (기본값: 20)
        std_multiplier : float
            표준편차 배수 (기본값: 2)
        check_interval : str
            체크 주기 ('1h': 1시간, '1d': 1일, '30m': 30분 등)
        verify_ssl : bool
            SSL 인증서 검증 여부
        use_proxy : bool
            프록시 사용 여부
        """
        self.symbol = symbol
        self.sma_period = sma_period
        self.std_multiplier = std_multiplier
        self.check_interval = check_interval
        self.verify_ssl = verify_ssl
        self.use_proxy = use_proxy

        # 포지션 상태: None, 'LONG', 'SHORT'
        self.position = None
        self.entry_price = None

        # curl_cffi 세션 생성
        self._setup_session()

    def _setup_session(self):
        """yfinance용 세션 설정"""
        import os

        if not self.verify_ssl:
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['SSL_CERT_FILE'] = ''

        if not self.use_proxy:
            os.environ['NO_PROXY'] = '*'
            os.environ['no_proxy'] = '*'

        proxies = {} if not self.use_proxy else None
        try:
            self.session = curl_requests.Session(impersonate="chrome", proxies=proxies)
        except:
            self.session = curl_requests.Session(proxies=proxies)

        if not self.verify_ssl:
            self.session.verify = False

    def calculate_bollinger_bands(self, df):
        """
        볼린저 밴드 계산

        Parameters:
        -----------
        df : pd.DataFrame
            가격 데이터 (Close 컬럼 필요)

        Returns:
        --------
        df : pd.DataFrame
            볼린저 밴드 컬럼 추가된 데이터프레임
        """
        # SMA (중간선) 계산
        df['SMA'] = df['Close'].rolling(window=self.sma_period).mean()

        # 표준편차 계산
        df['STD'] = df['Close'].rolling(window=self.sma_period).std()

        # 상한선과 하한선 계산
        df['Upper_Band'] = df['SMA'] + (df['STD'] * self.std_multiplier)
        df['Lower_Band'] = df['SMA'] - (df['STD'] * self.std_multiplier)

        return df

    def fetch_data(self):
        """
        yfinance로 데이터 조회

        Returns:
        --------
        df : pd.DataFrame
            가격 데이터
        """
        try:
            ticker = yf.Ticker(self.symbol, session=self.session)

            # interval에 따라 적절한 period 설정
            period_map = {
                '1m': '1d', '2m': '1d', '5m': '5d', '15m': '5d', '30m': '5d',
                '1h': '1mo', '1d': '1y', '1wk': '2y', '1mo': '5y'
            }
            period = period_map.get(self.check_interval, '1mo')

            # 데이터 가져오기
            df = ticker.history(period=period, interval=self.check_interval)

            if df.empty:
                print(f"[{datetime.now()}] {self.symbol} 데이터를 가져올 수 없습니다.")
                return None

            return df

        except Exception as e:
            print(f"[{datetime.now()}] 데이터 조회 오류: {e}")
            return None

    def generate_signal(self, current_price, upper_band, lower_band, middle_band):
        """
        트레이딩 시그널 생성

        Parameters:
        -----------
        current_price : float
            현재 종가
        upper_band : float
            볼린저 밴드 상한선
        lower_band : float
            볼린저 밴드 하한선
        middle_band : float
            볼린저 밴드 중간선 (SMA)

        Returns:
        --------
        signal : str
            'LONG_ENTRY', 'SHORT_ENTRY', 'LONG_EXIT', 'SHORT_EXIT', None
        """
        signal = None

        # 진입 시그널
        if self.position is None:
            if current_price > upper_band:
                signal = 'LONG_ENTRY'
                self.position = 'LONG'
                self.entry_price = current_price
            elif current_price < lower_band:
                signal = 'SHORT_ENTRY'
                self.position = 'SHORT'
                self.entry_price = current_price

        # 청산 시그널
        elif self.position == 'LONG':
            if current_price < middle_band:
                signal = 'LONG_EXIT'
                self.position = None
                self.entry_price = None

        elif self.position == 'SHORT':
            if current_price > middle_band:
                signal = 'SHORT_EXIT'
                self.position = None
                self.entry_price = None

        return signal

    def check_and_signal(self):
        """
        현재 데이터를 확인하고 시그널 생성
        """
        print(f"\n{'='*80}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.symbol} 체크 중...")

        # 데이터 조회
        df = self.fetch_data()
        if df is None:
            return

        # 볼린저 밴드 계산
        df = self.calculate_bollinger_bands(df)

        # 최신 데이터 추출
        latest = df.iloc[-1]
        current_price = latest['Close']
        upper_band = latest['Upper_Band']
        lower_band = latest['Lower_Band']
        middle_band = latest['SMA']

        # NaN 체크
        if pd.isna(upper_band) or pd.isna(lower_band) or pd.isna(middle_band):
            print(f"볼린저 밴드 계산을 위한 데이터가 부족합니다. (최소 {self.sma_period}개 필요)")
            return

        # 현재 상태 출력
        print(f"현재 가격: ${current_price:.2f}")
        print(f"볼린저 상한선: ${upper_band:.2f}")
        print(f"볼린저 중간선: ${middle_band:.2f}")
        print(f"볼린저 하한선: ${lower_band:.2f}")
        print(f"현재 포지션: {self.position if self.position else '없음'}")

        # 시그널 생성
        signal = self.generate_signal(current_price, upper_band, lower_band, middle_band)

        # 시그널 출력
        if signal:
            print(f"\n{'🔔 '*20}")
            if signal == 'LONG_ENTRY':
                print(f"📈 매수(LONG) 신호 발생!")
                print(f"   진입 가격: ${current_price:.2f}")
                print(f"   상한선 돌파!")
            elif signal == 'SHORT_ENTRY':
                print(f"📉 매도(SHORT) 신호 발생!")
                print(f"   진입 가격: ${current_price:.2f}")
                print(f"   하한선 돌파!")
            elif signal == 'LONG_EXIT':
                pnl = current_price - self.entry_price
                pnl_pct = (pnl / self.entry_price) * 100
                print(f"🔄 LONG 청산 신호 발생!")
                print(f"   진입 가격: ${self.entry_price:.2f}")
                print(f"   청산 가격: ${current_price:.2f}")
                print(f"   손익: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            elif signal == 'SHORT_EXIT':
                pnl = self.entry_price - current_price
                pnl_pct = (pnl / self.entry_price) * 100
                print(f"🔄 SHORT 청산 신호 발생!")
                print(f"   진입 가격: ${self.entry_price:.2f}")
                print(f"   청산 가격: ${current_price:.2f}")
                print(f"   손익: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            print(f"{'🔔 '*20}")
        else:
            print(f"신호 없음 (현재 포지션 유지)")

        print(f"{'='*80}")

    def get_interval_seconds(self):
        """
        check_interval을 초 단위로 변환

        Returns:
        --------
        seconds : int
            초 단위 시간
        """
        interval_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '1d': 86400
        }
        return interval_map.get(self.check_interval, 3600)

    def run(self, continuous=True):
        """
        트레이딩 시스템 실행

        Parameters:
        -----------
        continuous : bool
            True면 지속적으로 실행, False면 한 번만 실행
        """
        print(f"\n{'='*80}")
        print(f"볼린저 밴드 트레이딩 시스템 시작")
        print(f"{'='*80}")
        print(f"심볼: {self.symbol}")
        print(f"SMA 기간: {self.sma_period}")
        print(f"표준편차 배수: {self.std_multiplier}")
        print(f"체크 주기: {self.check_interval}")
        print(f"{'='*80}\n")

        if not continuous:
            # 한 번만 실행
            self.check_and_signal()
        else:
            # 지속적으로 실행
            interval_seconds = self.get_interval_seconds()
            print(f"⏰ {interval_seconds}초마다 체크합니다. (Ctrl+C로 종료)\n")

            try:
                while True:
                    self.check_and_signal()
                    print(f"\n⏳ 다음 체크까지 {interval_seconds}초 대기 중...\n")
                    time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print(f"\n\n{'='*80}")
                print(f"트레이딩 시스템 종료")
                print(f"{'='*80}")


def main():
    """
    사용 예시
    """
    # 설정
    SYMBOL = 'GC=F'  # 금 선물
    SMA_PERIOD = 20  # 20일 이동평균
    STD_MULTIPLIER = 2  # 표준편차 2배
    CHECK_INTERVAL = '1h'  # 1시간마다 체크

    # 트레이딩 시스템 생성
    trading_system = BollingerBandTrading(
        symbol=SYMBOL,
        sma_period=SMA_PERIOD,
        std_multiplier=STD_MULTIPLIER,
        check_interval=CHECK_INTERVAL,
        verify_ssl=False,  # SSL 인증서 오류 발생 시 False
        use_proxy=True     # 프록시 연결 오류 발생 시 False
    )

    # 시스템 실행
    # continuous=True: 지속 실행, False: 한 번만 실행
    trading_system.run(continuous=True)


if __name__ == "__main__":
    main()
