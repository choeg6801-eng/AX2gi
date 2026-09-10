import os
import base64
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="무역 직무 MBTI 테스트", page_icon="✈️", layout="centered")

current_dir = os.path.dirname(os.path.abspath(__file__))

# --- 스탠드형 지구본 SVG ---
globe_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <ellipse cx="250" cy="460" rx="90" ry="20" fill="#78909C"/>
  <ellipse cx="250" cy="455" rx="80" ry="16" fill="#90A4AE"/>
  <rect x="243" y="390" width="14" height="70" fill="#B0BEC5"/>
  <path d="M 250 80 A 185 185 0 0 1 250 420" fill="none" stroke="#78909C" stroke-width="18" stroke-linecap="round"/>
  <circle cx="250" cy="80" r="12" fill="#546E7A"/>
  <circle cx="250" cy="420" r="12" fill="#546E7A"/>
  <circle cx="250" cy="250" r="150" fill="#81D4FA"/>
  <ellipse cx="250" cy="250" rx="150" ry="60" fill="none" stroke="#B3E5FC" stroke-width="3" opacity="0.7"/>
  <ellipse cx="250" cy="250" rx="60" ry="150" fill="none" stroke="#B3E5FC" stroke-width="3" opacity="0.7"/>
  <line x1="100" y1="250" x2="400" y2="250" stroke="#B3E5FC" stroke-width="3" opacity="0.7"/>
  <line x1="250" y1="100" x2="250" y2="400" stroke="#B3E5FC" stroke-width="3" opacity="0.7"/>
  <path d="M 180 140 Q 210 130 230 160 Q 240 190 220 210 Q 190 220 170 190 Q 160 160 180 140 Z" fill="#A5D6A7"/>
  <path d="M 210 230 Q 240 220 250 250 Q 240 290 220 310 Q 190 320 200 270 Z" fill="#A5D6A7"/>
  <path d="M 270 140 Q 330 130 350 170 Q 360 210 320 230 Q 290 210 280 170 Z" fill="#A5D6A7"/>
  <path d="M 280 230 Q 320 220 330 260 Q 320 310 290 320 Q 270 290 280 230 Z" fill="#A5D6A7"/>
  <path d="M 330 310 Q 360 300 370 330 Q 350 350 330 340 Z" fill="#A5D6A7"/>
  <path d="M 140 180 A 130 130 0 0 1 220 130" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity="0.5"/>
