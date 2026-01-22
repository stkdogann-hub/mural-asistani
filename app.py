import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tablosu", layout="wide", page_icon="📊")

# --- SİSTEM BAŞLANGICI ---
if 'data' not in st.session_state:
    st.session_state.data = []

# Yan Menü
st.sidebar.title("⚙️ Kontrol Paneli")

# API Key Bağlantısı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("Sistem Hazır ✅")
except:
    st.error("API Key bulunamadı! Lütfen ayarlardan ekleyin.")
    st.stop()

# --- MODEL SEÇİCİ ---
def get_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-1.5-pro')

# --- ANALİZ FONKSİYONU ---
def analyze_image(image):
    model = get_model()
    prompt = """
    Bu resmi analiz et. Mural projelerini veya iş fırsatlarını bir Excel tablosu satırı gibi çıkar.
    
    ÇIKTI FORMATI (Saf JSON Listesi):
    [
      {
        "Proje": "Proje Adı",
        "Tarih": "YYYY-MM-DD" (Tarih yoksa null bırak),
        "Bütçe": "Para birimiyle (Örn: $5000)",
        "Konum": "Şehir/Eyalet",
        "Durum": "Başvuru Bekliyor",
        "Link": "Varsa link, yoksa 'Resimde'",
        "Detay": "Kısa not"
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
st.title("📊 Sıtkı'nın Proje Tablosu")

# 1. Yükleme Alanı
with st.expander("➕ Yeni Dosya Yükle (Tabloya Ekle)", expanded=True):
    uploaded_files = st.file_uploader("Resim, Screenshot veya Notlar", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et ve Tabloya İşle 🚀"):
        bar = st.progress(0, text="Yapay zeka tabloyu dolduruyor...")
        
        for i, file in enumerate(uploaded_files):
            img = Image.open(file)
            results = analyze_image(img)
            
            if results:
                for res in results:
                    st.session_state.data.append(res)
            
            bar.progress((i + 1) / len(uploaded_files))
            
        bar.empty()
        st.success("Veriler tabloya eklendi!")

# 2. TABLO ALANI (Excel Görünümü)
st.divider()
st.subheader("📋 Proje Listesi")

# Veri varsa veya yoksa tablo yapısını oluştur
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
else:
    # Boşken bile başlıkları göster
    df = pd.DataFrame(columns=["Proje", "Tarih", "Bütçe", "Konum", "Durum", "Link", "Detay"])

# Tarih formatını düzelt
if 'Tarih' in df.columns and not df.empty:
    df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')

# Tablo Ayarları
column_config = {
    "Proje": st.column_config.TextColumn("Proje Adı", width="medium"),
    "Tarih": st.column_config.DateColumn("Son Başvuru", format="DD.MM.YYYY"),
    "Bütçe": st.column_config.TextColumn("Bütçe", width="small"),
    "Link": st.column_config.LinkColumn("Link", display_text="🔗 Git"),
    "Durum": st.column_config.SelectboxColumn("Durum", options=["Başvuru Bekliyor", "Başvuruldu", "Tamamlandı"]),
}

# TABLOYU ÇİZ
st.data_editor(
    df,
    column_config=column_config,
    use_container_width=True,
    num_rows="dynamic", # Satır ekleyip silmene izin verir
    hide_index=True,
    key="editor"
)

# İndirme Butonu
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Excel Olarak İndir (CSV)", csv, "mural_listesi.csv", "text/csv")
