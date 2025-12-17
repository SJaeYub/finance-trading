# 금, 은, 오일 선물 트레이딩 시스템

yfinance를 사용하여 금(Gold), 은(Silver), 원유(Crude Oil) 선물 가격을 다양한 시간 단위로 수집하고, 볼린저 밴드 기반 트레이딩 시그널을 생성하는 프로그램입니다.

## 기능

- **다양한 시간 단위 지원**: 1분봉, 5분봉, 1시간봉, 1일봉, 주봉, 월봉 등
- **기간 설정 가능**: 1일, 1개월, 1년 등 원하는 기간 설정
- **3가지 상품**: 금(GC=F), 은(SI=F), 원유(CL=F) 선물 가격 수집
- **SSL/프록시 설정**: 네트워크 환경에 맞춰 SSL 검증 및 프록시 사용 제어
- **볼린저 밴드 트레이딩**: 자동 시그널 생성 및 포지션 관리

## 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 기본 사용법

```python
from main import get_futures_data

# 1일봉 데이터 수집 (최근 1개월)
result = get_futures_data(interval='1d', period='1mo')
print(result)

# 1시간봉 데이터 수집 (최근 5일)
result = get_futures_data(interval='1h', period='5d')
print(result)

# 30분봉 데이터 수집 (최근 1일)
result = get_futures_data(interval='30m', period='1d')
print(result)
```

### SSL 인증서 오류 해결

SSL 인증서 관련 오류가 발생하는 경우:

```python
# SSL 인증서 검증 비활성화
result = get_futures_data(interval='1d', period='1mo', verify_ssl=False)
```

### 프록시 연결 오류 해결

프록시 서버 연결 오류가 발생하는 경우:

```python
# 프록시 비활성화
result = get_futures_data(interval='1d', period='1mo', use_proxy=False)
```

### 모든 옵션 사용

```python
# SSL 검증 비활성화 + 프록시 비활성화
result = get_futures_data(
    interval='1d',
    period='1mo',
    verify_ssl=False,
    use_proxy=False
)
```

### 지원하는 interval 옵션

- `'1m'`, `'2m'`, `'5m'`, `'15m'`, `'30m'` - 분봉
- `'1h'` - 1시간봉
- `'1d'` - 1일봉 (기본값)
- `'1wk'` - 주봉
- `'1mo'` - 월봉

### 지원하는 period 옵션

- `'1d'`, `'5d'` - 일 단위
- `'1mo'`, `'3mo'`, `'6mo'` - 월 단위
- `'1y'` (기본값), `'2y'`, `'5y'`, `'10y'` - 연 단위
- `'ytd'` - 올해 시작부터
- `'max'` - 전체 기간

## 실행

```bash
python main.py
```

## 출력 데이터 형식

| Date | Open | High | Low | Close | Volume | Symbol |
|------|------|------|-----|-------|--------|--------|
| 2024-01-01 | 2050.0 | 2055.0 | 2048.0 | 2053.0 | 100000 | Gold |

## 볼린저 밴드 트레이딩 시스템

볼린저 밴드를 이용한 자동 트레이딩 시그널 생성 시스템입니다.

### 트레이딩 로직

- **매수(LONG) 신호**: 종가가 볼린저 밴드 상한선을 돌파
- **매도(SHORT) 신호**: 종가가 볼린저 밴드 하한선을 하향 돌파
- **LONG 청산**: LONG 포지션 보유 중 종가가 중간선(SMA) 아래로 하락
- **SHORT 청산**: SHORT 포지션 보유 중 종가가 중간선(SMA) 위로 상승

### 기본 사용법

```python
from bollinger_trading import BollingerBandTrading

# 트레이딩 시스템 생성
trading_system = BollingerBandTrading(
    symbol='GC=F',           # 거래 심볼 (금 선물)
    sma_period=20,           # SMA 계산 기간 (20일)
    std_multiplier=2,        # 표준편차 배수 (2배)
    check_interval='1h',     # 체크 주기 (1시간)
    verify_ssl=False,        # SSL 인증서 검증
    use_proxy=True           # 프록시 사용
)

# 지속적으로 실행
trading_system.run(continuous=True)

# 한 번만 실행
trading_system.run(continuous=False)
```

### 실행 예시

```bash
# 기본 실행 (계속 실행)
python bollinger_trading.py

# 테스트 실행 (한 번만)
python test_bollinger.py
```

