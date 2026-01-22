import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# --- YAN MENÜ (DEBUG VE AYARLAR) ---
st.sidebar.title("⚙️ Sistem Durumu")

# 1. API Key Kontrolü
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("Anahtar Bulundu ✅")
except Exception as e:
    st.error("API Key bulunamadı! Lütfen Secrets ayarlarını kontrol et.")
    st.stop()

# 2. Kütüphane Sürümü
st.sidebar.info(f"AI Sürümü: {genai.__version__}")

# --- ANA FONKSİYONLAR ---

def get_vision_model():
    """Çalışan en iyi görüntü modelini otomatik seçer"""
    try:
        # Önce en hızlı ve yeni modeli dene
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        # Olmazsa pro versiyonunu dene
        return genai.GenerativeModel('gemini-1.5-pro')

def create_calendar_link(title, date_str, details):
    """Takvim linki oluşturur"""
    try:
        base = "https://www.google.com/calendar/render?action=TEMPLATE"
        dt = pd.to_datetime(date_str)
        dates = f"{dt.strftime('%Y%m%d')}/{dt.strftime('%Y%m%d')}"
        url = f"{base}&text={urllib.parse.quote(title)}&dates={dates}&details={urllib.parse.quote(details)}"
        return url
    except:
        return "#"

def analyze_image_with_ai(image):
    """Resmi Analiz Et"""
    # Modeli güvenli şekilde çağır
    model = get_vision_model()
    
    prompt = """
    Bu resimdeki mural projelerini veya iş fırsatlarını analiz et.
    GÖREV: Tüm proje detaylarını JSON formatında listele.
    
    ÇIKTI FORMATI (Sadece bu JSON listesini ver):
    [
      {
        "project_name": "Proje İsmi",
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
        # JSON temizliği
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Analiz sırasında hata: {e}")
        return []

# --- ARAYÜZ (FRONTEND) ---

st.title("🎨 Sıtkı'nın Mural Asistanı")
st.markdown("---")

# Resim Yükleme Alanı
with st.expander("➕ Yeni Proje Ekle", expanded=True):
    uploaded_files = st.file_uploader("Resim Seç", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et 🚀"):
        if 'projects' not in st.session_state: st.session_state.projects = []
        
        my_bar = st.progress(0, text="Yapay zeka çalışıyor...")
        
        for i, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                results = analyze_image_with_ai(img)
                if results:
                    for res in results:
                        res['image_data'] = file
                        st.session_state.projects.append(res)
            except Exception as e:
                st.error(f"Dosya okuma hatası: {e}")
                
            my_bar.progress((i + 1) / len(uploaded_files))
        
        my_bar.empty()
        st.success("İşlem Tamamlandı!")

# --- LİSTE GÖRÜNÜMÜ ---

if 'projects' in st.session_state and st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    
    # Tarih sıralaması
    if 'deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='deadline')

    st.subheader(f"📋 Projeler ({len(df)})")
    
    for index, row in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            
            with c1:
                if 'image_data' in row:
                    st.image(row['image_data'], use_container_width=True)
            
            with c2:
                name = row.get('project_name', 'Proje')
                deadline = row.get('deadline')
                
                st.markdown(f"### {name}")
                st.caption(f"📍 {row.get('state', '-')} | 💰 {row.get('price', '-')}")
                st.write(f"📝 {row.get('wall_desc', '-')}")
                
                if pd.notnull(deadline):
                    st.markdown(f"🗓️ **:red[{deadline.strftime('%Y-%m-%d')}]**")
            
            with c3:
                cal_link = create_calendar_link(f"Mural: {name}", row.get('deadline'), row.get('link'))
                st.link_button("📅 Takvime Ekle", cal_link)
                
            st.divider()
        
