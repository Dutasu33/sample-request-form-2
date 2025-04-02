import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

st.set_page_config(page_title="화장품 개발 입력 시스템", layout="wide")
st.title("🧪 화장품 개발 입력 시스템 (자동입력 포함)")

# 세션 상태 초기화
if 'form_db' not in st.session_state:
    st.session_state.form_db = {}

if 'mode' not in st.session_state:
    st.session_state.mode = "등록"

# 작업 모드 선택
st.session_state.mode = st.sidebar.radio("작업 선택", ["등록", "조회", "수정"], index=["등록", "조회", "수정"].index(st.session_state.mode))

# 날짜 기반 의뢰번호 생성 함수
def generate_prescription_id():
    today = datetime.now().strftime("%Y-%m-%d")
    count = sum(1 for k in st.session_state.form_db if k.startswith(today))
    return f"{today}-{count+1:03d}"

# 자동입력 분석
parsed_data = {}
if st.session_state.mode == "등록":
    uploaded_file = st.file_uploader("📂 자동 입력용 파일 업로드 (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            for col in df.columns:
                for key in ["브랜드명", "제품명", "제품유형", "제형", "향", "컬러", "주요성분", "비건", "피부타입", "포지셔닝", "사용감",
                            "요청자명", "연락처", "기능성요청", "샘플 수량", "초도 수량", "예상 소비자가", "수출국가"]:
                    if key in col:
                        parsed_data[key] = str(df[col].iloc[0])
            st.success("✅ 파일 분석 완료: 자동 입력값이 반영됩니다.")
        except Exception as e:
            st.warning(f"파일 분석 실패: {e}")

# 공통 입력 필드 정의
def input_fields(existing_data=None, autofill_data=None):
    def get(key, default=""):
        if existing_data: return existing_data.get(key, default)
        if autofill_data: return autofill_data.get(key, default)
        return default

    brand = st.text_input("브랜드명", value=get("브랜드명"))
    name = st.text_input("제품명", value=get("제품명"))
    product_type = st.selectbox("제품유형", ["바디스크럽", "바디워시", "크림", "토너"],
                                index=["바디스크럽", "바디워시", "크림", "토너"].index(get("제품유형", "바디스크럽")))
    texture = st.selectbox("제형", ["오일", "젤", "클레이", "로션"],
                           index=["오일", "젤", "클레이", "로션"].index(get("제형", "오일")))
    functions = st.multiselect("기능성", ["각질제거", "진정", "피지관리", "보습", "미백"],
                               default=(get("기능성요청", "").split(",") if get("기능성요청") else []))
    ingredients = st.text_input("주요성분", value=get("주요성분"))
    fragrance = st.selectbox("향", ["시트러스", "머스크", "플로럴", "무향"],
                             index=["시트러스", "머스크", "플로럴", "무향"].index(get("향", "시트러스")))
    vegan = st.radio("비건 여부", ["Y", "N"], index=["Y", "N"].index(get("비건", "Y")))
    skin_type = st.selectbox("피부타입 추천", ["민감성", "지성", "건성", "복합성"],
                             index=["민감성", "지성", "건성", "복합성"].index(get("피부타입", "민감성")))
    positioning = st.text_input("제품 포지셔닝", value=get("포지셔닝"))
    feel = st.text_area("사용감 설명", value=get("사용감"))
    return {
        "브랜드명": brand,
        "제품명": name,
        "제품유형": product_type,
        "제형": texture,
        "기능성": functions,
        "주요성분": ingredients,
        "향": fragrance,
        "비건": vegan,
        "피부타입": skin_type,
        "포지셔닝": positioning,
        "사용감": feel,
        "입력일": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# 등록 모드
if st.session_state.mode == "등록":
    st.subheader("📝 신규 등록")
    new_data = input_fields(autofill_data=parsed_data)
    if st.button("✅ 등록하기"):
        new_id = generate_prescription_id()
        st.session_state.form_db[new_id] = new_data
        st.success(f"등록 완료! 의뢰번호: {new_id}")

# 조회 및 수정 공통
elif st.session_state.mode in ["조회", "수정"]:
    st.subheader("📋 의뢰서 선택")
    options = {f"{k} - {v['제품명']}": k for k, v in st.session_state.form_db.items()}
    selected_display = st.selectbox("조회할 의뢰서 선택", list(options.keys()))

    if selected_display:
        selected_id = options[selected_display]
        record = st.session_state.form_db[selected_id]

        st.markdown(f"### 📄 의뢰서 정보: {selected_id}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**브랜드명:** {record['브랜드명']}")
            st.markdown(f"**제품명:** {record['제품명']}")
            st.markdown(f"**제품유형:** {record['제품유형']}")
            st.markdown(f"**제형:** {record['제형']}")
            st.markdown(f"**향:** {record['향']}")
            st.markdown(f"**비건:** {record['비건']}")
        with col2:
            st.markdown(f"**피부타입 추천:** {record['피부타입']}")
            st.markdown(f"**포지셔닝:** {record['포지셔닝']}")
            st.markdown(f"**주요성분:** {record['주요성분']}")
            st.markdown(f"**기능성:** {', '.join(record['기능성'])}")
            st.markdown(f"**입력일:** {record['입력일']}")

        st.markdown("**🧴 사용감 설명:**")
        st.info(record['사용감'])

        if st.session_state.mode == "수정":
            updated_data = input_fields(existing_data=record)
            if st.button("💾 수정 저장"):
                st.session_state.form_db[selected_id] = updated_data
                st.success("수정이 완료되었습니다.")
