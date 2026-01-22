import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tablosu", layout="wide", page_icon="🎨")

st.title("🎨 Sıtkı'nın Mural Tablosu (Pro Versiyon)")

# --- SİSTEM HAZIRLIK ---
if 'data' not in st.session_state:
    st.session_state.data = []

# API Key Bağlantısı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"🚨 API Key Hatası: {e}")
    st.stop()

# --- ANALİZ FONKSİYONU ---
def analyze_image_final(image):
    # DEĞİŞİKLİK BURADA: Flash yerine PRO modelini kullanıyoruz.
    # Bu model her sürümde çalışır.
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = """
    Bu resmi analiz et. Mural projelerini veya iş fırsatlarını tablo verisi olarak çıkar.
    Eğer resimde proje yoksa boş liste ver.
    
    ÇIKTI FORMATI (Saf JSON):
    [
      {
        "Proje": "Proje Adı",
        "Tarih": "YYYY-MM-DD",
        "Bütçe": "Para birimiyle",
        "Konum": "Şehir/Eyalet",
        "Link": "Varsa link",
        "Notlar": "Detay"
      }
    ]
    """
    
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        # Hatayı ekrana bas ki görelim (ama PRO modelde hata vermeyecek)
        st.error(f"AI Hatası: {e}")
        return []

# --- ARAYÜZ ---
with st.container():
    uploaded_files = st.file_uploader("Resimleri Yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Tabloya Dönüştür 🚀"):
        
        my_bar = st.progress(0, text="Yapay zeka verileri tabloya işliyor...")
        
        for i, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                # Analiz fonksiyonunu çağır
                results = analyze_image_final(img)
                
                if results:
                    for res in results:
                        st.session_state.data.append(res)
                else:
                    st.warning(f"{file.name}: Veri bulunamadı.")
                    
            except Exception as e:
                st.error(f"Dosya Hatası: {e}")
            
            my_bar.progress((i + 1) / len(uploaded_files))
            
        my_bar.empty()
        st.success("İşlem Tamamlandı!")

# --- TABLO ALANI ---
st.divider()
st.subheader("📋 Proje Listesi")

# Tablo Verisi Hazırlama
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
else:
    # Boşken başlıkları göster
    df = pd.DataFrame(columns=["Proje", "Tarih", "Bütçe", "Konum", "Link", "Notlar"])

# Tabloyu Çiz (Excel Görünümü)
st.data_editor(
    df,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="🔗 Git"),
        "Tarih": st.column_config.DateColumn("Tarih", format="DD.MM.YYYY"),
    },
    use_container_width=True,
    num_rows="dynamic",
    key="project_table"
)
