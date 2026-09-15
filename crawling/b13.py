import pandas as pd
import requests
from bs4 import BeautifulSoup
import openpyxl

data = []

for i in range(1, 5):
    url = f"https://startcoding.pythonanywhere.com/basic?page={i}"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select(".product")

    for item in items:
        # 1. 카테고리
        category = item.select_one(".product-category").text.strip()
        
        # 2. 상품명
        category_name = item.select_one(".product-name").text.strip()
        
        # 3. 상세페이지 링크 (a 태그의 href 속성 가져오기)
        # 만약 상대 경로라면 앞에 도메인을 붙여줍니다.
        a_tag = item.select_one(".product-name > a")
        if a_tag and "href" in a_tag.attrs:
            category_link = "https://startcoding.pythonanywhere.com" + a_tag["href"]
        else:
            category_link = ""

        # 4. 가격 정제 (할인가 등이 겹쳐있을 경우 첫 번째 가격만 깔끔하게 가져오기)
        price_text = item.select_one(".product-price").text.strip()
        # '원'을 기준으로 자르고 쉼표 제거
        price = price_text.split("원")[0].replace(",", "").strip()

        data.append([category, category_name, category_link, price])

# 데이터프레임 생성 및 엑셀 저장
df = pd.DataFrame(data, columns=["카테고리", "상품명", "상세페이지링크", "가격"])
df.to_excel("data.xlsx", index=False)
print("엑셀 저장 완료!")