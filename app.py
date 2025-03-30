
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

def generate_dummy_pdf(data):
    buffer = BytesIO()
    buffer.write(f"고객사명: {data['고객사명']}\n".encode())
    buffer.write(f"담당자: {data['담당자']}\n".encode())
    buffer.write(f"상담 유형: {data['상담유형']}\n".encode())
    buffer.write(f"제품명: {data['제품명']}\n".encode())
    buffer.write(f"제품유형: {data['제품유형']}\n".encode())
    buffer.write(f"기능/컨셉: {data['기능']}\n".encode())
    buffer.write(f"요청 수량/일정: {data['수량/일정']}\n".encode())
    buffer.write(f"희망 단가/조건: {data['단가']}\n".encode())
    buffer.write(f"기타 요청 사항: {data['기타']}\n".encode())
    buffer.write(f"작성일: {datetime.today().strftime('%Y-%m-%d')}\n".encode())
    buffer.seek(0)
    return buffer

st.title("제품 개발 상담 입력폼 (Streamlit Demo)")

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

    pdf_buffer = generate_dummy_pdf(data)
    st.download_button(
        label="의뢰서 PDF 다운로드",
        data=pdf_buffer,
        file_name=f"의뢰서_{고객사명}.pdf",
        mime="application/pdf"
    )
