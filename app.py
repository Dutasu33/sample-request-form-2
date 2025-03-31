import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from PIL import Image
import os

# 더미 데이터
data = {
    "처방ID": [f"P{str(i+1).zfill(3)}" for i in range(20)],
    "사용감설명": [
        "끈적임 없이 촉촉하고 산뜻함", "세정력이 좋고 거품이 풍성함", "보습감이 뛰어나고 잔향이 오래 감",
        "피부가 편안하고 순한 사용감", "거칠지 않고 부드럽게 각질 제거됨", "세정 후 당김 없이 촉촉함",
        "향이 오래가고 부드러운 마무리감", "시원하고 개운한 사용감", "스크럽 입자가 자극 없이 부드러움",
        "상쾌하고 깔끔한 세정력", "풍성한 거품과 은은한 향", "흡수가 빠르고 산뜻한 마무리감",
        "부드럽게 마사지 되며 보습력 우수", "촉촉하지만 번들거리지 않음", "끈적임 없이 산뜻하게 흡수",
        "상쾌하고 향기로운 사용감", "자극 없이 세정되며 부드러움", "고급스러운 향이 오래 지속",
        "세정 후 피부가 매끄럽고 촉촉함", "빠르게 흡수되며 무향에 가까움"
    ]
}
df = pd.DataFrame(data)

# 벡터화 및 클러스터링
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df["사용감설명"])
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["클러스터"] = kmeans.fit_predict(tfidf_matrix)

# 앱 UI
st.set_page_config(page_title="힘들다연습 - 클러스터 처방 추천", page_icon="🧴")
st.title("💬 VOC 기반 클러스터 예측 및 사용감 키워드 시각화")

voc_input = st.text_area("📥 제품 사용감 VOC를 입력하세요:")

if voc_input:
    voc_vec = vectorizer.transform([voc_input])
    cluster = kmeans.predict(voc_vec)[0]
    st.success(f"예측된 클러스터: {cluster}번")

    st.subheader("📋 해당 클러스터의 대표 처방")
    top3 = df[df["클러스터"] == cluster].head(3)
    st.table(top3[["처방ID", "사용감설명"]])

    st.subheader("🖼️ 클러스터 사용감 키워드 시각화")
    image_path = f"wordclouds/cluster_{cluster}.png"
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"Cluster {cluster} WordCloud", use_column_width=True)
else:
    st.info("왼쪽에 VOC를 입력하면 클러스터와 대표 처방이 표시됩니다.")
