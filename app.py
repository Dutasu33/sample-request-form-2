
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ▶ Load 처방DB
df = pd.read_excel("처방DB_샘플_Streamlit용.xlsx")

st.set_page_config(page_title="제품 개발 의뢰 자동화", layout="centered")
st.title("🧴 제품 개발 의뢰 자동화 시스템")

st.header("1. 최초 의뢰서 입력")
with st.form("inquiry_form"):
    company = st.text_input("회사명")
    manager = st.text_input("담당자명")
    product = st.text_input("제품명(가칭)")
    ptype = st.selectbox("제품유형", df["제품유형"].unique())
    form = st.selectbox("제형", df["제형"].unique())
    function = st.text_input("요청 기능성 (쉼표로 구분)")
    vegan = st.radio("비건 여부", ["Y", "N"])
    submitted = st.form_submit_button("제출")

if submitted:
    st.header("2. 유사 처방 추천 (AI 기반)")
    df["검색키"] = df["제형"] + " " + df["기능성"] + " " + df["비건여부"]
    user_query = f"{form} {function} {vegan}"

    vect = TfidfVectorizer()
    tfidf_matrix = vect.fit_transform(df["검색키"])
    query_vec = vect.transform([user_query])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()

    df["유사도"] = similarity
    top3 = df.sort_values(by="유사도", ascending=False).head(3)

    selected = st.radio("추천 처방 중 선택:", top3["처방명"].tolist())

    if selected:
        st.header("3. 최종 의뢰서 PDF 생성")
        info = top3[top3["처방명"] == selected].iloc[0]

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 800, f"제품 개발 의뢰서 - {product}")
        pdf.drawString(100, 780, f"회사명: {company}")
        pdf.drawString(100, 760, f"담당자명: {manager}")
        pdf.drawString(100, 740, f"제품유형: {ptype} / 제형: {form} / 기능성: {function}")
        pdf.drawString(100, 720, f"선택 처방: {selected}")
        pdf.drawString(100, 700, f"주요성분: {info['주요성분']}")
        pdf.drawString(100, 680, f"거품: {info['거품의크기']}, 탄력성: {info['거품의탄력성']}")
        pdf.drawString(100, 660, f"보습력: {info['보습력']}, 산뜻함: {info['산뜻함']}, 촉촉함: {info['촉촉함']}")
        pdf.drawString(100, 640, f"피부타입: {info['피부타입추천']}, 계절: {info['권장사용시기']}")
        pdf.drawString(100, 620, f"제품포지셔닝: {info['제품포지셔닝']}")
        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        st.download_button(
            label="📄 최종 의뢰서 PDF 다운로드",
            data=buffer,
            file_name=f"{product}_의뢰서.pdf",
            mime="application/pdf"
        )
