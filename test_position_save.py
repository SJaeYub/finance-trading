"""
포지션 저장/로드 기능 테스트 스크립트
"""
from bollinger_trading import BollingerBandTrading
import json
import os

print("=" * 80)
print("포지션 저장/로드 기능 테스트")
print("=" * 80)

# 테스트용 트레이딩 시스템 생성
system = BollingerBandTrading(
    symbol='GC=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='1d',
    verify_ssl=False,
    use_proxy=True,
    save_dir='./test_trading_data'
)

print("\n1. 한 번 실행하여 시그널 확인")
system.run(continuous=False)

print("\n\n2. 저장된 포지션 파일 확인")
if os.path.exists(system.position_file):
    with open(system.position_file, 'r', encoding='utf-8') as f:
        position_data = json.load(f)
    print(f"포지션 파일 내용:")
    print(json.dumps(position_data, indent=2, ensure_ascii=False))
else:
    print("포지션 파일이 없습니다.")

print("\n\n3. 거래 히스토리 파일 확인")
if os.path.exists(system.history_file):
    with open(system.history_file, 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    print(f"거래 히스토리 ({len(history_data)}건):")
    for i, trade in enumerate(history_data[-5:], 1):  # 최근 5개만
        print(f"\n[{i}] {trade.get('action')}")
        print(f"    시간: {trade.get('time')}")
        print(f"    가격: ${trade.get('price'):.2f}")
        if 'pnl' in trade:
            print(f"    손익: ${trade.get('pnl'):.2f} ({trade.get('pnl_pct'):+.2f}%)")
else:
    print("거래 히스토리 파일이 없습니다.")

print("\n\n4. 새로운 시스템 인스턴스 생성하여 포지션 복원 확인")
system2 = BollingerBandTrading(
    symbol='GC=F',
    sma_period=20,
    std_multiplier=2,
    check_interval='1d',
    verify_ssl=False,
    use_proxy=True,
    save_dir='./test_trading_data'
)

print(f"\n복원된 포지션: {system2.position}")
if system2.position:
    print(f"진입 가격: ${system2.entry_price:.2f}")
    print(f"진입 시간: {system2.entry_time}")

print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)
