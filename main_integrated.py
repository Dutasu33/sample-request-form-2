
from email.mime.text import MIMEText
import base64

def send_email_via_gmail(recipient_email, subject, body_text, client_secrets_path='client_secrets.json'):
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body_text)
    message['to'] = recipient_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
    return send_message



import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_pdf_to_drive(file_path, client_secrets_path='client_secrets.json'):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    uploaded = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = uploaded.get('id')

    permission = {'type': 'anyone', 'role': 'reader'}
    service.permissions().create(fileId=file_id, body=permission).execute()

    share_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return share_link



import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from fpdf import FPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

st.title("화장품 개발 의뢰서 + 유사 처방 추천 + PDF 보고서 + 이메일 자동화 시스템")

# Step 1: Input form
with st.form("prescription_form"):
    st.subheader("제품 기본 정보")
    prescription_id = st.text_input("처방 ID")
    name = st.text_input("제품명")
    product_type = st.selectbox("제품유형", ["바디스크럽", "바디워시", "크림", "토너"])
    texture = st.selectbox("제형", ["오일", "젤", "클레이", "로션"])
    functions = st.multiselect("기능성", ["각질제거", "진정", "피지관리", "보습", "미백"])
    ingredients = st.text_input("주요성분 (쉼표로 구분)")
    fragrance = st.selectbox("향", ["시트러스", "머스크", "플로럴", "무향"])
    vegan = st.radio("비건 여부", ["Y", "N"])
    skin_type = st.selectbox("피부타입 추천", ["민감성", "지성", "건성", "복합성"])
    positioning = st.text_input("제품 포지셔닝")
    feel = st.text_area("사용감 설명")
    email = st.text_input("보고서를 받을 이메일 주소 입력")
    submitted = st.form_submit_button("제출")

if submitted:
    record = {
        "처방ID": prescription_id,
        "제품명": name,
        "제품유형": product_type,
        "제형": texture,
        "기능성": ", ".join(functions),
        "주요성분": ingredients,
        "향": fragrance,
        "비건": vegan,
        "피부타입추천": skin_type,
        "포지셔닝": positioning,
        "사용감설명": feel,
        "입력일": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        sheet_url = st.secrets["sheet_url"]
        requests.post(sheet_url, json=record)
        st.success("✅ Google Sheets 저장 완료!")
    except Exception as e:
        st.error(f"Google Sheets 저장 실패: {e}")

    # Step 2: Load dummy prescription data
    df = pd.read_excel("더미처방100개.xlsx")
    df["text"] = df["사용감설명"].fillna('') + " " + df["특징요약"].fillna('') + " " + df["주요성분"].fillna('')
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df["text"])
    input_vec = tfidf.transform([feel])
    sim_scores = cosine_similarity(input_vec, tfidf_matrix).flatten()
    df["유사도"] = sim_scores
    top5 = df.sort_values("유사도", ascending=False).head(5)

    st.subheader("📋 유사 처방 추천 결과 (Top 5)")
    st.dataframe(top5[["처방ID", "처방명", "제형", "기능성", "비건여부", "유사도", "사용감설명"]])

    # Step 3: PDF Report Generator
    def create_pdf(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("Nanum", "", "NanumGothic.ttf", uni=True)
        pdf.set_font("Nanum", "", 12)
        pdf.cell(200, 10, txt="유사 처방 추천 보고서", ln=1, align='C')
        pdf.ln(10)
        for index, row in data.iterrows():
            txt = f"{row['처방ID']} - {row['처방명']} / 유사도: {row['유사도']:.2f}"
            pdf.cell(200, 10, txt=txt, ln=1)
        pdf_path = "/mnt/data/recommendation_report.pdf"
        pdf.output(pdf_path)
        return pdf_path

    # Step 4: Email Sender
    def send_email(receiver_email, pdf_path):
        sender_email = st.secrets["email"]
        sender_pass = st.secrets["email_pass"]

        msg = EmailMessage()
        msg["Subject"] = "유사 처방 추천 보고서"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content("첨부된 PDF 보고서를 확인해주세요.")

        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="report.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_pass)
            smtp.send_message(msg)

    pdf_file = create_pdf(top5)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 추천 보고서 다운로드", data=f, file_name="recommendation_report.pdf")

    if email:
        try:
            send_email(email, pdf_file)
            st.success("📧 이메일이 성공적으로 발송되었습니다.")
        except Exception as e:
            st.error(f"이메일 발송 실패: {e}")
