import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json
import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# API Key Kontrolü
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key bulunamadı! Lütfen Streamlit ayarlarından 'Secrets' kısmına ekleyin.")
    st.stop()

# --- FONKSİYONLAR ---

def create_calendar_link(title, date_str, details):
    """Google Takvim linki oluşturur"""
    try:
        base = "https://www.google.com/calendar/render?action=TEMPLATE"
        dt = pd.to_datetime(date_str)
        dates = f"{dt.strftime('%Y%m%d')}/{dt.strftime('%Y%m%d')}"
        url = f"{base}&text={urllib.parse.quote(title)}&dates={dates}&details={urllib.parse.quote(details)}"
        return url
    except:
        return "#"

def analyze_image_with_ai(image):
    """Resmi Gemini ile analiz eder"""
    # En güvenilir model (Flash)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = """
    Bu resmi bir mural sanatçısı için analiz et.
    GÖREV: Resimdeki TÜM projeleri tespit et. Defter notlarıysa her başlığı ayır.
    
    ÇIKTI FORMATI (Sadece saf JSON listesi ver):
    [
      {
        "project_name": "Proje Adı",
        "deadline": "YYYY-MM-DD" (Tarih yoksa null),
        "price": "Bütçe",
        "state": "Konum",
        "link": "Link veya 'Resimde'",
        "wall_desc": "Görsel not"
      }
    ]
    """
    
    # HATA VEREN KISIM BURASIYDI (Şimdi düzeltildi)
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        # Hata olursa ekrana yaz ama uygulamayı çökertme
        st.error(f"AI Analiz Hatası: {e}")
        return []

# --- ARAYÜZ ---

st.title("🎨 Sıtkı'nın Mural Asistanı")
st.markdown("---")

with st.expander("➕ Yeni Proje Yükle", expanded=True):
    uploaded_files = st.file_uploader("Resimleri Seç", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et 🚀"):
        if 'projects' not in st.session_state: st.session_state.projects = []
        
        my_bar = st.progress(0, text="Yapay zeka çalışıyor...")
        
        for i, file in enumerate(uploaded_files):
            img = Image.open(file)
            results = analyze_image_with_ai(img)
            
            if results:
                for res in results:
                    res['image_data'] = file
                    st.session_state.projects.append(res)
            
            my_bar.progress((i + 1) / len(uploaded_files))
            
        my_bar.empty()
        st.success("✅ İşlem Tamam!")

# --- LİSTE ---

if 'projects' in st.session_state and st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    if 'deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='deadline')

    st.subheader(f"📋 Projeler ({len(df)})")
    
    for index, row in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                if 'image_data' in row: st.image(row['image_data'], use_container_width=True)
            with c2:
                name = row.get('project_name', 'Proje')
                deadline = row.get('deadline')
                st.markdown(f"### {name}")
                st.caption(f"📍 {row.get('state')} | 💰 {row.get('price')}")
                
                if pd.notnull(deadline):
                    d_str = deadline.strftime('%Y-%m-%d')
                    st.markdown(f"🗓️ **Deadline:** :red[{d_str}]")
                else:
                    st.write("🗓️ Tarih Yok")
            with c3:
                cal_
