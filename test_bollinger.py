"""
볼린저 밴드 트레이딩 시스템 테스트 스크립트
한 번만 실행하여 시그널 확인
"""
from bollinger_trading import BollingerBandTrading

# 금 선물 테스트
print("=" * 80)
print("금(Gold) 선물 테스트")
print("=" * 80)

gold_system = BollingerBandTrading(
    symbol='GC=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='1d',  # 일봉으로 테스트
    verify_ssl=False,
    use_proxy=True
)

# 한 번만 실행
gold_system.run(continuous=False)

print("\n\n")

# 은 선물 테스트
print("=" * 80)
print("은(Silver) 선물 테스트")
print("=" * 80)

silver_system = BollingerBandTrading(
    symbol='SI=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='1d',
    verify_ssl=False,
    use_proxy=True
)

# 한 번만 실행
silver_system.run(continuous=False)

print("\n\n")

# 원유 선물 테스트
print("=" * 80)
print("원유(Crude Oil) 선물 테스트")
print("=" * 80)

oil_system = BollingerBandTrading(
    symbol='CL=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='1d',
    verify_ssl=False,
    use_proxy=True
)

# 한 번만 실행
oil_system.run(continuous=False)
