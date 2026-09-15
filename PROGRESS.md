# Hybrid Trader 작업 체크포인트

최종 갱신: 2026-09-15

## 완료

- 전체 소스 검토: 현재 프로젝트 28개 Python 파일, sibling `trading-bot` 33개 Python 파일
- 고정 가격·가상 주문 반환 제거
- 주문 상태를 `NOT_SENT`, `UNKNOWN`, `REJECTED`, `UNRECONCILED`로 분리
- 체결 전 성공률·손익 확정 차단
- Upbit JWT 인증, query hash, 429·418·`Remaining-Req` 처리 추가
- 코인 24/7과 한국 주식·미국·유럽 정규장 스케줄 분리
- 신호별 중복 시세 조회 제거
- 실행 안전성 테스트 15개 통과

## 다음 작업 순서

1. 공통 체결 비용 모델 추가: commission, tax, slippage, FX (진행 중: 모델 추가)
2. 백테스트와 실시간 보고서가 동일 비용 모델 사용
3. DB 체결 원장에 broker/order/fill 식별자와 idempotency 추가
4. 계좌별 노출·예약 현금·중복 주문·일일 손실 한도 추가
5. 전체 회귀 테스트와 문법 검사

## 재개 방법

한도 초기화 후 이 파일을 먼저 읽고, `다음 작업 순서`의 미완료 첫 항목부터 계속 진행한다.
