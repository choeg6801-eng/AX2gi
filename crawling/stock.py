import FinanceDataReader as fdr

# 1. 삼성전자 주가 데이터 가져오기 (2025년 1월 1일부터 현재까지)
df = fdr.DataReader('005930', '2025-01-01')

# 2. 엑셀 파일로 저장하기
df.to_excel('samsung_stock.xlsx', index=True)

print('엑셀 파일 저장 완료!')
