
# 📤 PDF 자동 업로드 및 이메일 전송 시스템

이 프로젝트는 Streamlit 기반의 웹 앱으로, 사용자가 업로드한 PDF 파일을 Google Drive에 자동으로 저장하고, 해당 공유 링크를 입력된 이메일 주소로 전송하는 기능을 제공합니다.

## 🧩 주요 기능

- 📁 PDF 파일 업로드
- ☁️ Google Drive 자동 저장
- 🔗 공유 링크 생성
- 📧 Gmail API를 통한 자동 이메일 전송
- 🧑‍💻 Streamlit 기반 UI

---

## 📂 디렉토리 구조

```
📦 sample-request-form-2/
├── main_integrated.py               # Streamlit 메인 실행 파일
├── requirements.txt                 # 의존 패키지 목록
├── NanumGothic.ttf                  # 한글 폰트 파일
├── README.md                        # 프로젝트 설명서
├── README_FONT.txt                  # 폰트 관련 설명서
├── secrets.toml.example             # (선택) 인증 템플릿 예시
└── client_secrets.json             # 🔐 Google OAuth 인증 파일 (직접 업로드 필요, .gitignore 추천)
```

---

## 🚀 실행 방법

```bash
pip install -r requirements.txt
streamlit run main_integrated.py
```

최초 실행 시 Google 인증창이 열리며,  
Drive와 Gmail API 사용을 위한 권한 허용이 필요합니다.

---

## 🔐 OAuth 관련

`client_secrets.json` 파일은 개인 인증 정보가 포함된 민감한 파일입니다.  
GitHub에 업로드하지 않도록 `.gitignore`에 추가하는 것을 권장합니다.

---

## 🙌 만든 이유

- 영업팀이 고객 의뢰서를 PDF로 자동 정리하고
- 버튼 하나로 이메일 발송까지 처리하도록 도와주는 자동화 도구입니다.

---

## 📧 문의

문의: duskinlab@gmail.com
