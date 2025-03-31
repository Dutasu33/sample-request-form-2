
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))

# PDF 생성 함수
def create_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont('NanumGothic', 14)
    c.drawString(100, 800, "안녕하세요 😊")
    c.drawString(100, 780, "이 문서는 한글이 포함된 PDF입니다.")
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit 앱 화면
st.title("📄 한글 PDF 생성기 (Streamlit + Reportlab)")

if st.button("📥 PDF 다운로드"):
    pdf_file = create_pdf()
    st.download_button(
        label="📄 PDF 저장",
        data=pdf_file,
        file_name="한글_샘플.pdf",
        mime="application/pdf"
    )
