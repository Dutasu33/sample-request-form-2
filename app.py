
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# CSV 저장 함수
def save_to_csv(data_dict, filename="상담의뢰_목록.csv"):
    df = pd.DataFrame([data_dict])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

# TXT 파일 생성
def generate_txt(data_dict):
    buffer = BytesIO()
    content = ""
    for key, value in data_dict.items():
        content += f"{key}: {value}\n"
    content += f"작성일: {datetime.today().strftime('%Y-%m-%d')}\n"
    buffer.write(content.encode())
    buffer.seek(0)
    return buffer

# 입력폼
st.title("제품 개발 상담 입력폼 (CSV 저장 + TXT 다운로드)")

with st.form("form"):
    회사명 = st.text_input("회사명")
    담당자 = st.text_input("담당자")
    이메일 = st.text_input("이메일 / 휴대폰")
    제품명 = st.text_input("제품명 (가칭)")
    제품유형 = st.text_input("제품유형 / 용량")
    용기사양 = st.text_input("용기사양")
    출시일 = st.text_input("희망 출시일")
    초도수량 = st.text_input("초도수량(MOQ)")
    판매국가 = st.text_input("판매국가")
    기능성 = st.text_input("기능성")
    작성일 = datetime.today().strftime("%Y-%m-%d")
    제출 = st.form_submit_button("제출")

if 제출:
    data = {
        "회사명": 회사명,
        "담당자": 담당자,
        "이메일": 이메일,
        "제품명": 제품명,
        "제품유형": 제품유형,
        "용기사양": 용기사양,
        "희망출시일": 출시일,
        "초도수량": 초도수량,
        "판매국가": 판매국가,
        "기능성": 기능성,
        "작성일": 작성일
    }

    st.success("📬 의뢰서가 접수되었습니다!")
    st.table(pd.DataFrame([data]))

    # CSV 저장
    save_to_csv(data)

    # TXT 다운로드
    txt_file = generate_txt(data)
    st.download_button(
        label="의뢰서 TXT 다운로드",
        data=txt_file,
        file_name=f"의뢰서_{회사명}.txt",
        mime="text/plain"
    )
