import folium

# 서울 시내 명소 4곳 이름, 위도, 경도 샘플 데이터
places = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "남산타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "롯데월드", "lat": 37.5111, "lon": 127.0982},
    {"name": "한강", "lat": 37.5219, "lon": 126.9244}
]

# 서울 중심부(시청 기준) 좌표로 기본 지도 생성
map_center = [37.5666, 126.9784]
m = folium.Map(location=map_center, zoom_start=12)

# 리스트에 담긴 장소들을 하나씩 꺼내면서 마커 추가
for place in places:
    # 각 장소의 이름, 위도, 경도를 꺼내서 사용
    place_name = place["name"]
    latitude = place["lat"]
    longitude = place["lon"]
    
    # 지도에 마커 생성 후 추가
    folium.Marker(
        location=[latitude, longitude],
        popup=place_name,
        tooltip=place_name
    ).add_to(m)

# HTML 파일로 저장
m.save("basic_map.html")
print("지도가 성공적으로 저장되었습니다: basic_map.html")

#지도의 시작 중심 좌표(경복궁 기준) 지정해서 folium 지도 객체 생성 
#숫자가 클수록 더 가깝게 보여준다 

seoul_center = [37.5796, 126.9770]
map = folium.Map(location=seoul_center, zoom_start=13)


#folium으로 지도에 마커를 표시하는 예제 코드

#import folium

#서울 시내 명소 4곳의 좌표(위도/경도)와 이름을 리스트로 받아 folium 지도를 만들고

#각 좌표에 이름표가 붙은 마커를 찍은 다음, basic_map.html 파일로 저장하느느 예제 코드입니다

# 저장 basic_map.html 웹 브라우저로 열어서 확인

# python day06-1.py


#서울 시내 명소 4곳 이름, 위도, 경도 샘플데이터



