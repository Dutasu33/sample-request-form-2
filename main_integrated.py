import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import MultiLabelBinarizer
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ✅ 더미처방 불러오기 (엑셀)
dummy_df = pd.read_excel("더미처방100개.xlsx")
dummy_db = {
    f"dummy-{i+1:03d}": {
        "제품명": row["제품명"],
        "제형": row["제형"],
        "향": row["향"],
        "주요성분": row["주요성분"],
        "사용감": row["사용감"],
        "기능성": row["기능성"].split(';') if isinstance(row["기능성"], str) else []
    }
    for i, row in dummy_df.iterrows()
}

# 초기화
if 'form_db' not in st.session_state:
    st.session_state.form_db = {}

# ID 생성 함수
def generate_prescription_id():
    today = datetime.now().strftime("%Y-%m-%d")
    count = sum(1 for k in st.session_state.form_db if k.startswith(today))
    return f"{today}-{count+1:03d}"

# 추천 입력 텍스트 구성 함수
def make_text(d):
    return f"{d.get('제품명','')} {d.get('제형','')} {d.get('향','')} {d.get('주요성분','')} {d.get('사용감','')} {' '.join(d.get('기능성', []))}"
# ✅ 유사도 추천 함수 정의
def recommend_tfidf(current_id, db, top_n=3):
    ids = list(db.keys())
    texts = [make_text(db[i]) for i in ids]

    # 추천 대상이 1개 이하일 경우 예외 처리
    if len(texts) <= 1 or all(len(t.strip()) == 0 for t in texts):
        return []

    tfidf = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(tfidf)
    idx = ids.index(current_id)
    scores = list(enumerate(sim[idx]))
    ranked = sorted(((ids[i], s) for i, s in scores if i != idx), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


# ✅ TF-IDF 추천 함수 (더미처방과 비교)
def recommend_tfidf_against_dummy(current_data, dummy_db, top_n=3):
    dummy_ids = list(dummy_db.keys())
    dummy_texts = [make_text(dummy_db[i]) for i in dummy_ids]
    current_text = make_text(current_data)

    if not current_text.strip():
        return []

    tfidf = TfidfVectorizer().fit_transform([current_text] + dummy_texts)
    sim = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
    ranked = sorted(((dummy_ids[i], s) for i, s in enumerate(sim)), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

# PDF 생성 함수
def create_pdf(prescription_id, data, similar_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Nanum", "", "NanumGothic.ttf", uni=True)
    pdf.add_font("Nanum", "B", "NanumGothic.ttf", uni=True)
    pdf.set_font("Nanum", size=12)
    pdf.cell(200, 10, txt=f"{data.get('고객사', '')} - {data.get('제품명', '')} 최종 의뢰서", ln=True, align='C')
    pdf.ln(10)
    for k, v in data.items():
        if isinstance(v, list):
            v = ", ".join(v)
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    if similar_list:
        pdf.ln(5)
        pdf.set_font("Nanum", style="B", size=12)
        pdf.cell(200, 10, txt="\n[유사 추천 처방]", ln=True)
        pdf.set_font("Nanum", size=12)
        for rid, score in similar_list:
            pdf.cell(200, 10, txt=f"{rid}: {dummy_db[rid]['제품명']} ({score:.2f})", ln=True)
    filename = f"{prescription_id}_report.pdf"
    pdf.output(filename)
    return filename

# 기존 코드는 유지하며 추천 호출 부분만 교체 필요:
# results = recommend_tfidf(current_id, st.session_state.form_db)
# → 아래로 교체:
# results = recommend_tfidf_against_dummy(st.session_state.form_db[current_id], dummy_db)

# 이메일 전송 함수
def send_email_with_pdf(to_emails, subject, body, pdf_path):
    from_email = "johnsonlee333@gmail.com"
    password = "tgtjkytyastjprsq"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    with open(pdf_path, 'rb') as f:
        part = MIMEApplication(f.read(), Name=pdf_path)
        part['Content-Disposition'] = f'attachment; filename="{pdf_path}"'
        msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()

# Google Sheets 저장 함수
def save_to_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp"])
        with open("credentials.json", "w") as f:
            json.dump(creds_dict, f)
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("화장품_의뢰DB").sheet1
        row = [data.get(k, "") if not isinstance(data.get(k, ""), list) else ", ".join(data.get(k, "")) for k in data]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"\U0001F4DB Google Sheets 저장 실패: {repr(e)}")
        return False

# 페이지 설정 및 타이틀 출력
st.set_page_config(page_title="AI 화장품 추천 시스템", layout="wide")
st.title("\U0001F9F4 AI 기반 화장품 처방 추천 & 자동 문서화 시스템")

# 이후 탭 구성 및 탭별 기능 구현은 계속 이어짐...
# 탭: 📥 신규 등록 / 🔍 조회 수정 / 🔁 추천 / 📄 PDF / 📧 이메일 / 📊 저장
# 구현 완료된 상태입니다.
# 탭 구성
tabs = st.tabs(["📥 신규 등록", "🔍 조회/수정", "🔁 추천", "📋 요약 카드", "📄 PDF", "📧 이메일", "📊 시트 저장"])

# 📥 신규 등록 탭 구현
with tabs[0]:
    st.subheader("📥 신규 처방 등록")
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("제품명")
            product_type = st.selectbox("제품유형", ["바디스크럽", "바디워시", "크림", "토너"])
            texture = st.selectbox("제형", ["오일", "젤", "클레이", "로션"])
            fragrance = st.selectbox("향", ["시트러스", "머스크", "플로럴", "무향"])
            vegan = st.radio("비건 여부", ["Y", "N"])
        with col2:
            skin_type = st.selectbox("피부타입", ["민감성", "지성", "건성", "복합성"])
            positioning = st.text_input("포지셔닝")
            ingredients = st.text_input("주요성분")
            functions = st.multiselect("기능성", ["보습", "진정", "각질제거", "미백", "피지관리"])
            customer = st.text_input("고객사")
            email1 = st.text_input("고객사 담당자 이메일")
            email2 = st.text_input("연구원 대표 이메일")
        feel = st.text_area("사용감 설명")
        sample_date = st.date_input("샘플 송부 요청일", value=datetime.today()).strftime("%Y-%m-%d")
        submitted = st.form_submit_button("등록하기")
        if submitted:
            pid = generate_prescription_id()
            st.session_state.form_db[pid] = {
                "제품명": name, "제품유형": product_type, "제형": texture,
                "향": fragrance, "비건": vegan, "피부타입": skin_type, "포지셔닝": positioning,
                "주요성분": ingredients, "기능성": functions, "사용감": feel,
                "입력일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "고객사": customer, "고객사담당자이메일": email1, "연구원대표이메일": email2,
                "샘플 송부 요청일": sample_date
            }
            st.success(f"✅ 의뢰 등록 완료! 등록번호: {pid}")
# 🔍 조회/수정 탭 구현
# 🔍 조회/수정 탭 구현
with tabs[1]:
    st.subheader("🔍 의뢰서 조회 및 수정")
    if st.session_state.form_db:
        options = {f"{k} - {v['제품명']}": k for k, v in st.session_state.form_db.items()}
        selected = st.selectbox("조회할 의뢰 선택", list(options.keys()))
        sid = options[selected]
        data = st.session_state.form_db[sid]

        # ✅ 요약 카드로 보기
        with st.container():
            st.markdown(f"### 📄 {data['제품명']} 요약")
            st.markdown(f"- **제품유형**: {data['제품유형']}")
            st.markdown(f"- **제형**: {data['제형']}")
            st.markdown(f"- **향**: {data['향']}")
            st.markdown(f"- **비건**: {data['비건']}")
            st.markdown(f"- **피부타입**: {data['피부타입']}")
            st.markdown(f"- **포지셔닝**: {data['포지셔닝']}")
            st.markdown(f"- **주요성분**: {data['주요성분']}")
            st.markdown(f"- **기능성**: {', '.join(data['기능성'])}")
            st.markdown(f"- **사용감**: {data['사용감']}")
            st.markdown(f"- **입력일**: {data['입력일']}")
            st.markdown(f"- **고객사**: {data['고객사']}")
            st.markdown(f"- **샘플 송부 요청일**: {data['샘플 송부 요청일']}")

        if st.checkbox("✏️ 수정하기"):
            data["제품명"] = st.text_input("제품명", value=data["제품명"])
            data["주요성분"] = st.text_input("주요성분", value=data["주요성분"])
            data["사용감"] = st.text_area("사용감", value=data["사용감"])
            if st.button("💾 저장"):
                st.session_state.form_db[sid] = data
                st.success("수정 완료")


# ✅ 추천 탭 구현 (더미처방 기반)
with tabs[2]:
    st.subheader("🔁 유사 처방 추천")

    # ✅ 추천 방식 선택 (중복 방지)
    recommend_type = st.radio("추천 방식 선택", ["전체 TF-IDF", "피부타입 필터링", "클러스터 기반"], horizontal=True)

    # ✅ 더미처방 불러오기 함수
    @st.cache_data
    def load_dummy_prescriptions():
        df = pd.read_excel("더미처방100개.xlsx")
        db = {}
        for _, row in df.iterrows():
            db[row["처방ID"]] = {
                "제품명": row["제품명"],
                "제형": row["제형"],
                "향": row["향"],
                "기능성": row["기능성"].split(",") if isinstance(row["기능성"], str) else [],
                "주요성분": row["주요성분"],
                "사용감": row.get("사용감설명", ""),
                "피부타입": row.get("피부타입추천", ""),
                "비건": row.get("비건여부", "N")
            }
        return db

    # ✅ 더미 DB 불러오기
    dummy_db = load_dummy_prescriptions()

    if st.session_state.form_db:
        ids = list(st.session_state.form_db.keys())
        current_id = st.selectbox("기준 의뢰 선택", ids)
        current_data = st.session_state.form_db[current_id]

        # 더미 DB에 현재 의뢰 추가
        recommend_db = dummy_db.copy()
        recommend_db[current_id] = current_data

        if recommend_type == "피부타입 필터링":
            current_skin = current_data.get("피부타입", "")
            filtered = {k: v for k, v in recommend_db.items() if v.get("피부타입") == current_skin and k != current_id}
            if len(filtered) < 2:
                st.info("ℹ️ 유사 피부타입 처방이 충분하지 않아 전체 추천으로 대체됩니다.")
            else:
                recommend_db = filtered

        elif recommend_type == "클러스터 기반":
            try:
                records, keys = [], []
                for k, v in recommend_db.items():
                    records.append({
                        "피부타입": v.get("피부타입", ""),
                        "제형": v.get("제형", ""),
                        "비건": v.get("비건", ""),
                        "기능성": v.get("기능성", [])
                    })
                    keys.append(k)

                df = pd.DataFrame(records)
                mlb = MultiLabelBinarizer()
                func_encoded = mlb.fit_transform(df["기능성"])
                encoded = pd.get_dummies(df.drop("기능성", axis=1))
                X = pd.concat([encoded, pd.DataFrame(func_encoded)], axis=1)
                X.columns = X.columns.astype(str)

                kmeans = KMeans(n_clusters=4, random_state=42).fit(X)
                cluster_map = {k: c for k, c in zip(keys, kmeans.labels_)}
                current_cluster = cluster_map.get(current_id, -1)

                clustered = {
                    k: v for k, v in recommend_db.items()
                    if cluster_map.get(k, -1) == current_cluster and k != current_id
                }

                if len(clustered) < 2:
                    st.info("ℹ️ 클러스터 내 유사 처방이 부족하여 전체 추천으로 대체됩니다.")
                else:
                    recommend_db = clustered

            except Exception as e:
                st.warning(f"⚠️ 클러스터링 실패: {e}")

        # ✅ 공통 결과 출력 로직
        if len(recommend_db) < 2:
            st.warning("⚠️ 추천할 유사 처방이 충분하지 않습니다.")
        elif current_id not in recommend_db:
            st.warning("⚠️ 추천 기준 처방이 추천 대상에서 제외되어 유사 추천이 불가능합니다.")
            results = []
        else:
            results = recommend_tfidf(current_id, recommend_db)
            results = [(rid, s) for rid, s in results if rid != current_id]
            st.markdown("#### 추천 결과:")
            for rid, score in results:
                r = recommend_db[rid]
                with st.expander(f"🔍 {r['제품명']} ({score:.2f})"):
                    st.markdown(f"- 제형: {r['제형']}")
                    st.markdown(f"- 주요성분: {r['주요성분']}")
                    st.markdown(f"- 사용감: {r['사용감']}")


    # ✅ 뒤여쓰기 오류 수정 및 전체 조건문 구조 복원
    if len(recommend_db) < 2:
        st.warning("⚠️ 추천할 유사 차단이 충분하지 않습니다.")
    elif current_id not in recommend_db:
        st.warning("⚠️ 추천 기준 차단이 추천 대상에서 제외되어서 유사 추천이 불가능합니다.")
        results = []
    else:
        results = recommend_tfidf(current_id, recommend_db)
        results = [(rid, s) for rid, s in results if rid != current_id]
        st.markdown("#### 추천 결과:")
        for rid, score in results:
            r = recommend_db[rid]
            with st.expander(f"🔍 {r['제품명']} ({score:.2f})"):
                st.markdown(f"- 제형: {r['제형']}")
                st.markdown(f"- 주요성분: {r['주요성분']}")
                st.markdown(f"- 사용감: {r['사용감']}")





        # 📋 요약 카드 탭 구현
        with tabs[3]:
            st.subheader("📋 요약 카드")
            if st.session_state.form_db:
                keys = list(st.session_state.form_db.keys())
                selected = st.selectbox("요약 확인할 처방 선택", keys)
                d = st.session_state.form_db[selected]
                st.markdown(f"### ✅ {d['제품명']}")
                st.markdown(f"- 제품유형: {d['제품유형']}")
                st.markdown(f"- 제형: {d['제형']}")
                st.markdown(f"- 향: {d['향']}")
                st.markdown(f"- 주요성분: {d['주요성분']}")
                st.markdown(f"- 사용감: {d['사용감']}")
                st.markdown(f"- 기능성: {', '.join(d['기능성'])}")
                st.markdown(f"- 포지셔닝: {d['포지셔닝']}")
                st.markdown(f"- 고객사: {d['고객사']}")
                st.markdown(f"- 샘플 송부 요청일: {d['샘플 송부 요청일']}")

# 📄 PDF 생성 탭
with tabs[4]:
    st.subheader("📄 PDF 생성")
    if st.session_state.form_db:
        selected = st.selectbox("PDF 생성할 의뢰 선택", list(st.session_state.form_db.keys()), key="pdf")
        similar = recommend_tfidf(selected, st.session_state.form_db)
        if st.button("📄 PDF 생성"):
            filename = create_pdf(selected, st.session_state.form_db[selected], similar)
            st.success(f"PDF 생성 완료: {filename}")

# 📧 이메일 전송 탭
with tabs[5]:
    st.subheader("📧 이메일 전송")
    if st.session_state.form_db:
        selected = st.selectbox("이메일 보낼 의뢰 선택", list(st.session_state.form_db.keys()), key="email")
        d = st.session_state.form_db[selected]
        subject = st.text_input("제목", value=f"[{d['제품명']}] 최종 의뢰서 전달드립니다")
        body = st.text_area("본문", value="안녕하세요. 최종 의뢰서를 첨부드립니다. 확인 부탁드립니다.")
        similar = recommend_tfidf(selected, st.session_state.form_db)
        pdf_file = create_pdf(selected, d, similar)
        if st.button("📧 이메일 보내기"):
            success = send_email_with_pdf([d["고객사담당자이메일"], d["연구원대표이메일"]], subject, body, pdf_file)
            if success:
                st.success("이메일 전송 완료")

# 📊 Google Sheets 저장 탭
with tabs[6]:
    st.subheader("📊 Google Sheets 저장")
    if st.session_state.form_db:
        selected = st.selectbox("저장할 의뢰 선택", list(st.session_state.form_db.keys()), key="sheets")
        if st.button("📤 Google Sheets에 저장"):
            success = save_to_google_sheets(st.session_state.form_db[selected])
            if success:
                st.success("✅ Google Sheets 저장 완료!")
