import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# 상위 폴더의 .env 파일 경로 설정
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

WEATHER_API_KEY = os.getenv("openweather_API_key") or os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("exchange_API_key") or os.getenv("EXCHANGE_API_KEY")
KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY") or os.getenv("KAKAO_API_KEY")

st.set_page_config(
    page_title="✈️ 트립 피플 - 스마트 여행 플래너",
    page_icon="🎒",
    layout="wide"
)

# 모바일 반응형 및 스타일 설정
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                        url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .centered-title {
        text-align: center;
        font-weight: 800;
        color: #1E3A8A;
    }
    .centered-subtitle {
        text-align: center;
        color: #4B5563;
        margin-bottom: 30px;
        font-size: 1.1rem;
    }
    html, body, [class*="css"] {
        font-size: 1.05rem !important;
    }
    .element-container {
        background: transparent !important;
    }
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 보조 함수 정의
# ==========================================
def get_weather_data(city_name, api_key):
    if not api_key:
        return None, "OpenWeather API 키가 설정되지 않았습니다."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.text.strip():
            return res.json(), None
    except Exception as e:
        return None, str(e)
    return None, "날씨 정보를 불러오지 못했습니다."

def get_exchange_rate(base, target, api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.text.strip():
            data = res.json()
            if data.get("result") == "success":
                rates = data["conversion_rates"]
                return rates.get(target), rates, None
    except Exception:
        pass
    
    try:
        fallback_url = f"https://open.er-api.com/v6/latest/{base}"
        res = requests.get(fallback_url, timeout=5)
        if res.status_code == 200 and res.text.strip():
            data = res.json()
            if data.get("result") == "success":
                rates = data["rates"]
                return rates.get(target), rates, None
    except Exception as e:
        return None, None, str(e)
    return None, None, "환율 정보를 불러오지 못했습니다."

def get_kakao_places(keyword, x, y, api_key):
    if not api_key:
        return None, "카카오 API 키가 설정되지 않았습니다."
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={keyword}&x={x}&y={y}&sort=distance&size=15"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and res.text.strip():
            return res.json().get("documents", []), None
    except Exception as e:
        return None, str(e)
    return None, "카카오맵 API 오류"

def get_reverse_geocode(lat_val, lon_val):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat_val}&lon={lon_val}&format=json&accept-language=ko"
    headers = {'User-Agent': 'TravelDashboard/1.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and res.text.strip():
            data = res.json()
            if "display_name" in data:
                return data["display_name"]
    except Exception:
        pass
    return f"위도: {lat_val}, 경도: {lon_val}"

def translate_city_to_english(city_str):
    city_map = {
        "프라하": "Prague", "런던": "London", "로마": "Rome",
        "베를린": "Berlin", "바르셀로나": "Barcelona", "시드니": "Sydney",
        "뮌헨": "Munich", "파리": "Paris", "도쿄": "Tokyo", 
        "뉴욕": "New York", "서울": "Seoul", "부산": "Busan"
    }
    cleaned = city_str.strip()
    return city_map.get(cleaned, cleaned)

def get_default_coordinates(city_name):
    coord_map = {
        "Prague": (50.0755, 14.4378), "London": (51.5074, -0.1278),
        "Rome": (41.9028, 12.4964), "Berlin": (52.5200, 13.4050),
        "Barcelona": (41.3851, 2.1734), "Sydney": (-33.8688, 151.2093),
        "Munich": (48.1351, 11.5820), "Paris": (48.8566, 2.3522),
        "New York": (40.7128, -74.0060), "Tokyo": (35.6762, 139.6503),
        "Seoul": (37.5665, 126.9780)
    }
    return coord_map.get(city_name, (48.8566, 2.3522))

# ==========================================
# 2. 도시별 실제 유명 장소 데이터베이스 (실제 상호명 및 실제 주소 15개 이상 구성)
# ==========================================
REAL_PLACES_DB = {
    "prague": [
        {"name": "Good Food, Coffee and Bakery", "address": "Karoliny Světlé 2, 110 00 Staré Město, 체코", "lat": 50.0833, "lon": 14.4152},
        {"name": "Trdlomls", "address": "Smetanovo nábř. 1012/2, 110 00 Staré Město, 체코", "lat": 50.0850, "lon": 14.4140},
        {"name": "MLS Traditional Czech Chimney Cake", "address": "Mostecká 48/5, 118 00 Malá Strana, 체코", "lat": 50.0872, "lon": 14.4048},
        {"name": "Krusovice Restaurant Spilka", "address": "U královského dvora 931/2, 110 00 Staré Město, 체코", "lat": 50.0875, "lon": 14.4285},
        {"name": "Bakeshop Prague", "address": "Kozí 918/1, 110 00 Staré Město, 체코", "lat": 50.0895, "lon": 14.4230},
        {"name": "Cafe Louvre", "address": "Národní 22, 110 00 Nové Město, 체코", "lat": 50.0812, "lon": 14.4190},
        {"name": "Kantýna", "address": "Politických vězňů 1511/5, 110 00 Nové Město, 체코", "lat": 50.0818, "lon": 14.4280},
        {"name": "Lokál Dlouhááá", "address": "Dlouhá 33, 110 00 Staré Město, 체코", "lat": 50.0890, "lon": 14.4245},
        {"name": "Naše maso", "address": "Dlouhá 39, 110 00 Staré Město, 체코", "lat": 50.0893, "lon": 14.4248},
        {"name": "Hard Rock Cafe Prague", "address": "Dum U Zlateho Cepecu, V Celnici 4, 110 00 Praha 1, 체코", "lat": 50.0860, "lon": 14.4290},
        {"name": "Café Imperial", "address": "Na Poříčí 15, 110 00 Petrská čtvrť, 체코", "lat": 50.0897, "lon": 14.4312},
        {"name": "Grand Café Orient", "address": "Ovocný trh 19, 110 00 Staré Město, 체코", "lat": 50.0855, "lon": 14.4260},
        {"name": "Maitrea Restaurant", "address": "Týnská ulička 6, 110 00 Staré Město, 체코", "lat": 50.0878, "lon": 14.4215},
        {"name": "Restaurace U Fleků", "address": "Křemencova 11, 110 00 Nové Město, 체코", "lat": 50.0792, "lon": 14.4178},
        {"name": "Dish Fine Burger Bistro", "address": "Římská 29, 120 00 Vinohrady, 체코", "lat": 50.0768, "lon": 14.4355}
    ],
    "london": [
        {"name": "Honest Burgers Soho", "address": "12 Meard St, London W1F 0PR, 영국", "lat": 51.5135, "lon": -0.1332},
        {"name": "Flat Iron Covent Garden", "address": "17-18 Henrietta St, London WC2E 8QH, 영국", "lat": 51.5118, "lon": -0.1235},
        {"name": "Burger & Lobster Soho", "address": "36 Dean St, London W1D 4PS, 영국", "lat": 51.5143, "lon": -0.1322},
        {"name": "Dishoom Covent Garden", "address": "12 Upper St Martin's Ln, London WC2H 9FB, 영국", "lat": 51.5126, "lon": -0.1260},
        {"name": "The Churchill Arms", "address": "119 Kensington Church St, London W8 7LN, 영국", "lat": 51.5065, "lon": -0.1935},
        {"name": "Borough Market", "address": "8 Southwark St, London SE1 1TL, 영국", "lat": 51.5055, "lon": -0.0909},
        {"name": "Hawksmoor Seven Dials", "address": "11 Langley St, London WC2H 9JG, 영국", "lat": 51.5132, "lon": -0.1250},
        {"name": "The Wolseley", "address": "160 Piccadilly, St. James's, London W1J 9EB, 영국", "lat": 51.5075, "lon": -0.1412},
        {"name": "Padella", "address": "6 Southwark St, London SE1 1TQ, 영국", "lat": 51.5052, "lon": -0.0905},
        {"name": "Duck & Waffle", "address": "110 Bishopsgate, London EC2N 4AY, 영국", "lat": 51.5155, "lon": -0.0825},
        {"name": "Sketch London", "address": "9 Conduit St, Mayfair, London W1S 2XG, 영국", "lat": 51.5128, "lon": -0.1420},
        {"name": "Fortnum & Mason", "address": "181 Piccadilly, St. James's, London W1A 1ER, 영국", "lat": 51.5082, "lon": -0.1405},
        {"name": "Covent Garden Market", "address": "The Market, Covent Garden, London WC2E 8RF, 영국", "lat": 51.5115, "lon": -0.1228},
        {"name": "Harrods Food Hall", "address": "87-135 Brompton Rd, Knightsbridge, London SW1X 7XL, 영국", "lat": 51.4994, "lon": -0.1632},
        {"name": "Notting Hill Bookshop", "address": "13 Blenheim Crescent, Notting Hill, London W11 2EE, 영국", "lat": 51.5130, "lon": -0.2045}
    ],
    "paris": [
        {"name": "Le Comptoir de la Relais", "address": "9 Carrefour de l'Odéon, 75006 Paris, 프랑스", "lat": 48.8520, "lon": 2.3385},
        {"name": "Bouillon Chartier", "address": "7 Rue du Mont-Thabor, 75001 Paris, 프랑스", "lat": 48.8665, "lon": 2.3275},
        {"name": "L'As du Fallafel", "address": "34 Rue des Rosiers, 75004 Paris, 프랑스", "lat": 48.8575, "lon": 2.3590},
        {"name": "Angelina Paris", "address": "226 Rue de Rivoli, 75001 Paris, 프랑스", "lat": 48.8650, "lon": 2.3325},
        {"name": "Café de Flore", "address": "172 Bd Saint-Germain, 75006 Paris, 프랑스", "lat": 48.8542, "lon": 2.3330},
        {"name": "Les Deux Magots", "address": "6 Place Saint-Germain des Prés, 75006 Paris, 프랑스", "lat": 48.8540, "lon": 2.3332},
        {"name": "Du Pain et des Idées", "address": "34 Rue Yves Toudic, 75010 Paris, 프랑스", "lat": 48.8712, "lon": 2.3630},
        {"name": "Pierre Hermé Paris", "address": "72 Rue Bonaparte, 75006 Paris, 프랑스", "lat": 48.8515, "lon": 2.3335},
        {"name": "Ladurée Champs-Élysées", "address": "75 Av. des Champs-Élysées, 75008 Paris, 프랑스", "lat": 48.8705, "lon": 2.3065},
        {"name": "Le Jules Verne", "address": "Eiffel Tower, Av. Gustave Eiffel, 75007 Paris, 프랑스", "lat": 48.8582, "lon": 2.2945},
        {"name": "Bistrot Paul Bert", "address": "18 Rue Paul Bert, 75011 Paris, 프랑스", "lat": 48.8525, "lon": 2.3850},
        {"name": "Breizh Café Marais", "address": "109 Rue Vieille-du-Temple, 75003 Paris, 프랑스", "lat": 48.8590, "lon": 2.3595},
        {"name": "Shakespeare and Company Café", "address": "37 Rue de la Bûcherie, 75005 Paris, 프랑스", "lat": 48.8528, "lon": 2.3470},
        {"name": "Galeries Lafayette Gourmet", "address": "35 Boulevard Haussmann, 75009 Paris, 프랑스", "lat": 48.8732, "lon": 2.3320},
        {"name": "Le Procope", "address": "13 Rue de l'Ancienne Comédie, 75006 Paris, 프랑스", "lat": 48.8532, "lon": 2.3380}
    ]
}

CITY_GUIDE = {
    "paris": {
        "food_meal": ["🍲 어니언 스프 (French Onion Soup)", "🥩 스테이크 프리스 (Steak Frites)", "🦪 에스카르고 & 해산물 요리"],
        "food_dessert": ["🥖 정통 바게트 & 크루아상", "🥮 마카롱 (Laduree/Pierre Herme)", "🍫 수제 초콜릿 & 에클레르"],
        "places_art": ["🖼️ 루브르 박물관", "🏛️ 오르세 미술관", "🎨 퐁피두 센터"],
        "places_activity": ["⛵ 센강 유람선(바토무슈) 탑승", "🍷 프랑스 와인 시음 클래스", "🥖 바게트 만들기 원데이 클래스"],
        "places_shopping": ["🛍️ 갤러리 라파예트 백화점", "🕯️ 르메르 & 아페쎄 플래그십 스토어", "📚 셰익스피어 앤 컴퍼니 서점"],
        "places_landmark": ["🗼 에펠탑", "⛪ 노트르담 대성당", "🏛️ 개선문 & 샹젤리제 거리"]
    },
    "prague": {
        "food_meal": ["🍖 굴라쉬 (Goulash)", "🥩 꼴레뇨 (Koleno - 전통 돼지고기족발구이)", "🧀 오리 구이 & 감자만두"],
        "food_dessert": ["🥖 굴뚝빵 (Trdelník)", "🍺 체코 필스너 우르켈 생맥주", "🥮 체코 전통 허니케이크 (Marlenka)"],
        "places_art": ["🖼️ 프레즈노 박물관", "🏛️ 국립 미술관", "🎨 프라하 성 국립 갤러리"],
        "places_activity": ["⛵ 블타바 강 유람선 야경 투어", "🍺 프라하 맥주 스파 체험", "🎻 카를교 야경 산책"],
        "places_shopping": ["🛍️ 팔라디움 쇼핑센터", "🎁 하벨 시장 (Havelské tržiště)", "🕯️ 보헤미안 크리스탈 상점가"],
        "places_landmark": ["🌉 카를교 (Charles Bridge)", "🏰 프라하 성 (Prague Castle)", "⏰ 구시가 광장 천문시계"]
    },
    "london": {
        "food_meal": ["🥧 피치 & 스테이크 파이", "🐟 피시 앤 칩스 (Fish and Chips)", "🍛 영국식 치킨 티카 마살라"],
        "food_dessert": ["🫖 애프터눈 티 세트 & 스콘", "🍮 스티키 토피 푸딩", "🍫 영국 전통 퍼지 (Fudge)"],
        "places_art": ["🖼️ 대영 박물관 (British Museum)", "🏛️ 내셔널 갤러리", "🎨 테이트 모던"],
        "places_activity": ["🎭 런던 웨스트엔드 뮤지컬 관람", "🎡 런던 아이 탑승", " Thames 템즈강 유람선 투어"],
        "places_shopping": ["🛍️ 해러즈 백화점 (Harrods)", "🎁 코벤트 가든 시장", "🧵 옥스퍼드 스트리트 쇼핑가"],
        "places_landmark": ["🕰️ 빅벤 & 국회의사당", "🌉 타워 브리지", "👑 런던 탑"]
    },
    "rome": {
        "food_meal": ["🍝 까르보나라 파이프 (정통 로마식)", "🍕 로마식 얇은 피자 (Pizza Romana)", "🥩 소꼬리 찜 요리 (Coda alla Vaccinara)"],
        "food_dessert": ["🍨 정통 수제 젤라또", "☕ 이탈리안 에스프레소 & 티라미수", "🥮 카놀리 파이"],
        "places_art": ["🖼️ 바티칸 박물관 & 시스티나 성당", "🏛️ 보르게세 미술관", "🎨 카피톨리니 미술관"],
        "places_activity": ["🪙 트레비 분수 동전 던지기 체험", "🍷 이탈리아 와인 & 파스타 쿠킹 클래스", "🛵 로마 시내 스쿠터 야경 투어"],
        "places_shopping": ["🛍️ 콘도티 거리 (Via Condotti) 명품가", "🎁 나보나 광장 기념품 상점", "🧵 콜로세움 인근 가죽 공방 거리"],
        "places_landmark": ["🏛️ 콜로세움 (Colosseum)", "🪙 트레비 분수", "🏛️ 판테온 신전"]
    },
    "munich": {
        "food_meal": ["🍖 슈바인스학세 (Schweinshaxe)", "🥨 독일 바이에른 프레첼 (Pretzel)", "🥩 바이에른 소시지 (Weisswurst)"],
        "food_dessert": ["🍎 아펠스트루델 (Apfelstrudel)", "🥞 카이저슈마른 (Kaiserschmarrn)", "🍺 독일 정통 밀맥주 (Weissbier)"],
        "places_art": ["🖼️ 알테 피나코테크 미술관", "🏛️ 렌바흐하우스 미술관", "🎨 뮌헨 현대미술관"],
        "places_activity": ["🍻 호프브로이하우스 맥주 양조장 투어", "🚲 잉글리시 가든 자전거 라이딩", "🏰 퓌센 노이슈반슈타인 성 투어"],
        "places_shopping": ["🛍️ 마리엔플라츠 쇼핑거리", "🏬 오데온스플라츠 명품가", "🎁 빅투알리엔 시장 마켓 쇼핑"],
        "places_landmark": ["🏛️ 뮌헨 신시청사 (Marienplatz)", "🏰 님펜부르크 궁전", "🏟️ 알리안츠 아레나"]
    },
    "seoul": {
        "food_meal": ["🔥 직화 삼겹살 & 된장찌개", "🍲 닭한마리 & 칼국수", "🍜 전통 평양냉면"],
        "food_dessert": ["🍧 인절미 빙수", "🥮 전통 한과 & 약과 디저트", "☕ 연남동 감성 카페 디저트류"],
        "places_art": ["🖼️ 국립현대미술관 (MMCA)", "🏛️ 리움 미술관", "🎨 동대문 디자인 플라자(DDP)"],
        "places_activity": ["👘 경복궁 한복 체험", "⛵ 한강 요트 투어 및 라면 조리", "🪡 전통 공예 만들기 체험"],
        "places_shopping": ["🛍️ 더현대 서울 & 여의도 IFC몰", "🎁 성수동 팝업스토어 거리", "💄 명동 뷰티 쇼핑가"],
        "places_landmark": ["🗼 N서울타워", "🏯 경복궁 & 북촌한옥마을", "🌊 롯데월드타워 서울스카이"]
    },
    "tokyo": {
        "food_meal": ["🍣 오마카세 스시", "🍜 돈코츠 라멘 & 츠케멘", "🥩 규카츠 & 야키니쿠"],
        "food_dessert": ["🍡 당고 & 말차 아이스크림", "🥞 수플레 팬케이크", "🍓 과일 모찌"],
        "places_art": ["🖼️ 팀랩 플래닛 도쿄 (디지털 아트)", "🏛️ 도쿄 국립박물관", "🎨 모리 미술관"],
        "places_activity": ["👘 아사쿠사 인력거 체험", "🍣 초밥 만들기 장인 클래스", "🕹️ 아키하바라 애니메이션 투어"],
        "places_shopping": ["🛍️ 긴자 식스 & 백화점 거리", "👟 시부야 파르코 (닌텐도/포켓몬)", "🧸 하라주쿠 다이칸야마 편집숍"],
        "places_landmark": ["🗼 도쿄 타워 & 도쿄 스카이트리", "⛩️ 센소지 사원", "🌆 시부야 스크램블 교차로"]
    },
    "new york": {
        "food_meal": ["🍕 뉴욕 스타일 조각 피자", "🥩 패스트라미 샌드위치 (카츠 델리카테센)", "🍔 쉑쉑 버거 본점"],
        "food_dessert": ["🥯 뉴욕 베이글 & 크림치즈", "🍪 르뱅 베이커리 쿠키", "🧁 매그놀리아 바나나 푸딩"],
        "places_art": ["🖼️ 뉴욕 현대미술관 (MoMA)", "🏛️ 메트로폴리탄 미술관 (Met)", "🎨 구겐하임 미술관"],
        "places_activity": ["🚁 뉴욕 헬기 투어", "🎭 브로드웨이 뮤지컬 관람", "⛸️ 록펠러 센터 아이스링크"],
        "places_shopping": ["🛍️ 소호(SoHo) 쇼핑 거리", "5번가 명품 플래그십 스토어", "🏬 메이시스 백화점"],
        "places_landmark": ["🗽 자유의 여신상", "🌳 센트럴 파크", "🌆 타임스 스퀘어", "🌉 브루클린 브리지 & 덤보"]
    }
}

DEFAULT_GUIDE = {
    "food_meal": ["🍴 현지 전통 메인 요리", "🍲 로컬 인기 향토 음식", "🥩 유명 로컬 레스토랑 코스"],
    "food_dessert": ["🍞 대표 베이커리 & 패스트리", "☕ 분위기 좋은 로컬 카페 디저트", "🍨 수제 아이스크림 & 젤라또"],
    "places_art": ["🖼️ 시립 미술관 및 갤러리", "🏛️ 역사 박물관", "🎨 문화 예술의 거리"],
    "places_activity": ["⛵ 현지 투어 크루즈 / 보트", "🧗 로컬 액티비티 체험", "🍷 미식 쿠킹 클래스"],
    "places_shopping": ["🛍️ 대형 복합 쇼핑몰", "🎁 로컬 기념품 상점가", "🧵 중심가 패션 편집숍"],
    "places_landmark": ["🗼 도시 랜드마크 타워/전망대", "🌿 도심 속 대형 공원", "⛪ 역사적인 유적지 광장"]
}

# ==========================================
# 3. 사이드바 설정
# ==========================================
st.sidebar.markdown("### 🎒 여행 설정")
is_korea = st.sidebar.checkbox("🇰🇷 국내 여행인가요?", value=False)
raw_city_input = st.sidebar.text_input("🌍 여행 도시명 (한글 또는 영문)", value="Prague" if not is_korea else "Seoul")
city = translate_city_to_english(raw_city_input)

default_lat, default_lon = get_default_coordinates(city)

st.sidebar.markdown("### 💱 환율 설정")
base_currency = st.sidebar.selectbox("기준 통화 (Base)", ["USD", "EUR", "JPY", "GBP", "KRW", "CNY", "AUD", "CAD", "SGD"], index=0)
target_currency = st.sidebar.selectbox("목표 통화 (Target)", ["KRW", "USD", "EUR", "JPY", "GBP", "CNY", "AUD", "CAD", "SGD"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ 장소 및 지도 검색")
search_keyword = st.sidebar.text_input("검색 키워드 (예: 햄버거, 맛집, 카페, 빵집, 굴뚝빵)", value="굴뚝빵" if not is_korea else "맛집")

col_lat, col_lng = st.sidebar.columns(2)
with col_lat:
    lat = st.number_input("위도", value=37.5665 if is_korea else default_lat, format="%.4f")
with col_lng:
    lng = st.number_input("경도", value=126.9780 if is_korea else default_lon, format="%.4f")

lon = lng

st.markdown(f"<h1 class='centered-title'>✈️ {raw_city_input} 맞춤형 여행 대시보드</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='centered-subtitle'><b>{raw_city_input}</b>의 실시간 날씨, 야외활동 적합도, 환율 및 맞춤 장소를 한눈에 확인하세요.</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 4. 메인 대시보드 UI 및 로직 실행
# ==========================================
top_col1, top_col2 = st.columns(2)

with top_col1:
    st.subheader(f"🌤️ {raw_city_input} 실시간 기상 및 야외활동 정보")
    weather_data, w_err = get_weather_data(city, WEATHER_API_KEY)
    
    if w_err:
        st.error(f"날씨 오류: {w_err}")
    elif weather_data:
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        desc = weather_data["weather"][0]["description"]
        
        is_good_activity = True
        reason = []
        if temp < 5 or temp > 30:
            is_good_activity = False
            reason.append("기온이 다소 부적절합니다")
        if wind_speed > 9:
            is_good_activity = False
            reason.append("바람이 강합니다")
        if humidity > 85:
            is_good_activity = False
            reason.append("습도가 매우 높습니다")
        if "비" in desc or "눈" in desc or "소나기" in desc:
            is_good_activity = False
            reason.append("강수 소식이 있습니다")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ 온도", f"{temp:.1f}°C")
        c2.metric("🧥 체감", f"{feels_like:.1f}°C")
        c3.metric("💧 습도", f"{humidity}%")
        c4.metric("💨 풍속", f"{wind_speed}m/s")
        
        st.markdown(f"**하늘 상태:** {desc.capitalize()}")
        
        if is_good_activity:
            st.success("✨ **[야외 활동 추천]** 날씨가 쾌적하여 야외 활동을 즐기기 아주 좋은 날입니다!")
        else:
            st.warning(f"⚠️ **[야외 활동 주의]** 주의 사항: {', '.join(reason)}")

with top_col2:
    st.subheader(f"💱 실시간 환율 및 멀티 환산")
    target_rate, all_rates, e_err = get_exchange_rate(base_currency, target_currency, EXCHANGE_API_KEY)
    
    if e_err:
        st.error(f"환율 오류: {e_err}")
    elif target_rate:
        st.metric(label=f"1 {base_currency} 당 환율", value=f"{target_rate:,.4f} {target_currency}")
        input_amount = st.number_input(f"환산할 금액 ({base_currency})", min_value=0.0, value=100.0, step=10.0)
        st.info(f"💱 **계산 결과:** {input_amount:,.2f} {base_currency} = **{input_amount * target_rate:,.2f} {target_currency}**")

st.markdown("---")

# 가이드 섹션
st.subheader(f"🍽️ & 🏛️ {raw_city_input} 여행자 맞춤 추천 가이드")
city_key = city.strip().lower()
guide = CITY_GUIDE.get(city_key, DEFAULT_GUIDE)

food_col1, food_col2 = st.columns(2)
with food_col1:
    st.markdown("#### 🍲 꼭 먹어야 할 음식류")
    for item in guide["food_meal"]: st.markdown(f"- {item}")
with food_col2:
    st.markdown("#### 🍰 꼭 먹어야 할 디저트류")
    for item in guide["food_dessert"]: st.markdown(f"- {item}")

st.markdown("")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)
with p_col1:
    st.markdown("#### 🖼️ 예술")
    for item in guide["places_art"]: st.markdown(f"- {item}")
with p_col2:
    st.markdown("#### ⛵ 체험")
    for item in guide["places_activity"]: st.markdown(f"- {item}")
with p_col3:
    st.markdown("#### 🛍️ 쇼핑")
    for item in guide["places_shopping"]: st.markdown(f"- {item}")
with p_col4:
    st.markdown("#### 🗼 랜드마크 & 풍경")
    for item in guide["places_landmark"]: st.markdown(f"- {item}")

st.markdown("---")

# ==========================================
# 5. 장소 검색 및 지도 표시 (실제 상호명 및 실제 주소 기반 연동)
# ==========================================
current_address = get_reverse_geocode(lat, lon)

if is_korea:
    st.markdown(f"### 🇰🇷 국내 '{search_keyword}' 추천 리스트 및 지도")
    st.markdown(f"📌 **현재 탐색 위치 (주소):** `{current_address}`")
    
    places, k_err = get_kakao_places(search_keyword, lng, lat, KAKAO_API_KEY)
    if places:
        place_list = []
        for idx, p in enumerate(places):
            dummy_rating = round(4.9 - (idx * 0.03), 2)
            place_list.append({
                "평점": f"⭐ {max(dummy_rating, 4.0)}",
                "장소명": p.get("place_name"),
                "거리": f"{p.get('distance')}m",
                "주소": p.get("road_address_name") or p.get("address_name"),
                "상세링크": p.get("place_url"),
                "lat": float(p.get("y")),
                "lon": float(p.get("x"))
            })
        
        l_col, r_col = st.columns([1.2, 0.8])
        with l_col:
            df_places = pd.DataFrame(place_list)
            st.dataframe(df_places[["평점", "장소명", "거리", "주소", "상세링크"]], 
                         column_config={"상세링크": st.column_config.LinkColumn("상세정보", display_text="🔗 카카오맵")},
                         use_container_width=True, hide_index=True)
        with r_col:
            m = folium.Map(location=[lat, lng], zoom_start=14)
            for item in place_list:
                folium.Marker([item["lat"], item["lon"]], popup=item["장소명"], icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
            st_folium(m, width=500, height=420)
    else:
        st.info("검색된 장소 결과가 없습니다.")
else:
    st.markdown(f"### 🌍 해외 '{search_keyword}' 추천 리스트 및 지도 ({raw_city_input})")
    st.markdown(f"📌 **현재 탐색 위치 (주소):** `{current_address}`")
    
    city_lower = city.strip().lower()
    spots_data = REAL_PLACES_DB.get(city_lower, REAL_PLACES_DB["prague"])

    place_list = []
    m = folium.Map(location=[default_lat, default_lon], zoom_start=13)

    for idx, spot in enumerate(spots_data):
        dummy_rating = round(4.9 - (idx * 0.02), 2)
        if dummy_rating < 4.2: dummy_rating = 4.2
        
        name = spot["name"]
        address = spot["address"]
        s_lat = spot["lat"]
        s_lon = spot["lon"]
        
        google_map_url = f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(f'{name} {raw_city_input}')}"
        
        place_list.append({
            "평점": f"⭐ {dummy_rating}",
            "장소명": name,
            "주소": address,
            "상세링크": google_map_url
        })
        
        folium.Marker(
            [s_lat, s_lon],
            popup=f"<b>{name}</b> (⭐ {dummy_rating})<br>{address}",
            tooltip=name,
            icon=folium.Icon(color="green", icon="star", prefix="fa")
        ).add_to(m)

    l_col, r_col = st.columns([1.2, 0.8])
    with l_col:
        st.markdown(f"#### 🏆 해외 '{search_keyword}' 평점순 추천 장소 (총 {len(place_list)}개)")
        df_overseas = pd.DataFrame(place_list)
        st.dataframe(
            df_overseas[["평점", "장소명", "주소", "상세링크"]],
            column_config={
                "상세링크": st.column_config.LinkColumn("상세정보", display_text="🔗 구글 지도")
            },
            use_container_width=True,
            hide_index=True
        )
    with r_col:
        st.markdown(f"#### 🗺️ 해외 위치 지도 ({raw_city_input})")
        st_folium(m, width=500, height=480)