import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv() 
WEATHER_API_KEY = os.getenv("openweather_API_key")
EXCHANGE_API_KEY = os.getenv("exchange_API_key")

# 2. 페이지 설정
st.set_page_config(page_title="글로벌 비즈니스 & 여행 대시보드", page_icon="🌍", layout="wide")

# 3. 커스텀 CSS (목록바 글자 크기 대폭 확대 및 자몽색 테두리)
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F4F9F4;
}
/* 세계지도 배경에 연두색 필터 및 투명도 적용 */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%;
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg");
    background-size: cover;
    background-position: center;
    opacity: 0.25;
    filter: invert(75%) sepia(40%) saturate(600%) hue-rotate(50deg);
    z-index: 0;
    pointer-events: none;
}
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}

/* 셀렉트박스 글자 크기를 더 크게 키우고 박스 높이 조정 */
.stSelectbox div[data-baseweb="select"] {
    border-color: #FF7F50 !important; /* 자몽색 테두리 */
    border-width: 2px !important;
    border-radius: 12px !important;
    min-height: 75px !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div {
    font-size: 1.8rem !important; /* 글자 크기 대폭 확대 */
    font-weight: 700 !important;
}

.info-card {
    background-color: rgba(248, 249, 250, 0.95);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    height: 100%;
    position: relative;
    z-index: 1;
}
.metric-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin-top: 10px;
}
.metric-box {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    margin: 5px;
    flex: 1;
    min-width: 100px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.metric-value {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333333;
}
.metric-label {
    font-size: 0.9rem;
    color: #666666;
    margin-top: 5px;
}
.analysis-box {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 6px solid #4A90E2;
    height: 100%;
}
.analysis-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #2C3E50;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.analysis-content {
    font-size: 0.95rem;
    color: #4A5568;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# 4. 지원 국가 데이터 (여행용 치안 정보 추가 완료)
LOCATION_DATA = {
    "미국 (뉴욕)": {
        "city": "New York", "currency": "USD", "symbol": "$", 
        "base_rate": 1350, "price_level": "약 140% (주거 및 외식비 높음)", 
        "trade_export": "자동차, 반도체, 기계류, 석유제품",
        "trade_import": "원유, 천연가스, 항공기, 농산물",
        "trade_culture": "결론 우선 직설적 화법 선호, 계약서 상의 문서 증빙과 준법 정신을 극도로 중시",
        "trade_economy": "견조한 소비 중심 성장이나 고금리 장기화로 인한 자금 조달 비용 부담 존재",
        "packing_tip": "멀티탭(110V), 편한 운동화, 일교차 겉옷",
        "safety_info": "전반적으로 안전하나 심야 시간대의 지하철역이나 우범 지역(할렘가 일부 등)은 단독 통행을 피하고 소매치기 주의",
        "must_visit": "센트럴 파크, 타임스퀘어, 브로드웨이",
        "images": [
            "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "멕시코 (멕시코시티)": {
        "city": "Mexico City", "currency": "MXN", "symbol": "$", 
        "base_rate": 80, "price_level": "약 70% (현지 물가와 식비가 비교적 저렴함)", 
        "trade_export": "자동차, 전자부품, 철강, 의료기기",
        "trade_import": "원유, 정밀기기, 화학공업제품, 농축산물",
        "trade_culture": "개인적인 신뢰와 유대감(파네르소)을 중시하며, 악수와 인사를 나누는 정중한 태도 필요",
        "trade_economy": "미국 인접 효과(니어쇼어링)로 제조업 및 의료기기·제약 분야 투자가 급증하는 유망 시장",
        "packing_tip": "고고도 대비 자외선 차단제, 가벼운 외투(일교차 큼), 멀티어댑터",
        "safety_info": "치안 주의 지역으로, 공식 택시(디시오) 이용 필수 및 야간 인적이 드문 장소나 대중교통 이용 시 각별한 주의 요망",
        "must_visit": "소칼로 광장, 차풀테페크 공장, 프리다 칼로 미술관",
        "images": [
            "https://images.unsplash.com/photo-1512813266185-3b1f5fc23015?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1585464671268-904c22c26d8e?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "콜롬비아 (보고타)": {
        "city": "Bogota", "currency": "COP", "symbol": "$", 
        "base_rate": 0.35, "price_level": "약 65% (의료기기 및 제약 공공 조달 수요 높음)", 
        "trade_export": "자동차 부품, 석유화학제품, 철강, 기계류",
        "trade_import": "의료기기, 의약품, 정밀화학, 방송통신기기",
        "trade_culture": "격식 있는 호칭과 정중한 태도를 중시하며, 직접적인 거절보다는 우회적인 표현 사용",
        "trade_economy": "중남미 내 대표적인 보건의료 허브로 제약 및 첨단 의료기기 수입 수요가 매우 활발함",
        "packing_tip": "고산지대 대비 우산(소나기 잦음), 따뜻한 겉옷(선선한 날씨)",
        "safety_info": "소매치기 및 날치기 범죄가 빈번하므로 고가품(귀금속, 스마트폰) 노출을 자제하고 안전한 구역 위주로 이동 권장",
        "must_visit": "몬세라테 언덕, 황금 박물관, 볼리바르 광장",
        "images": [
            "https://images.unsplash.com/photo-1589909202874-17f975762af0?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1583321500900-82807e45c03e?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1531737704602-44287528e1a1?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "칠레 (산티아고)": {
        "city": "Santiago", "currency": "CLP", "symbol": "$", 
        "base_rate": 1.4, "price_level": "약 80% (남미에서 경제적 안정성과 투명성이 높은 국가)", 
        "trade_export": "자동차, 기계류, 석유제품, 철강",
        "trade_import": "의료기기, 의약품, 광산용 장비, IT 기기",
        "trade_culture": "시간 약속을 철저히 지키며 비즈니스 매너가 매우 서구적이고 투명함",
        "trade_economy": "공공 및 민간 병원 인프라 현대화로 첨단 의료기기 및 제약 분야 수입 의존도가 높음",
        "packing_tip": "자외선 차단제, 선글라스, 건조한 날씨 대비 보습 용품",
        "safety_info": "남미 국가 중 비교적 치안이 안정적이나 관광지 및 지하철 내 소매치기, 차량털이 범죄에 주의 필요",
        "must_visit": "산타 루시아 언덕, 아라스 광장,스카이 코스타네라",
        "images": [
            "https://images.unsplash.com/photo-1512813266185-3b1f5fc23015?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "오스트리아 (비엔나)": {
        "city": "Vienna", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 115% (서유럽 평균 수준의 높은 삶의 질과 물가)", 
        "trade_export": "기계, 자동차 부품, 철강, 전기기기",
        "trade_import": "의약품, 의료기기, 정밀기계, 에너지",
        "trade_culture": "공식 직함과 학위를 중요하게 여기며, 철저한 서면 계약과 격식 있는 태도 요구",
        "trade_economy": "중동부 유럽을 잇는 비즈니스 거점이며 안정적인 제조업과 제약·의료 산업 인프라 보유",
        "packing_tip": "EU 규격 어댑터, 클래식 공연 관람용 단정한 옷차림, 편한 걷기용 신발",
        "safety_info": "세계에서 가장 안전한 도시 중 하나로 꼽히나 주요 관광지 주변 소매치기만 주의하면 안전함",
        "must_visit": "벨베데레 궁전, 쇤브룬 궁전, 비엔나 국립 오페라극장",
        "images": [
            "https://images.unsplash.com/photo-1516550893885-303cefc47b36?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1543785734-4b6e564642f8?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "스위스 (취리히)": {
        "city": "Zurich", "currency": "CHF", "symbol": "CHF", 
        "base_rate": 1500, "price_level": "약 160% (세계 최고 수준의 외식비 및 물가)", 
        "trade_export": "정밀기기, 의약품, 기계, 시계",
        "trade_import": "귀금속, 의약품 원료, 첨단 의료기기, 화학제품",
        "trade_culture": "시간 엄수가 절대적이며 정확성, 신뢰성, 철저한 문서 기록을 극도로 중시",
        "trade_economy": "제약 및 바이오, 정밀 의료기기 산업의 세계적 중심지로 강력한 경제력을 자랑함",
        "packing_tip": "J타입(스위스 전용) 어댑터, 고가의 물가 대비 여유로운 예산 준비",
        "safety_info": "치안 상태가 매우 우수하며 범죄율이 낮아 밤에도 비교적 안전하게 다닐 수 있음",
        "must_visit": "취리히 호수, 반호프슈트라세, 구시가지(알트슈타트)",
        "images": [
            "https://images.unsplash.com/photo-1515488764276-beab7607c1e6?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1502101872923-d48509bff386?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1527668707036-7c32725d2038?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "네덜란드 (암스테르담)": {
        "city": "Amsterdam", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 120% (주거비와 서비스 물가가 높은 편)", 
        "trade_export": "반도체 장비, 기계, 화학제품, 원예 농산물",
        "trade_import": "전자제품, 원유, 의료기기, 의약품",
        "trade_culture": "매우 직설적이고 실용적인 화법을 구사하며 회의에서 빠른 결론과 효율성 추구",
        "trade_economy": "유럽의 물류·유통 허브이며 ASML 등 첨단 반도체 및 의료 기술 인프라가 매우 발달함",
        "packing_tip": "방수 자켓(비와 바람이 잦음), 자전거 전용 도로 주의용 운동화",
        "safety_info": "치안은 양호하나 자전거 전용 도로가 많아 보행 시 교통사고에 유의해야 하며 혼잡한 구역 소매치기 주의",
        "must_visit": "반 고흐 미술관, 국립 미술관, 운하 크루즈",
        "images": [
            "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-158321500900-82807e45c03e?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "이탈리아 (로마)": {
        "city": "Rome", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 105% (관광지는 비싸지만 일반 물가는 합리적임)", 
        "trade_export": "기계류, 자동차, 패션/의류, 의료기기",
        "trade_import": "에너지(천연가스/원유), 의약품, 철강, 전자부품",
        "trade_culture": "인간관계를 중요하게 생각하며 공식 미팅 전 가벼운 스몰토크와 친밀감 형성이 유리함",
        "trade_economy": "관광업 회복과 더불어 공공 보건 의료 부문의 의료기기 현대화 사업이 꾸준히 진행 중",
        "packing_tip": "소매치기 방지 백팩, 유적지 관람용 편한 운동화, 선글라스",
        "safety_info": "관광객을 노린 소매치기, 날치기 및 사기꾼(팔찌 강매 등)이 매우 많으므로 소지품 관리에 각별한 주의 필요",
        "must_visit": "콜로세움, 트레비 분수, 바티칸 시국",
        "images": [
            "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1525874684015-58379d421a52?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "영국 (런던)": {
        "city": "London", "currency": "GBP", "symbol": "£", 
        "base_rate": 1700, "price_level": "약 145% (교통비/주거비 최고 수준)", 
        "trade_export": "승용차, 의약품, 바이오, 기계류",
        "trade_import": "원유, 천연가스, 기계장치, 귀금속",
        "trade_culture": "우회적이고 정중한 화법 사용, 비즈니스 네트워킹과 신용도 매우 중시",
        "trade_economy": "서비스 산업 중심의 경제이나 고금리 및 브렉시트 여파로 성장 둔화 압력",
        "packing_tip": "BF타입 어댑터, 튼튼한 3단 우산, 컨택리스 카드",
        "safety_info": "치안은 비교적 안전하나 번화가나 지하철 내에서 오토바이 날치기나 소매치기 범죄 조심",
        "must_visit": "대영박물관, 런던 아이, 타워 브리지",
        "images": [
            "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1506579309014-c3a444a35413?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "포르투갈 (리스본)": {
        "city": "Lisbon", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 75% (서유럽 국가 중 물가와 식비가 가장 저렴한 편)", 
        "trade_export": "기계, 자동차 부품, 와인/농산물, 섬유",
        "trade_import": "화학제품, 기계류, 석유제품, 의료기기",
        "trade_culture": "예의를 갖추고 친근하며, 여유롭고 완만한 속도의 비즈니스 진행 선호",
        "trade_economy": "스타트업 및 IT 허브로 급부상 중이며 관광 및 헬스케어 인프라 투자 확대 추세",
        "packing_tip": "편한 운동화(언덕과 돌길이 많음), 선글라스, 가벼운 외투",
        "safety_info": "유럽에서 손꼽힐 정도로 치안이 안전한 편이나 트램 안이나 밀집된 관광지에서 소매치기 주의",
        "must_visit": "제이루무 수도원, 벨렘탑, 코메르시우 광장",
        "images": [
            "https://images.unsplash.com/photo-1585208798174-6ed3c4041a04?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1513603175902-3f7d1b54f494?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1548711621-16d7a4659f1e?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "독일 (베를린)": {
        "city": "Berlin", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 110% (마트 물가는 저렴함)", 
        "trade_export": "자동차부품, 배터리, 화학제품, 기계",
        "trade_import": "천연가스, 의약품, 전자제품, 원유",
        "trade_culture": "엄격한 규정과 절차 준수, 공사 구분 명확, 철저한 사전 서면 검토 요구",
        "trade_economy": "제조업 부진 및 에너지 전환 비용 증가로 인해 완만한 성장 정체 국면",
        "packing_tip": "EU 어댑터, 방수 바람막이, 동전 지갑",
        "safety_info": "치안 상태가 매우 안전하나 베를린 등 대도시 기차역 주변이나 야간 번화가에서는 소지품 주의",
        "must_visit": "브란덴부르크 문, 베를린 장벽, 박물관 섬",
        "images": [
            "https://images.unsplash.com/photo-1560969184-10fe8719e047?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "일본 (도쿄)": {
        "city": "Tokyo", "currency": "JPY", "symbol": "¥", 
        "base_rate": 900, "price_level": "약 90% (엔저로 체감 물가 낮음)", 
        "trade_export": "철강, 반도체 장비, 전자부품, 자동차",
        "trade_import": "액화천연가스(LNG), 원유, 의류, 식료품",
        "trade_culture": "격식 있는 호칭과 철저한 비즈니스 예절(명함 교환 등), 신뢰 구축 중시",
        "trade_economy": "완만한 임금 상승과 관광객 유입으로 내수 회복세이나 엔화 변동성 주의",
        "packing_tip": "동전 지갑, 돼지코(110V), 숙소용 슬리퍼",
        "safety_info": "세계에서 가장 치안이 안전한 국가 중 하나로 밤늦은 귀가도 안전함 (가끔 지진 발생 대비 필요)",
        "must_visit": "시부야 스크램블, 센소지, 도쿄타워",
        "images": [
            "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "호주 (시드니)": {
        "city": "Sydney", "currency": "AUD", "symbol": "$", 
        "base_rate": 880, "price_level": "약 130% (외식/인건비 높음)", 
        "trade_export": "석유제품, 자동차, 기계, 정밀기기",
        "trade_import": "철광석, 석탄, 천연가스, 여행·교육 서비스",
        "trade_culture": "워라밸을 중시하며 수평적이고 실용적인 커뮤니케이션 선호",
        "trade_economy": "자원 수출 호조를 보이고 있으나 높은 인플레이션과 금리 압박 존재",
        "packing_tip": "O타입 어댑터, 자외선 차단제, 수영복",
        "safety_info": "치안이 매우 안정적이나 해변가나 도심 유흥가에서 심야 시간대 과도한 음주자 간 시비 조심",
        "must_visit": "오페라 하우스, 하버브리지, 본다이 비치",
        "images": [
            "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "브라질 (상파울루)": {
        "city": "Sao Paulo", "currency": "BRL", "symbol": "R$", 
        "base_rate": 270, "price_level": "약 75% (공산품은 비싸지만 현지 식품 물가는 저렴함)", 
        "trade_export": "철강, 자동차 부품, 화학제품, 전자제품",
        "trade_import": "대두, 철광석, 원유, 육류(소고기/가금류), 커피",
        "trade_culture": "따뜻하고 정중한 인사와 악수를 중시하며, 서두르지 않는 여유로운 비즈니스 스타일",
        "trade_economy": "자원 및 농축산물 수출 대국이나 높은 인플레이션과 환율 변동성에 주의 필요",
        "packing_tip": "변압기(대부분 110V/220V 혼용이나 확인 필요), 소매치기 방지 백팩, 모기 기피제",
        "safety_info": "강도 및 날치기 위험이 높은 지역이 많으므로 고가 스마트폰 노출 금지 및 야간 단독 외출 절대 자제",
        "must_visit": "파울리스타 대로, 이비라푸에라 공장, 상파울루 미술관",
        "images": [
            "https://images.unsplash.com/photo-1531737704602-44287528e1a1?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1512813266185-3b1f5fc23015?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "아르헨티나 (부에노스아이레스)": {
        "city": "Buenos Aires", "currency": "ARS", "symbol": "$", 
        "base_rate": 1.5, "price_level": "약 60% (외국인 환율 체감상 물가가 매우 저렴하게 느껴짐)", 
        "trade_export": "기계류, 자동차 부품, 화학제품, 플라스틱",
        "trade_import": "곡물(대두/밀), 육류, 리튬, 원유 및 가스",
        "trade_culture": "친근한 스킨십(볼 키스 등)과 대화를 선호하며, 개인적인 유대감을 쌓은 뒤 거래 진행",
        "trade_economy": "만성적인 고인플레이션과 복잡한 외환 규제가 존재하므로 대금 결제 조건 리스크 관리 필수",
        "packing_tip": "C/I 타입 겸용 어댑터, 넉넉한 현금(달러 선호), 편한 산책화",
        "safety_info": "오토바이 소매치기 및 날치기가 빈번하므로 길거리에서 스마트폰을 꺼내 들고 통화하는 행위 주의",
        "must_visit": "라보카(캄니토), 5월 광장, 오벨리스크",
        "images": [
            "https://images.unsplash.com/photo-1589909202874-17f975762af0?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1612294037637-ec32374e2846?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1583321500900-82807e45c03e?auto=format&fit=crop&w=600&q=80"
        ]
    }
}

# 5. API 호출 함수 (캐싱)
@st.cache_data(ttl=600)
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=3600)
def get_exchange_rates(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 6. 상단 선택기 중앙 배치 및 크기 조절
col_space1, col_sel1, col_sel2, col_space2 = st.columns([2.0, 1.2, 1.2, 2.0])
with col_sel1:
    purpose = st.selectbox("🎯 사용 용도", ["여행용 🎒", "무역 실무용 💼"])
with col_sel2:
    selected_option = st.selectbox("✈️ 국가 및 도시", list(LOCATION_DATA.keys()))

target_city = LOCATION_DATA[selected_option]["city"]
target_currency = LOCATION_DATA[selected_option]["currency"]
currency_symbol = LOCATION_DATA[selected_option]["symbol"]
country_name = selected_option.split(' ')[0]

st.title(f"🌍 {country_name} 실시간 대시보드")
st.markdown("---")

col1, col2 = st.columns(2)

# ------------------ [좌측: 날씨 정보] ------------------
with col1:
    st.subheader(f"🌤️ {target_city.upper()} 날씨 정보")
    w_data = None
    if not WEATHER_API_KEY:
        st.error("날씨 API 키가 설정되지 않았습니다.")
    else:
        w_data = get_weather(target_city, WEATHER_API_KEY)
        if w_data:
            temp = w_data['main']['temp']
            feels_like = w_data['main']['feels_like']
            humidity = w_data['main']['humidity']
            wind_speed = w_data['wind']['speed']
            description = w_data['weather'][0]['description']
            icon_code = w_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            
            st.markdown(f"**현재 날씨:** {temp:.1f}°C, {description}")
            st.image(icon_url, width=80)
            
            weather_html = f"""
<div class="info-card">
<div class="metric-container">
<div class="metric-box">
<div class="metric-value">{feels_like:.1f}°C</div>
<div class="metric-label">체감 온도</div>
</div>
<div class="metric-box">
<div class="metric-value">{humidity}%</div>
<div class="metric-label">습도</div>
</div>
<div class="metric-box">
<div class="metric-value">{wind_speed} m/s</div>
<div class="metric-label">풍속</div>
</div>
</div>
</div>
"""
            st.markdown(weather_html, unsafe_allow_html=True)
        else:
            st.error("날씨 정보를 불러오지 못했습니다.")

# ------------------ [우측: 환율 정보] ------------------
with col2:
    st.subheader(f"💱 {country_name} 환율 정보")
    target_to_krw = 0 
    e_data = None
    
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키가 설정되지 않았습니다.")
    else:
        e_data = get_exchange_rates(EXCHANGE_API_KEY)
        if e_data and e_data.get("result") == "success":
            rates = e_data['conversion_rates']
            
            usd_to_krw = rates['KRW']
            target_to_krw = rates['KRW'] / rates[target_currency]
            
            display_rate = target_to_krw * 100 if target_currency == 'JPY' else target_to_krw
            display_unit = "100 JPY" if target_currency == 'JPY' else f"1 {target_currency}"
            
            st.markdown(f"**업데이트 기준일:** {e_data['time_last_update_utc'][:16]}")
            st.markdown("<div style='font-size: 65px; height: 80px; display: flex; align-items: center; margin-bottom: 1rem;'>💵</div>", unsafe_allow_html=True) 
            
            exchange_html = f"""
<div class="info-card">
<div class="metric-container">
<div class="metric-box">
<div class="metric-value">{display_rate:,.2f} 원</div>
<div class="metric-label">선택 국가 ({display_unit})</div>
</div>
<div class="metric-box">
<div class="metric-value">{usd_to_krw:,.2f} 원</div>
<div class="metric-label">기본 달러 (1 USD)</div>
</div>
</div>
</div>
"""
            st.markdown(exchange_html, unsafe_allow_html=True)

# ------------------ [맞춤형 정보 제공 (치안 상황 추가 및 5분할 배치)] ------------------
if w_data and e_data:
    st.markdown(f"### 📊 {purpose} 맞춤 심층 분석")
    
    compare_rate = display_rate
    base_rate = LOCATION_DATA[selected_option]['base_rate']
    
    if purpose == "여행용 🎒":
        weather_rec = "야외 활동을 하기에 쾌적하고 무난한 날씨입니다. 가벼운 발걸음으로 도시를 둘러보세요."
        if "비" in description or "눈" in description or "흐림" in description:
            weather_rec = "기상 상태가 좋지 않거나 비/눈 소식이 있습니다. 야외 일정보다는 박물관, 미술관 등 **실내 위주의 일정**을 강력히 추천합니다!"
        elif temp > 28:
            weather_rec = "기온이 높아 다소 덥습니다. 한낮에는 무리한 야외 활동을 피하시고, 충분한 수분 섭취와 그늘 휴식이 필수입니다."
        elif temp < 5:
            weather_rec = "날씨가 쌀쌀하거나 추우니 따뜻한 방한용품을 꼭 챙기시고 실내 위주로 동선을 짜세요."
            
        if compare_rate > base_rate * 1.02:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선보다 높은 **원화 약세 구간**입니다. 현지 체류 시 예산 관리에 유의하세요."
        elif compare_rate < base_rate * 0.98:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선보다 낮은 **원화 강세 구간**입니다. 쇼핑과 기념품 구매를 즐기기 매우 좋은 시기입니다!"
        else:
            rate_rec = "현재 환율이 평년 수준을 유지하고 있어 계획하신 예산대로 안정적인 여행이 가능합니다."

        # 💡 여행용 5개 항목을 가로로 나란히 배치 (st.columns(5))
        col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
        
        with col_t1:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">🌤️ 날씨 가이드</div>
                <div class="analysis-content">{weather_rec}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #38A169;">
                <div class="analysis-title">💵 환율 예산 팁</div>
                <div class="analysis-content">{rate_rec}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🛒 물가 및 준비물</div>
                <div class="analysis-content">
                    <b>• 물가:</b> {LOCATION_DATA[selected_option]['price_level']}<br><br>
                    <b>• 준비물:</b> {LOCATION_DATA[selected_option]['packing_tip']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #E53E3E;">
                <div class="analysis-title">🚨 현재 치안 상황</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['safety_info']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t5:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #805AD5;">
                <div class="analysis-title">📍 추천 핫플레이스</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['must_visit']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 📸 {country_name} 추천 핫플레이스 포토 갤러리")
        img_cols = st.columns(3)
        city_images = LOCATION_DATA[selected_option]["images"]
        
        for idx, col in enumerate(img_cols):
            with col:
                st.image(city_images[idx], use_container_width=True)
        
    else: # 무역 실무용 (4분할 가로 나란히 배치 유지)
        if compare_rate > base_rate * 1.02:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 상회하는 <b>원화 약세장</b>: <b>수출 기업</b> 가격 경쟁력 확보 유리, <b>수입 기업</b> 원가 부담 증가로 환헤지 필수."
        elif compare_rate < base_rate * 0.98:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 하회하는 <b>원화 강세장</b>: <b>수입 기업</b> 원자재 단가 절감 유리, <b>수출 기업</b> 채산성 악화 대비 전략 필요."
        else:
            trade_rec = "현재 환율이 안정적인 박스권을 보이며 환 리스크 부담이 적어 평소 기준에 맞춘 안정적인 대외 거래가 가능합니다."

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #DD6B20;">
                <div class="analysis-title">📦 주요 수출/수입품</div>
                <div class="analysis-content">
                    <b>• 주요 수출품:</b><br>{LOCATION_DATA[selected_option]['trade_export']}<br><br>
                    <b>• 주요 수입품:</b><br>{LOCATION_DATA[selected_option]['trade_import']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">📊 현재 경제 상황</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_economy']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🤝 비즈니스 문화</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_culture']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #E53E3E;">
                <div class="analysis-title">📈 환율 기반 전략</div>
                <div class="analysis-content">{trade_rec}</div>
            </div>
            """, unsafe_allow_html=True)

# ------------------ [하단: 스위칭 환전 계산기] ------------------
st.markdown("---") 

if e_data and e_data.get("result") == "success":
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown(f"<h3 style='text-align: center;'>🧮 양방향 환전 계산기</h3>", unsafe_allow_html=True)
        
        calc_mode = st.radio("🔄 계산 방향 선택", [f"{target_currency} ➔ 원화(KRW)", f"원화(KRW) ➔ {target_currency}"], horizontal=True)
        
        if calc_mode.startswith(target_currency):
            input_amount = st.number_input(f"환전할 {country_name} 금액({target_currency})을 입력하세요:", min_value=0.0, value=100.0, step=10.0)
            krw_result = input_amount * target_to_krw
            st.success(f"예상 환전 금액: **{krw_result:,.0f} 원(KRW)**")
        else:
            input_amount = st.number_input(f"환전할 원화(KRW) 금액을 입력하세요:", min_value=0.0, value=100000.0, step=10000.0)
            target_result = input_amount / target_to_krw
            st.success(f"예상 환전 금액: **{currency_symbol} {target_result:,.2f}** ({target_currency})")