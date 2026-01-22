import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# Sürüm Kontrolü (Hata ayıklamak için ekrana yazıyoruz)
st.sidebar.info(f"AI Kütüphane Sürümü: {genai.__version__}")

# API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key hatası! Lütfen Secrets ayarlarını kontrol et.")
    st.stop()

# --- FONKSİYONLAR ---
def create_calendar_link(title, date_str, details):
    try:
        base = "https://www.google.com/calendar/render?action=TEMPLATE"
        dt = pd.to_datetime(date_str)
        dates = f"{dt.strftime('%Y%m%d')}/{dt.strftime('%Y%m%d')}"
        url = f"{base}&text={urllib.parse.quote(title)}&dates={dates}&details={urllib.parse.quote(details)}"
        return url
    except:
        return "#"

def analyze_image_with_ai(image):
    # En hızlı ve yeni model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Bu resmi bir mural sanatçısı için analiz et.
    GÖREV: Resimdeki TÜM projeleri tespit et.
    ÇIKTI: Sadece JSON listesi ver.
    [
      {
        "project_name": "Proje Adı",
        "deadline": "YYYY-MM-DD" (Tarih yoksa null),
        "price": "Bütçe",
        "state": "Konum",
        "link": "Link veya 'Resimde'",
        "wall_desc": "Notlar"
      }
    ]
    """
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"AI Analiz Hatası: {e}")
        return []

# --- ARAYÜZ ---
st.title("🎨 Sıtkı'nın Mural Asistanı")
st.markdown("---")

with st.expander("➕ Yeni Proje Yükle", expanded=True):
    uploaded_files = st.file_uploader("Resim Seç", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et 🚀"):
        if 'projects' not in st.session_state: st.session_state.projects = []
        
        bar = st.progress(0, text="Analiz ediliyor...")
        for i, file in enumerate(uploaded_files):
            img = Image.open(file)
            results = analyze_image_with_ai(img)
            if results:
                for res in results:
                    res['image_data'] = file
                    st.session_state.projects.append(res)
            bar.progress((i + 1) / len(uploaded_files))
        
        bar.empty()
        st.success("Listeye eklendi!")

# --- LİSTE ---
if 'projects' in st.session_state and st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    if 'deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='deadline')

    st.subheader(f"📋 Projeler ({len(df)})")
    for index, row in df.iterrows():
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            if 'image_data' in row: st.image(row['image_data'])
        with c2:
            st.markdown(f"### {row.get('project_name')}")
            st.caption(f"📍 {row.get('state')} | 💰 {row.get('price')}")
            if pd.notnull(row.get('deadline')):
                st.markdown(f"🗓️ **:red[{row['deadline'].strftime('%Y-%m-%d')}]**")
        with c3:
            st.link_button("📅 Takvime Ekle", create_calendar_link(f"DEADLINE: {row.get('project_name')}", row.get('deadline'), row.get('link')))
        st.divider()
