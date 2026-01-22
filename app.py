import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tracker", layout="wide", page_icon="🎨")

# API Key'i Güvenli Şekilde Alıyoruz (Streamlit Secrets'tan)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key bulunamadı! Lütfen Streamlit ayarlarından ekleyin.")
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
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    Bu resmi bir mural sanatçısı için analiz et. Resim bir ekran görüntüsü veya el çizimi notlar olabilir.
    GÖREV: Resimdeki TÜM projeleri tespit et.
    ÇIKTI FORMATI (JSON Listesi):
    [
      {
        "project_name": "Proje Adı",
        "deadline": "YYYY-MM-DD" (Tarih yoksa null),
        "price": "Bütçe",
        "state": "Konum",
        "link": "Link veya 'Notlardan'",
        "wall_desc": "Görsel tanım (Örn: Köprü altı)"
      }
    ]
    Sadece JSON ver.
    """
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"HATA OLUŞTU: {e}") # <--- Hatayı ekrana basacak!
        return []

# --- ARAYÜZ ---
st.title("🎨 Sıtkı'nın Mural Asistanı")
st.markdown("---")

with st.expander("➕ Yeni Proje / Screenshot Yükle", expanded=True):
    uploaded_files = st.file_uploader("Resimleri Seç", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et 🚀"):
        if 'projects' not in st.session_state: st.session_state.projects = []
        
        for file in uploaded_files:
            img = Image.open(file)
            results = analyze_image_with_ai(img)
            for res in results:
                res['image_data'] = file # Resmi sakla
                st.session_state.projects.append(res)
        st.success("Listeye eklendi!")

if 'projects' in st.session_state and st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    # Tarihe göre sıralama (Hata önleyici)
    if 'deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df = df.sort_values(by='deadline')

    st.subheader(f"📋 Takip Listesi ({len(df)})")
    
    for index, row in df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                if 'image_data' in row: st.image(row['image_data'], use_container_width=True)
            with c2:
                d_str = row['deadline'].strftime('%Y-%m-%d') if pd.notnull(row['deadline']) else "Tarih Yok"
                st.markdown(f"### {row.get('project_name', 'Proje')}")
                st.caption(f"📍 {row.get('state', '-')} | 💰 {row.get('price', '-')}")
                if pd.notnull(row['deadline']): st.markdown(f"🗓️ **:red[{d_str}]**")
            with c3:
                cal_link = create_calendar_link(f"DEADLINE: {row.get('project_name')}", row.get('deadline'), f"Link: {row.get('link')}")
                st.link_button("📅 Takvime Ekle", cal_link)
                if row.get('link') and row.get('link') != 'Notlardan':
                    st.link_button("🔗 Link", row.get('link'))
            st.markdown("---")
