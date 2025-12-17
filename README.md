# 금, 은, 오일 선물 가격 수집 프로그램

yfinance를 사용하여 금(Gold), 은(Silver), 원유(Crude Oil) 선물 가격을 다양한 시간 단위로 수집하는 프로그램입니다.

## 기능

- **다양한 시간 단위 지원**: 1분봉, 5분봉, 1시간봉, 1일봉, 주봉, 월봉 등
- **기간 설정 가능**: 1일, 1개월, 1년 등 원하는 기간 설정
- **3가지 상품**: 금(GC=F), 은(SI=F), 원유(CL=F) 선물 가격 수집
- **SSL/프록시 설정**: 네트워크 환경에 맞춰 SSL 검증 및 프록시 사용 제어

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

## 주의사항

- 분봉 데이터는 최근 7일간의 데이터만 제공됩니다
- 네트워크 환경에 따라 데이터 수집이 실패할 수 있습니다
- yfinance는 Yahoo Finance API를 사용하므로, API 변경 시 동작하지 않을 수 있습니다
