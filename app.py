import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json
import io

# --- AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# Yan Menü: Sistem Durumu
st.sidebar.header("🛠 Sistem Paneli")

# 1. API Key Bağlantısı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("Sistem Online 🟢")
except:
    st.error("API Key eksik! Lütfen ayarlardan ekleyin.")
    st.stop()

# --- AKILLI MODEL SEÇİCİ ---
def get_working_model():
    """Çalışan en iyi modeli otomatik bulur"""
    try:
        # Öncelik sırası: Flash (Hızlı) -> Pro (Güçlü)
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        for p in priority:
            if p in available:
                st.sidebar.info(f"Motor: {p.split('/')[-1]}")
                return genai.GenerativeModel(p)
        
        return genai.GenerativeModel('gemini-1.5-flash') # Varsayılan
    except:
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
        return None

def analyze_image_with_ai(image):
    model = get_working_model()
    if not model: return []

    prompt = """
    Bu resmi analiz et ve içindeki iş fırsatlarını/projeleri tablo verisi olarak çıkar.
    ÇIKTI (Saf JSON listesi):
    [
      {
        "Proje Adı": "Proje ismini yaz",
        "Tarih": "YYYY-MM-DD" (Yoksa null),
        "Bütçe": "Para birimiyle yaz",
        "Konum": "Şehir/Ülke",
        "Link": "Varsa URL",
        "Notlar": "Kısa açıklama"
      }
    ]
    """
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except:
        return []

# --- ARAYÜZ ---
st.title("🎨 Sıtkı'nın Mural Asistanı")
st.markdown("### 📊 Proje Takip Tablosu")

# Dosya Yükleme
with st.expander("➕ Yeni İş / Resim Ekle", expanded=False):
    uploaded_files = st.file_uploader("Resim yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Tabloya Ekle 🚀"):
        if 'data' not in st.session_state: st.session_state.data = []
        
        bar = st.progress(0, text="Veriler tabloya işleniyor...")
        for i, file in enumerate(uploaded_files):
            img = Image.open(file)
            results = analyze_image_with_ai(img)
            if results:
                for res in results:
                    # Takvim Linkini Hazırla
                    cal_url = create_calendar_link(
                        f"Mural: {res.get('Proje Adı')}", 
                        res.get('Tarih'), 
                        f"Bütçe: {res.get('Bütçe')}\nLink: {res.get('Link')}"
                    )
                    res['Takvime Ekle'] = cal_url # Linki veriye ekle
                    st.session_state.data.append(res)
            bar.progress((i + 1) / len(uploaded_files))
        bar.empty()
        st.success("Tablo güncellendi!")

# --- TABLO GÖRÜNÜMÜ (EXCEL TARZI) ---
if 'data' in st.session_state and st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    # Tarih formatını düzelt
    if 'Tarih' in df.columns:
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')

    # TABLO AYARLARI (Sütunları Güzelleştirme)
    column_config = {
        "Proje Adı": st.column_config.TextColumn("Proje Adı", width="medium"),
        "Tarih": st.column_config.DateColumn("Son Başvuru", format="DD.MM.YYYY"),
        "Bütçe": st.column_config.TextColumn("Bütçe", width="small"),
        "Konum": st.column_config.TextColumn("Konum", width="small"),
        "Link": st.column_config.LinkColumn("Başvuru Linki", display_text="🔗 Başvur"),
        "Takvime Ekle": st.column_config.LinkColumn("Takvim", display_text="📅 Kaydet"),
        "Notlar": st.column_config.TextColumn("Notlar", width="large"),
    }

    # Tabloyu Göster (Sıralanabilir, Genişletilebilir)
    st.dataframe(
        df, 
        use_container_width=True, 
        column_config=column_config, 
        hide_index=True
    )

    # İndirme Butonu (Excel/CSV)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tabloyu İndir (CSV)",
        data=csv,
        file_name='mural_projeleri.csv',
        mime='text/csv',
    )

else:
    st.info("Tablo boş. Yukarıdan resim yükleyerek başlayabilirsin.")
