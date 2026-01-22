import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# Yan Menü: Sistem Bilgisi
st.sidebar.header("🛠 Sistem Durumu")

# 1. API Key Bağlantısı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("Anahtar Bağlandı ✅")
except:
    st.error("API Key yok! Lütfen Secrets ayarına ekle.")
    st.stop()

# --- AKILLI MODEL SEÇİCİ (OTOMATİK) ---
def get_working_model():
    """Senin hesabında çalışan modeli otomatik bulur"""
    try:
        # Mevcut modelleri listele
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Öncelik sırasına göre dene
        priority_list = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']
        
        selected_model = None
        for model_name in priority_list:
            if model_name in available_models:
                selected_model = model_name
                break
        
        # Hiçbiri yoksa listedeki ilk "vision" modelini al
        if not selected_model:
            for m in available_models:
                if 'vision' in m or '1.5' in m:
                    selected_model = m
                    break
        
        # Bulunan modeli ekrana yaz (Bilgi amaçlı)
        if selected_model:
            st.sidebar.info(f"Kullanılan Model: {selected_model}")
            return genai.GenerativeModel(selected_model)
        else:
            st.sidebar.error("Hiçbir model bulunamadı!")
            return None
            
    except Exception as e:
        st.sidebar.error(f"Model arama hatası: {e}")
        # Hata olursa varsayılan olarak en garantisini dene
        return genai.GenerativeModel('gemini-1.5-flash')

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
    # OTOMATİK MODELİ ÇAĞIR
    model = get_working_model()
    
    if not model:
        return []

    prompt = """
    Bu resmi analiz et.
    GÖREV: Resimdeki mural projelerini veya notları tespit et.
    ÇIKTI (Sadece JSON):
    [
      {
        "project_name": "Proje Adı",
        "deadline": "YYYY-MM-DD" (Yoksa null),
        "price": "Bütçe",
        "state": "Konum",
        "link": "Link veya 'Resimde'",
        "wall_desc": "Not"
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

with st.expander("➕ Yeni Proje / Resim Yükle", expanded=True):
    uploaded_files = st.file_uploader("Resim Yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et 🚀"):
        if 'projects' not in st.session_state: st.session_state.projects = []
        
        bar = st.progress(0, text="Otomatik model seçiliyor ve analiz ediliyor...")
        
        for i, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                results = analyze_image_with_ai(img)
                if results:
                    for res in results:
                        res['image_data'] = file
                        st.session_state.projects.append(res)
            except Exception as e:
                st.error(f"Dosya hatası: {e}")
            
            bar.progress((i + 1) / len(uploaded_files))
        
        bar.empty()
        st.success("✅ Listeye eklendi!")

if 'projects' in st.session_state and st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    if 'deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='deadline')

    st.subheader(f"📋 Projeler ({len(df)})")
    
    for index, row in df.iterrows():
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            if 'image_data' in row: st.image(row['image_data'], use_container_width=True)
        with c2:
            st.markdown(f"### {row.get('project_name', 'Proje')}")
            st.caption(f"📍 {row.get('state')} | 💰 {row.get('price')}")
            if pd.notnull(row.get('deadline')):
                st.markdown(f"🗓️ **:red[{row['deadline'].strftime('%Y-%m-%d')}]**")
        with c3:
            cal = create_calendar_link(f"Mural: {row.get('project_name')}", row.get('deadline'), row.get('link'))
            st.link_button("📅 Takvime Ekle", cal)
        st.divider()