</svg>"""
b64_globe = base64.b64encode(globe_svg.encode('utf-8')).decode('utf-8')

# --- UI 및 반응형 CSS 주입 ---
def apply_custom_ui():
    shinchan_plane_url = "https://media.tenor.com/2sP0wQ2o5u4AAAAi/crayon-shin-chan-shin-chan.gif"

    custom_css = f"""
    <style>
    /* 1. 정중앙에 50% 투명도로 배치되는 일러스트 지구본 배경 */
    [data-testid="stAppViewContainer"] {{
        background-color: #E0F7FA !important;
        background-image: linear-gradient(rgba(224, 247, 250, 0.5), rgba(224, 247, 250, 0.5)), url("data:image/svg+xml;base64,{b64_globe}") !important;
        background-position: center center !important;
        background-size: 520px !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}

    /* ⭐ 가독성 해결: 질문 및 결과가 담기는 컨테이너에 하얀색 반투명 배경 적용 ⭐ */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgba(255, 255, 255, 0.88) !important;
        border: none !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        padding: 10px;
    }}

    /* 3. 파스텔 자몽색 버튼 */
    div.stButton > button {{
        background-color: #FFB2A7 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease;
    }}
    div.stButton > button:hover {{
        background-color: #FF9B8A !important;
        transform: translateY(-2px);
    }}

    /* 4. 상단 우측 비행기 타는 짱구 애니메이션 */
    .shinchan-plane {{
        position: fixed;
        top: 20px;
        right: 25px;
        width: 125px;
        z-index: 99999;
        animation: airplane-fly 3s ease-in-out infinite alternate;
        pointer-events: none;
    }}
    @keyframes airplane-fly {{
        0% {{ transform: translateY(0px) rotate(-3deg); }}
        100% {{ transform: translateY(-12px) rotate(4deg); }}
    }}

    /* 5. 폰트/라디오 버튼 스타일 */
    .question-title {{ font-size: 1.25rem !important; font-weight: 700 !important; color: #1E293B !important; margin-bottom: 20px; }}
    div[data-testid="stRadio"] label p {{ font-size: 1.15rem !important; font-weight: 500 !important; color: #334155 !important; line-height: 1.6 !important; }}
    div[data-testid="stRadio"] label {{ margin-bottom: 12px !important; padding: 8px 12px !important; border-radius: 8px !important; cursor: pointer !important; }}
    div[data-testid="stRadio"] label:hover {{ background-color: rgba(0, 0, 0, 0.05) !important; }}
    div[data-testid="stRadio"] input[type="radio"], div[data-testid="stRadio"] [data-baseweb="radio"] div:first-child {{ transform: scale(1.4) !important; margin-right: 12px !important; }}

    @media screen and (max-width: 768px) {{
        [data-testid="stAppViewContainer"] {{ background-size: 320px !important; }}
        .shinchan-plane {{ width: 85px; top: 10px; right: 15px; }}
    }}
    </style>
    <img src="{shinchan_plane_url}" class="shinchan-plane" alt="Shinchan Plane">
    """
    st.markdown(custom_css, unsafe_allow_html=True)

apply_custom_ui()

# --- 문항 리스트 (직무 MBTI 20개 + 산업 매칭 10개 = 총 30개) ---
questions = [
    # --- 직무 MBTI 20문항 (E/I, S/N, T/F, J/P) ---
    {"q": "해외 전시회에 참가하게 되었습니다. 당신의 행동은?", "options": [{"text": "적극적으로 부스를 돌아다니며 새로운 바이어에게 먼저 말을 건다.", "type": "E"}, {"text": "우리 부스에 찾아오는 바이어를 맞이하며 깊이 있는 상담을 준비한다.", "type": "I"}]},
    {"q": "해외 바이어와 소통할 때 더 선호하는 방식은?", "options": [{"text": "즉각적인 피드백을 주고받을 수 있는 유선 통화나 화상 미팅", "type": "E"}, {"text": "내용을 꼼꼼하게 정리하고 기록으로 남길 수 있는 영문 이메일", "type": "I"}]},
    {"q": "새로운 해외 시장을 개척해야 할 때 당신의 첫걸음은?", "options": [{"text": "현지 에이전트나 지인 네트워크를 활용해 사람부터 만난다.", "type": "E"}, {"text": "KOTRA나 무역협회의 공신력 있는 시장 조사 보고서부터 정독한다.", "type": "I"}]},
    {"q": "팀 단위로 대형 수출 프로젝트를 진행할 때 당신은?", "options": [{"text": "외부 파트너 및 타 부서와 활발히 소통하며 전체 조율을 이끄는 역할", "type": "E"}, {"text": "데이터 분석과 정확한 계약 서류 작업을 도맡아 내실을 다지는 역할", "type": "I"}]},
    {"q": "바쁜 해외 출장 중 자유시간이 주어졌을 때?", "options": [{"text": "현지 거래처나 동료들과 함께 식사하며 친밀한 유대를 쌓는다.", "type": "E"}, {"text": "호텔이나 조용한 곳에서 혼자 휴식을 취하며 에너지를 재충전한다.", "type": "I"}]},
    {"q": "선적 서류(B/L, C/I, P/L)를 검토할 때 당신의 스타일은?", "options": [{"text": "오탈자, 규격 코드, 단가 수치 하나하나를 정밀하게 대조한다.", "type": "S"}, {"text": "인코텀즈 조건과 납기 일정 등 전체적인 흐름과 맥락을 먼저 본다.", "type": "N"}]},
    {"q": "새로운 수출입 품목을 발굴할 때 끌리는 것은?", "options": [{"text": "이미 시장 수요가 검증되었고 마진 구조가 안정적인 실물 제품", "type": "S"}, {"text": "현재 수요는 작지만 향후 트렌드를 선도할 혁신적인 아이템", "type": "N"}]},
    {"q": "수출입 프로세스 매뉴얼을 접했을 때 당신의 태도는?", "options": [{"text": "정해진 절차와 규정을 엄격하게 지키며 안전하게 업무를 수행한다.", "type": "S"}, {"text": "기존 절차의 비효율을 찾고 더 개선된 방식을 주도적으로 고안한다.", "type": "N"}]},
    {"q": "경쟁사 동향을 파악할 때 더 눈여겨보는 지표는?", "options": [{"text": "경쟁사의 현재 수출 물동량, 실거래 단가, 주요 거래처 명단", "type": "S"}, {"text": "경쟁사가 지향하는 중장기 비전과 글로벌 무역 환경의 구조적 변화", "type": "N"}]},
    {"q": "복잡한 관세법령이나 무역 규정을 해석해야 할 때?", "options": [{"text": "법령 조항의 명시된 문구와 기존의 유권해석 판례를 중심으로 본다.", "type": "S"}, {"text": "규정이 제정된 정책적 배경과 향후 개정 방향성을 종합해 유추한다.", "type": "N"}]},
    {"q": "거래처로부터 제품 하자로 인한 클레임이 접수되었습니다. 첫 조치는?", "options": [{"text": "계약서상 품질 보증 조항과 귀책사유를 객관적으로 규명한다.", "type": "T"}, {"text": "바이어가 겪었을 곤란함에 진심 어린 유감을 표하며 관계를 보호한다.", "type": "F"}]},
    {"q": "바이어와의 단가 협상 테이블에서 가장 중요한 원칙은?", "options": [{"text": "철저한 손익 계산을 바탕으로 회사의 마진을 철통 방어하는 것", "type": "T"}, {"text": "상대방의 입장을 배려하며 상호 신뢰 기반의 윈-윈 관계를 구축하는 것", "type": "F"}]},
    {"q": "포워더(물류사)의 실수로 선적이 지연되었을 때 대처법은?", "options": [{"text": "지연 원인을 논리적으로 따지고 계약에 따른 지체보상금을 청구한다.", "type": "T"}, {"text": "물류사 담당자의 고충을 헤아리며 함께 긴급 대체선을 신속히 찾는다.", "type": "F"}]},
    {"q": "해외 파트너사에게 개선 요구사항을 전달해야 할 때?", "options": [{"text": "문제점과 요구 조건을 명확하고 직설적으로 짚어 전달한다.", "type": "T"}, {"text": "상대방의 기여도를 먼저 칭찬한 뒤 완곡하게 개선을 당부한다.", "type": "F"}]},
    {"q": "당신이 생각하는 가장 이상적인 무역 부서의 모습은?", "options": [{"text": "역할 분담이 칼같이 명확하고 정량적 성과로 보상받는 팀", "type": "T"}, {"text": "서로 힘든 점을 챙겨주고 가족처럼 끈끈하게 화합하는 팀", "type": "F"}]},
    {"q": "수출 화물의 출항 일정을 조율할 때 당신의 방식은?", "options": [{"text": "통관부터 선적까지 단계별 마감 시한을 빈틈없이 계획해 둔다.", "type": "J"}, {"text": "대략적인 일정만 잡고, 현장 부두 상황에 맞춰 유연하게 조율한다.", "type": "P"}]},
    {"q": "세관 검사로 인해 예상치 못한 통관 지연이 발생했습니다.", "options": [{"text": "계획이 틀어진 것에 스트레스를 받으며 사전에 짠 비상 계획을 실행한다.", "type": "J"}, {"text": "무역 실무에서 흔히 있는 변수라 여기며 현장 상황에 유연하게 맞춘다.", "type": "P"}]},
    {"q": "업무용 컴퓨터 바탕화면이나 서류함 정리 상태는?", "options": [{"text": "프로젝트별, 날짜별 폴더 트리가 규칙적으로 완벽히 정돈되어 있다.", "type": "J"}, {"text": "조금 흩어져 있어 보여도 나만의 감각으로 필요한 파일을 즉각 찾는다.", "type": "P"}]},
    {"q": "바이어와의 중요한 미팅을 주재할 때 당신은?", "options": [{"text": "사전에 배포한 회의 안건(Agenda) 순서대로 타이트하게 진행한다.", "type": "J"}, {"text": "대화 흐름에 따라 자연스럽게 새로운 화제를 넘나들며 미팅한다.", "type": "P"}]},
    {"q": "분기별 무역 실적 보고서 제출 마감이 다가올 때?", "options": [{"text": "며칠 전부터 일찌감치 데이터를 취합해 여유 있게 마감한다.", "type": "J"}, {"text": "마감 직전의 긴장감 속에서 최고의 집중력을 발휘해 한 번에 끝낸다.", "type": "P"}]},

    # --- 산업 매칭 10문항 (FAS:패션/소비재, TEC:IT/테크, HEV:중공업/제조, BIO:바이오/제약) ---
    {"q": "제품을 소싱하거나 판매할 때 더 끌리는 매력 포인트는?", "options": [{"text": "트렌디한 디자인과 브랜드 스토리", "type": "FAS"}, {"text": "압도적인 기술력과 정밀한 하드웨어 스펙", "type": "TEC"}]},
    {"q": "당신이 담당하고 싶은 바이어와 프로젝트의 성격은?", "options": [{"text": "수천 건의 오더가 빠르게 순환하는 다이내믹한 소비재 B2B/B2C", "type": "FAS"}, {"text": "수년에 걸쳐 진행되는 수백억 단위의 대형 B2B 장기 프로젝트", "type": "HEV"}]},
    {"q": "당신이 더 관심을 가지는 글로벌 무역 규제/인증은?", "options": [{"text": "국가별 식약처 위생허가 및 인체 무해성 성분 규제", "type": "BIO"}, {"text": "글로벌 환경 규제 및 대형 기계/설비 안전 표준 인증", "type": "HEV"}]},
    {"q": "당신이 더 선호하는 박람회(전시회)의 모습은?", "options": [{"text": "화려한 조명과 인플루언서들이 모인 트렌디한 팝업 부스", "type": "FAS"}, {"text": "거대한 설비와 기계가 웅장하게 시연되는 B2B 산업 전시장", "type": "HEV"}]},
    {"q": "수출 제품에 문제가 생겼을 때 그나마 다루기 편한 것은?", "options": [{"text": "제품 변질, 유통기한 경과 등 화학적/생물학적 이슈", "type": "BIO"}, {"text": "부품 결함, 소프트웨어 버그 등 기계/전자적 이슈", "type": "TEC"}]},
    {"q": "무역 전문지에서 당신이 더 즐겨 읽는 뉴스 주제는?", "options": [{"text": "글로벌 패션위크 동향 및 K-뷰티 수출 폭발 리포트", "type": "FAS"}, {"text": "글로벌 반도체 공급망 변화 및 신형 스마트폰 출시 소식", "type": "TEC"}]},
    {"q": "당신이 생각하는 이상적인 거래처 현장의 분위기는?", "options": [{"text": "하얀 가운을 입고 연구와 실험이 진행되는 깔끔하고 고요한 랩실", "type": "BIO"}, {"text": "안전모를 쓰고 거대한 설비가 힘차게 돌아가는 역동적인 제조 공장", "type": "HEV"}]},
    {"q": "영업 실적을 달성했을 때 당신의 가장 큰 쾌감 포인트는?", "options": [{"text": "내가 수출한 화장품이나 옷을 입은 사람들을 길에서 마주칠 때", "type": "FAS"}, {"text": "내가 수출한 핵심 부품이 글로벌 대기업의 신제품에 탑재되었을 때", "type": "TEC"}]},
    {"q": "수출용 제품 카탈로그를 볼 때 당신이 꼼꼼히 확인하는 것은?", "options": [{"text": "제품의 성분 배합표와 부작용 여부, 임상 시험 데이터", "type": "BIO"}, {"text": "도면, 규격 수치, 내구성을 증명하는 강도 실험 데이터", "type": "HEV"}]},
    {"q": "10년 뒤 당신은 무역 업계에서 어떤 전문가로 불리고 싶나요?", "options": [{"text": "인류의 생명과 건강 연장에 기여하는 바이오/의약품 무역 스페셜리스트", "type": "BIO"}, {"text": "국가 핵심 산업을 이끄는 첨단 테크/전자 장비 수출 엑스퍼트", "type": "TEC"}]}
]

# --- 세션 상태 초기화 ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'answers' not in st.session_state:
    st.session_state.answers = [None] * 30

# --- 6가지 직무 MBTI 결과 ---
def get_job_result(mbti):
    if mbti in ["ENTJ", "ENTP", "ENFJ", "ESTJ"]:
        return {
            "job": "불도저형 글로벌 해외영업",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 자신감 넘치는 짱구
            "desc": "뛰어난 협상력과 거침없는 돌파력으로 전 세계 바이어를 사로잡는 무역업계의 프론트맨! 회사의 실적을 직접 견인하는 해외영업 직무가 천직입니다.",
            "features": "- 신규 벤더(Vendor) 및 바이어 발굴을 통한 시장 개척\n- 마진 방어를 위한 치열한 단가 및 계약 협상 주도\n- 수주부터 선적, 대금 회수까지 무역 프로젝트 총괄",
            "strategy": "- 전략 제2외국어(스페인어, 독일어 등) 회화력 어필\n- 낯선 환경에서의 문제 해결 및 글로벌 네트워킹 경험 강조\n- 면접 시 주도적인 목표 의식과 당당한 태도 어필"
        }
    elif mbti in ["ISFJ", "ISFP", "ESFJ"]:
        return {
            "job": "꼼꼼함의 끝판왕 무역사무/오퍼레이션",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 돋보기/안경 쓰고 열공하는 짱구
            "desc": "선적 서류의 철자 하나도 놓치지 않는 무결점 완벽주의자! 복잡한 수출입 통관과 결제가 한 치의 오차 없이 흘러가도록 지탱하는 핵심 엔진입니다.",
            "features": "- B/L, C/I 등 선적 서류 신속 정확한 발행 및 교차 검증\n- 신용장(L/C) 심사 및 Nego를 통한 대금 결제 리스크 관리\n- 수출입 실적 및 관세 환급 정산, 타 부서와의 유기적 협업",
            "strategy": "- 국제무역사, 무역영어 자격증을 통한 실무 이론 입증\n- 엑셀, ERP(SAP) 등 소프트웨어 활용 및 멀티태스킹 능력 강조\n- 과거 사소한 오류를 잡아내어 팀의 손실을 막은 꼼꼼함 어필"
        }
    elif mbti in ["ESTP", "ESFP", "ISTP"]:
        return {
            "job": "위기 대처의 달인 물류/SCM 담당자",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 다급하게 달려가는 짱구
            "desc": "어떤 악조건에서도 동물적인 감각으로 플랜 B를 찾아내는 당신! 전 세계 물류 공급망을 지휘하고 창고의 효율을 극대화하는 물류의 마에스트로입니다.",
            "features": "- 포워더, 선사, 항공사 조율을 통한 최적 운송 루트 설계\n- 선적 지연, 파손 등 돌발 상황 시 긴급 대체편 수배 및 수습\n- 운송비 절감 및 창고 재고 회전율 최적화 관리",
            "strategy": "- 물류관리사, 보세사 등 물류 특화 자격증 선점\n- 압박 상황에서 감정보다 이성으로 트러블슈팅(Troubleshooting)한 경험\n- 물류비용이나 소요 시간을 단축한 정량적 성과 중심의 자소서"
        }
    elif mbti in ["INTJ", "INTP"]:
        return {
            "job": "전략적 분석가 구매/글로벌 소싱",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 노트북 타자 치는 지적인 짱구
            "desc": "원자재 시세부터 환율 그래프까지 꿰뚫어 보는 두뇌! 전 세계 제조사를 샅샅이 뒤져 최상의 가성비 파트너를 발굴하는 전략가입니다.",
            "features": "- 글로벌 시장 조사를 통한 경쟁력 있는 신규 공급선 발굴\n- 원자재 지수, 환율 데이터 기반의 논리적인 구매 단가 협상\n- 공급사의 재무 건전성 및 생산 리스크 사전 진단/평가",
            "strategy": "- SQL, 파이썬 등 데이터 분석 및 재무제표 해독 능력 기르기\n- 특정 산업군(제조, 반도체 등) 원가 동향 분석 포트폴리오 준비\n- 감정적 호소보다 논리적 수치 기반의 냉철한 설득력 강조"
        }
    elif mbti in ["ENFP", "INFP", "INFJ"]:
        return {
            "job": "아이디어 뱅크 무역 마케터",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 끼부리며 춤추는 짱구
            "desc": "국경을 뛰어넘어 현지 소비자의 감성을 울리는 스토리텔러! 문화적 차이를 절묘하게 파고들어 우리 제품을 세계적인 브랜드로 만듭니다.",
            "features": "- 타겟 국가 문화와 트렌드를 반영한 제품 로컬라이징 마케팅\n- 글로벌 전시회 부스 총괄 기획 및 영문 홍보 콘텐츠 제작\n- 아마존/알리바바 등 글로벌 B2B/B2C 플랫폼 및 SNS 운영",
            "strategy": "- 카드뉴스, 홍보 영상 기획 등 시각적 디자인 툴 포트폴리오 필수\n- K-컬처 해외 반응 등 글로벌 소비 트렌드를 비즈니스로 연결한 경험\n- 글로벌 마케팅 공모전 수상 및 인플루언서 협업 마케팅 경험 어필"
        }
    else: # ISTJ 및 기타
        return {
            "job": "철두철미한 관세/컴플라이언스 전문가",
            "shinchan_gif": "https://mblogthumb-phinf.pstatic.net/20120102_138/too2500_1325495967275hnAd9_GIF/begdf.gif?type=w420", # 각 잡고 거수경례하는 단호한 짱구
            "desc": "복잡한 관세법과 규정을 완벽하게 사수하는 수호자! 기업이 막대한 과태료나 리스크 없이 순항하도록 이끄는 법률 전문가입니다.",
            "features": "- 국가별 수입 인증 및 비관세 장벽 요건 사전 검토\n- FTA 원산지 판정 및 증명서 발급, 관세 환급 업무\n- 세관 기업 심사(사후 검증) 대비 무역 서류 무결성 관리",
            "strategy": "- 원산지관리사, 관세사 1차 등 고난도 무역 법률 자격증 취득\n- 융통성보다는 원칙을 지켜 조직의 리스크를 방어했던 정직한 경험\n- 오탈자 하나 없는 완벽한 자소서로 빈틈없는 꼼꼼함 증명"
        }

# --- 4가지 산업(도메인) 결과 ---
def get_industry_result(scores):
    best_ind = max(scores, key=scores.get)
    if best_ind == "FAS":
        return {"name": "트렌드세터! 패션/뷰티/소비재", "desc": "트렌드 변화가 빠르고 감각적인 B2C 중심의 라이프스타일 산업이 잘 맞습니다. (예: 화장품, 의류 벤더, 생활용품 수출)"}
    elif best_ind == "TEC":
        return {"name": "혁신의 아이콘! IT/반도체/전자", "desc": "기술의 진보와 스펙의 우위를 다투는 첨단 테크 산업이 가슴을 뛰게 합니다. (예: 반도체 부품, 스마트 기기, 소프트웨어)"}
    elif best_ind == "HEV":
        return {"name": "스케일의 제왕! 자동차/기계/중공업", "desc": "수백억 단위의 장기 프로젝트와 거대한 설비가 오가는 묵직한 B2B 제조 산업군이 천직입니다. (예: 완성차, 철강, 플랜트 장비)"}
    else: # BIO
        return {"name": "인류의 수호자! 바이오/제약/의료기기", "desc": "인류의 생명과 직결되어 고도의 정밀함과 엄격한 규제가 동반되는 하이엔드 산업이 어울립니다. (예: 제약, 메디컬 기기, 화장품 원료)"}

# --- 상단 헤더 섹션 ---
def render_header():
    st.markdown("""
    <div style='text-align: center; margin-top: 5px; margin-bottom: 20px;'>
        <h1 style='font-size: 2.1rem; color: #0F172A; margin-bottom: 8px; font-weight: 800;'>무역 직무 MBTI 테스트 ✈️</h1>
        <p style='font-size: 1.15rem; color: #0284C7; font-weight: 600; margin: 0;'>글로벌 인재인 당신! 과연 어떤 직무가 맞을지 궁금하지 않나요?</p>
    </div>
    """, unsafe_allow_html=True)

render_header()

# ================================================
# 화면 1: 시작 화면
# ================================================
if st.session_state.step == 0:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center; color: #1E293B;'>나만의 무역 커리어 나침반 찾기 🧭</h3>", unsafe_allow_html=True)
        st.write("---")
        st.markdown("""
        해외영업, 무역사무, 물류, 마케팅... 광활한 무역의 세계에서  
        **나의 기질에 맞는 포지션**과 **가장 잘 어울리는 산업군(아이템)**은 무엇일까요?
        
        단 **30개의 실전 질문**을 통해 내 안의 무역 DNA를 분석하고,  
        합격을 부르는 **실전 취업 전략**까지 한 번에 확인해 보세요!
        """)
        st.write("")
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("테스트 시작하기 🚀", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

# ================================================
# 화면 2: 질문 화면 (1 ~ 30)
# ================================================
elif 1 <= st.session_state.step <= 30:
    q_idx = st.session_state.step - 1
    q_data = questions[q_idx]
    
    with st.container(border=True):
        progress = st.session_state.step / 30
        st.progress(progress)
        
        # 질문 파트 구분 표시
        if st.session_state.step <= 20:
            part_title = f"직무 적성 파악 중... ({st.session_state.step}/20)"
        else:
            part_title = f"맞춤 산업(도메인) 탐색 중... ({st.session_state.step - 20}/10)"
            
        st.markdown(f"<span style='color: #0284C7; font-weight: bold;'>{part_title}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-title'>Q{st.session_state.step}. {q_data['q']}</div>", unsafe_allow_html=True)
        
        options_text = [opt['text'] for opt in q_data['options']]
        default_idx = st.session_state.answers[q_idx] if st.session_state.answers[q_idx] is not None else 0
        
        choice = st.radio("보기", options_text, index=default_idx, label_visibility="collapsed")
        choice_idx = options_text.index(choice)
        
        st.write("---")
        
        # 네비게이션 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.step > 1:
                if st.button("⬅️ 이전 질문", use_container_width=True):
                    st.session_state.answers[q_idx] = choice_idx
                    st.session_state.step -= 1
                    st.rerun()
        with col2:
            button_label = "결과 보기 🎉" if st.session_state.step == 30 else "다음 질문 ➡️"
            if st.button(button_label, use_container_width=True):
                st.session_state.answers[q_idx] = choice_idx
                st.session_state.step += 1
                st.rerun()

# ================================================
# 화면 3: 결과 화면
# ================================================
elif st.session_state.step == 31:
    # 점수 집계 로직
    job_scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    ind_scores = {'FAS': 0, 'TEC': 0, 'HEV': 0, 'BIO': 0}
    
    for i, ans_idx in enumerate(st.session_state.answers):
        if ans_idx is not None:
            q_type = questions[i]['options'][ans_idx]['type']
            if i < 20:
                job_scores[q_type] += 1
            else:
                ind_scores[q_type] += 1

    mbti = ""
    mbti += "E" if job_scores['E'] >= job_scores['I'] else "I"
    mbti += "S" if job_scores['S'] >= job_scores['N'] else "N"
    mbti += "T" if job_scores['T'] >= job_scores['F'] else "F"
    mbti += "J" if job_scores['J'] >= job_scores['P'] else "P"
    
    job_res = get_job_result(mbti)
    ind_res = get_industry_result(ind_scores)
    
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; color: #0F172A;'>🎉 당신의 무역 커리어 분석 결과 🎉</h2>", unsafe_allow_html=True)
        st.write("---")
        
        # 짱구 GIF 삽입 (CSS로 박스 안에 예쁘게 배치)
        st.markdown(f"""
        <div style='display: flex; justify-content: center; margin-bottom: 20px;'>
            <img src="{job_res['shinchan_gif']}" width="180" style='border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);' alt="Result GIF">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='text-align: center;'>나의 무역 기질은 <span style='color: #0284C7;'>{mbti}</span>!</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #FF9B8A; margin-bottom: 30px;'>{job_res['job']}</h2>", unsafe_allow_html=True)
        
        # 1. 산업 매칭 결과
        st.write("#### 🏭 당신에게 딱 맞는 취업 산업(아이템)")
        st.info(f"**{ind_res['name']}**\n\n{ind_res['desc']}")
        st.write("---")
        
        # 2. 직무 요약
        st.write("#### 👤 직무 요약")
        st.write(job_res['desc'])
        st.write("---")
        
        # 3. 주요 업무 특징
        st.write("#### 📝 실전 주요 업무 특징")
        st.info(job_res['features'])
        st.write("---")
        
        # 4. 취업 전략
        st.write("#### 🎯 합격을 부르는 취업 준비 전략")
        st.success(job_res['strategy'])
        
        st.write("")
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("테스트 다시하기 🔄", use_container_width=True):
                st.session_state.step = 0
                st.session_state.answers = [None] * 30
                st.rerun()