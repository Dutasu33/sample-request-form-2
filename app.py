
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

def save_to_csv(data, filename="상담_의뢰_리스트.csv"):
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

def generate_simple_txt(data):
    buffer = BytesIO()
    content = ""
    for key, value in data.items():
        content += f"{key}: {value}\n"
    content += f"작성일: {datetime.today().strftime('%Y-%m-%d')}\n"
    buffer.write(content.encode())
    buffer.seek(0)
    return buffer

st.title("제품 개발 상담 통합 입력폼")

with st.form("sample_form"):
    st.subheader("📌 [기본정보]")
    회사명 = st.text_input("회사명")
    담당자 = st.text_input("담당자")
    이메일_휴대폰 = st.text_input("이메일 / 휴대폰")

    st.subheader("🧴 [제품기본]")
    제품명 = st.text_input("제품명 (가칭)")
    제품유형_용량 = st.text_input("제품유형 / 용량")
    용기사양 = st.text_input("용기사양")

    st.subheader("🚀 [출시정보]")
    출시일 = st.text_input("희망 출시일")
    초도수량 = st.text_input("초도수량(MOQ)")
    판매국가 = st.text_input("판매국가")

    st.subheader("🧪 [개발요청]")
    제형감 = st.text_area("제형 및 사용감")
    색상향펄 = st.text_input("색상 / 향 / 펄 여부")
    핵심성분 = st.text_area("핵심 성분")

    st.subheader("💡 [기능 / 임상]")
    기능성 = st.text_input("기능성")
    임상항목 = st.text_area("임상 요청 항목")

    st.subheader("🎯 [마케팅 요소]")
    제품컨셉 = st.text_area("제품/브랜드 컨셉")
    감성포인트 = st.text_area("스토리 또는 감성 포인트")
    마케팅차별 = st.text_area("마케팅 차별 요소 (ex. 지역소구, 원료소구)")

    st.subheader("✅ [인증 / 규제]")
    비건 = st.text_input("비건 인증 여부")
    규제확인 = st.text_area("수출국 규제 확인 필요 항목")

    st.subheader("📦 [부자재]")
    사급여부 = st.text_input("사급 여부")
    포장구성 = st.text_input("포장 구성 (1차/2차)")
    용기상세 = st.text_area("용기/캡/인쇄 상세")

    st.subheader("📌 [기타 요청사항]")
    견적조건 = st.text_input("견적 조건")
    샘플요청 = st.text_input("샘플 요청일 / 수량")
    특이사항 = st.text_area("특이사항")

    제출 = st.form_submit_button("제출")

if 제출:
    data = {
        "회사명": 회사명,
        "담당자": 담당자,
        "이메일/휴대폰": 이메일_휴대폰,
        "제품명": 제품명,
        "제품유형/용량": 제품유형_용량,
        "용기사양": 용기사양,
        "희망출시일": 출시일,
        "초도수량": 초도수량,
        "판매국가": 판매국가,
        "제형 및 사용감": 제형감,
        "색상/향/펄": 색상향펄,
        "핵심성분": 핵심성분,
        "기능성": 기능성,
        "임상요청항목": 임상항목,
        "제품컨셉": 제품컨셉,
        "감성포인트": 감성포인트,
        "마케팅차별요소": 마케팅차별,
        "비건인증여부": 비건,
        "규제확인항목": 규제확인,
        "사급여부": 사급여부,
        "포장구성": 포장구성,
        "용기상세": 용기상세,
        "견적조건": 견적조건,
        "샘플요청일수량": 샘플요청,
        "특이사항": 특이사항,
        "작성일": datetime.today().strftime("%Y-%m-%d")
    }

    st.success("의뢰서가 접수되었습니다!")
    st.subheader("입력 요약")
    st.table(pd.DataFrame([data]))

    save_to_csv(data)

    txt_buffer = generate_simple_txt(data)
    st.download_button(
        label="의뢰서 TXT 다운로드",
        data=txt_buffer,
        file_name=f"의뢰서_{회사명}.txt",
        mime="text/plain"
    )
