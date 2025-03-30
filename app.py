
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="바디케어 샘플 추천 시스템", page_icon="🧴")
st.title("🧴 바디케어 샘플 자동 추천 시스템")

product_name = st.text_input("제품명 입력", "오브제 바이 쿤달 바디워시")
product_type = st.selectbox("제품 타입 선택", ["바디워시", "스크럽", "핸드워시"])
customer_text = st.text_area("요구사항을 자유롭게 입력하세요",
    "끈적임 없고 세정력이 강하며 향이 오래가는 제품을 원해요")

def extract_keywords(text):
    keywords = {}
    if re.search("끈적.*않", text): keywords['끈적임'] = '낮음'
    if re.search("세정력.*강|깨끗", text): keywords['세정력'] = '강함'
    if re.search("풍성.*거품", text): keywords['거품감'] = '풍성'
    if re.search("향.*오래|지속", text): keywords['지속력'] = '높음'
    if re.search("머스크", text): keywords['향'] = '머스크'
    return keywords

keywords = extract_keywords(customer_text)
st.subheader("🔍 추출된 사용감 키워드")
st.json(keywords)

cluster_profiles = pd.DataFrame({
    '클러스터': [0, 1, 2],
    '끈적임': [2, 0, 1],
    '세정력': [1, 2, 1],
    '지속력': [0, 2, 1],
}).set_index('클러스터')

scale_map = {'낮음': 0, '중간': 1, '높음': 2, '강함': 2, '약함': 0}
input_vector = {}
for k in cluster_profiles.columns:
    v = keywords.get(k)
    if v: input_vector[k] = scale_map.get(v, 1)

def compute_distance(row, target):
    score = 0
    count = 0
    for k, v in target.items():
        if k in row:
            score += (row[k] - v) ** 2
            count += 1
    return (score / count) ** 0.5 if count > 0 else float('inf')

cluster_profiles['distance'] = cluster_profiles.apply(lambda row: compute_distance(row, input_vector), axis=1)
recommended_cluster = cluster_profiles['distance'].idxmin()

st.subheader("✅ 추천 결과")
st.success(f"추천 클러스터: 클러스터 {recommended_cluster}번")

sample_recommendations = {
    0: ["드리오페 바디워시 자스민머스크", "라라츄 홈쇼핑 바디워시"],
    1: ["쿤달 퓨어 바디워시 베이비파우더", "쿤달 퓨어 바디워시 화이트머스크"],
    2: ["낫포유 클리어 바디스크럽", "슬로우허밍 바디스크럽"]
}

st.subheader("🧪 유사 추천 처방")
for item in sample_recommendations.get(recommended_cluster, []):
    st.markdown(f"- {item}")
