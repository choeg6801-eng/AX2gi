import pandas as pd
import requests

# 전체 데이터를 담을 빈 리스트 생성
all_df_list = []

# 1페이지부터 10페이지까지 반복 (필요에 따라 숫자를 늘리거나 줄이세요)
for page in range(1, 11):
  url = f'https://finance.naver.com/item/sise_day.naver?code=005930&page={page}'
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  }

  response = requests.get(url, headers=headers)
  df_list = pd.read_html(response.text)
  df = df_list[0]

  # 결측값(NaN)이 있는 행 제거
  df = df.dropna(how='all')

  # 리스트에 추가
  all_df_list.append(df)

# 여러 페이지의 데이터를 하나로 합치기
final_df = pd.concat(all_df_list, ignore_index=True)

# 날짜 최신순으로 정렬
final_df = final_df.sort_values(by='날짜', ascending=False)

# 엑셀 파일로 저장
final_df.to_excel('naver_samsung_stock_all.xlsx', index=False)

print('10페이지 분량의 데이터 수집 및 엑셀 저장 완료!')