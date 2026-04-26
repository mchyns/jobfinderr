import streamlit as st
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

# ========================
# Page Config
# ========================
st.set_page_config(
    page_title="JobFinder",
    page_icon="🔍",
    layout="wide"
)

# ========================
# Custom CSS
# ========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { background-color: #0a0a0f; color: #e0e0e0; }

h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

.hero {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
    border: 1px solid #1e2d40;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 50% 50%, rgba(0,200,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-family: 'Space Mono', monospace !important;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00c8ff, #0077ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.hero-sub {
    color: #556070;
    font-size: 0.95rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.stat-box {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    color: #00c8ff;
    font-weight: 700;
}

.stat-label {
    color: #556070;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.job-card {
    background: #0d1117;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}

.job-card:hover { border-color: #00c8ff; }

.job-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

.job-company { color: #00c8ff; font-size: 0.9rem; font-weight: 600; }
.job-location { color: #556070; font-size: 0.85rem; }

.tag {
    display: inline-block;
    background: #1e2d40;
    color: #00c8ff;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.75rem;
    margin: 2px;
    font-family: 'Space Mono', monospace;
}

.skor-badge {
    background: linear-gradient(90deg, #00c8ff22, #0077ff22);
    border: 1px solid #00c8ff44;
    color: #00c8ff;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}

.rank-num {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    color: #1e2d40;
    font-weight: 700;
}

.sumber-badge {
    background: #1a1a2e;
    color: #7070aa;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ========================
# Load & Index Data
# ========================
@st.cache_resource
def load_data():
    with open("data_bersih.json", "r") as f:
        loker_list = json.load(f)
    dokumen = [l["teks_gabung"] for l in loker_list]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(dokumen)
    bm25 = BM25Okapi([d.split() for d in dokumen])
    return loker_list, vectorizer, tfidf_matrix, bm25

loker_list, vectorizer, tfidf_matrix, bm25 = load_data()

def cari(query, metode="bm25", top_k=10):
    query = query.lower()
    if metode == "tfidf":
        skor = cosine_similarity(vectorizer.transform([query]), tfidf_matrix).flatten()
    else:
        skor = bm25.get_scores(query.split())
    ranking = sorted(enumerate(skor), key=lambda x: x[1], reverse=True)
    return [(loker_list[i], s) for i, s in ranking[:top_k] if s > 0]

# ========================
# Hero Section
# ========================
st.markdown("""
<div class="hero">
    <div class="hero-title">🔍 JOBFINDER</div>
    <div class="hero-sub">Smart Job Search · Powered by TF-IDF & BM25</div>
</div>
""", unsafe_allow_html=True)

# Stats
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(loker_list)}</div><div class="stat-label">Total Loker</div></div>', unsafe_allow_html=True)
with c2:
    sumber = len(set(l.get("sumber","") for l in loker_list))
    st.markdown(f'<div class="stat-box"><div class="stat-num">{sumber}</div><div class="stat-label">Sumber Data</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-num">2</div><div class="stat-label">Metode IR</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ========================
# Search Bar
# ========================
col_input, col_metode = st.columns([3, 1])
with col_input:
    query = st.text_input("", placeholder="🔍  Cari posisi, skill, atau perusahaan...", label_visibility="collapsed")
with col_metode:
    metode = st.selectbox("", ["BM25", "TF-IDF"], label_visibility="collapsed")

# ========================
# Hasil Pencarian
# ========================
if query:
    hasil = cari(query, metode=metode.lower().replace("-",""))
    
    if hasil:
        st.markdown(f"**{len(hasil)} hasil** untuk **`{query}`** menggunakan **{metode}**")
        st.markdown("---")
        
        for rank, (loker, skor) in enumerate(hasil, 1):
            tags = loker.get('tags', '')
            tag_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in tags.split(",") if t.strip()][:5])
            sumber = loker.get('sumber', '')
            url = loker.get('url', '#')
            
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div style="flex:1">
                        <span class="rank-num">#{rank}</span>
                        <div class="job-title">{loker['judul'].title()}</div>
                        <div style="margin-bottom:8px">
                            <span class="job-company">🏢 {loker['perusahaan'].title()}</span>
                            &nbsp;&nbsp;
                            <span class="job-location">📍 {loker['lokasi'].title()}</span>
                        </div>
                        <div style="margin-bottom:10px">{tag_html}</div>
                    </div>
                    <div style="text-align:right">
                        <span class="skor-badge">⚡ {skor:.4f}</span><br><br>
                        <span class="sumber-badge">{sumber}</span>
                    </div>
                </div>
                <a href="{url}" target="_blank" style="color:#00c8ff; font-size:0.85rem; text-decoration:none;">Lihat Loker →</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada hasil untuk query tersebut. Coba kata kunci lain.")

else:
    st.markdown("""
    <div style="text-align:center; padding:60px; color:#556070;">
        <div style="font-size:3rem">🔍</div>
        <div style="font-family:'Space Mono',monospace; margin-top:10px;">Ketik sesuatu untuk mulai mencari</div>
        <div style="font-size:0.85rem; margin-top:8px;">contoh: software engineer, data analyst, marketing</div>
    </div>
    """, unsafe_allow_html=True)