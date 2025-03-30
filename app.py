
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# 간단한 텍스트 기반 PDF 생성 함수 (실제는 .txt 형태)
def generate_simple_pdf(data):
    buffer = BytesIO()
    content = ""
    for key, value in data.items():
        content += f"{key}: {value}\n"
    content += f"작성일: {datetime.today().strftime('%Y-%m-%d')}\n"
    buffer.write(content.encode())
    buffer.seek(0)
    return buffer

st.title("제품 개발 상담 입력폼 (간단 PDF 버전)")

with st.form("sample_form"):
    고객사명 = st.text_input("고객사명")
    담당자 = st.text_input("담당자 성함 및 연락처")
    상담유형 = st.selectbox("상담 유형", ["ODM 개발", "신제품 개발", "기존 제품 리뉴얼", "OEM 생산"])
    제품명 = st.text_input("제품명 (가칭)")
    제품유형 = st.text_input("제품 유형")
    기능 = st.text_area("주요 기능 및 컨셉")
    수량일정 = st.text_input("요청 수량 및 납기 일정")
    단가 = st.text_input("희망 단가 또는 조건")
    기타 = st.text_area("기타 요청 사항")
    제출 = st.form_submit_button("제출")

if 제출:
    data = {
        "고객사명": 고객사명,
        "담당자": 담당자,
        "상담유형": 상담유형,
        "제품명": 제품명,
        "제품유형": 제품유형,
        "기능": 기능,
        "수량/일정": 수량일정,
        "단가": 단가,
        "기타": 기타,
    }
    st.success("의뢰서가 접수되었습니다!")

    st.subheader("입력 요약")
    st.table(pd.DataFrame([data]))

    pdf_buffer = generate_simple_pdf(data)
    st.download_button(
        label="의뢰서 PDF 다운로드",
        data=pdf_buffer,
        file_name=f"의뢰서_{고객사명}.txt",
        mime="text/plain"
    )