### 설정 가능한 파라미터

| 파라미터 | 설명 | 기본값 | 예시 |
|---------|------|--------|------|
| `symbol` | 거래할 심볼 | - | 'GC=F', 'SI=F', 'CL=F' |
| `sma_period` | SMA 계산 기간 | 20 | 10, 20, 50 |
| `std_multiplier` | 표준편차 배수 | 2 | 1.5, 2, 2.5 |
| `check_interval` | 체크 주기 | '1h' | '1m', '5m', '1h', '1d' |
| `verify_ssl` | SSL 인증서 검증 | True | True, False |
| `use_proxy` | 프록시 사용 | True | True, False |
| `save_dir` | 데이터 저장 디렉토리 | './trading_data' | './data', './logs' |

### 다양한 설정 예시

```python
# 금 선물 - 일봉, 표준편차 2.5배
gold_trading = BollingerBandTrading(
    symbol='GC=F',
    sma_period=20,
    std_multiplier=2.5,
    check_interval='1d',
    verify_ssl=False
)

# 은 선물 - 1시간봉, 10일 SMA
silver_trading = BollingerBandTrading(
    symbol='SI=F',
    sma_period=10,
    std_multiplier=2,
    check_interval='1h',
    verify_ssl=False
)

# 원유 선물 - 30분봉
oil_trading = BollingerBandTrading(
    symbol='CL=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='30m',
    verify_ssl=False
)
```

### 출력 예시

```
================================================================================
[2025-12-17 12:00:00] GC=F 체크 중...
현재 가격: $2050.50
볼린저 상한선: $2065.30
볼린저 중간선: $2045.00
볼린저 하한선: $2024.70
현재 포지션: 없음

🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔
📈 매수(LONG) 신호 발생!
   진입 가격: $2050.50
   상한선 돌파!
🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔 🔔
================================================================================
```

### 포지션 저장 및 히스토리 기능

트레이딩 시스템은 자동으로 포지션 상태와 거래 히스토리를 JSON 파일로 저장합니다.

#### 자동 저장 기능

- **포지션 상태 저장**: 진입/청산 시 자동으로 현재 포지션을 JSON 파일에 저장
- **거래 히스토리 기록**: 모든 진입/청산 기록을 시간순으로 저장
- **프로그램 재시작 시 복원**: 시스템 시작 시 자동으로 이전 포지션 로드

#### 저장 파일 위치

```
trading_data/
├── GC_F_position.json      # 금 선물 포지션 상태
├── GC_F_history.json        # 금 선물 거래 히스토리
├── SI_F_position.json       # 은 선물 포지션 상태
├── SI_F_history.json        # 은 선물 거래 히스토리
└── ...
```

#### 포지션 파일 형식 (GC_F_position.json)

```json
{
  "symbol": "GC=F",
  "position": "LONG",
  "entry_price": 2050.5,
  "entry_time": "2025-12-17 12:00:00",
  "last_updated": "2025-12-17 12:00:00"
}
```

#### 거래 히스토리 형식 (GC_F_history.json)

```json
[
  {
    "symbol": "GC=F",
    "action": "LONG_ENTRY",
    "price": 2050.5,
    "time": "2025-12-17 12:00:00",
    "upper_band": 2065.3,
    "middle_band": 2045.0,
    "lower_band": 2024.7
  },
  {
    "symbol": "GC=F",
    "action": "LONG_EXIT",
    "price": 2045.0,
    "entry_price": 2050.5,
    "pnl": -5.5,
    "pnl_pct": -0.27,
    "time": "2025-12-17 13:00:00",
    "upper_band": 2060.0,
    "middle_band": 2045.0,
    "lower_band": 2030.0
  }
]
```

#### 포지션 복원 예시

프로그램 시작 시 자동으로 저장된 포지션을 로드합니다:

```
✅ 저장된 포지션 로드: LONG
   진입 가격: $2050.50
   진입 시간: 2025-12-17 12:00:00
```

## 주의사항

- 분봉 데이터는 최근 7일간의 데이터만 제공됩니다
- 네트워크 환경에 따라 데이터 수집이 실패할 수 있습니다
- yfinance는 Yahoo Finance API를 사용하므로, API 변경 시 동작하지 않을 수 있습니다
- 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 실제 거래에 사용 시 자기 책임하에 사용하세요
- 과거 데이터 기반 시그널이므로 미래 수익을 보장하지 않습니다
