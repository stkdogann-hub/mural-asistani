import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tablosu", layout="wide", page_icon="🎨")

# Başlık
st.title("🎨 Sıtkı'nın Mural Tablosu (Otomatik Model Seçici)")

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

# --- AKILLI MODEL SEÇİCİ FONKSİYONU ---
def get_response_from_any_model(prompt, image):
    """
    Sırasıyla tüm modelleri dener. Hangisi çalışırsa cevabı ondan alır.
    Böylece 'Model Not Found' hatası engellenir.
    """
    # Denenecek Modeller Listesi (Yeniden eskiye doğru)
    models_to_try = [
        'gemini-1.5-flash',      # En Hızlı
        'gemini-1.5-pro',        # En Güçlü
        'gemini-pro-vision',     # Eski Altyapı (Yedek)
    ]
    
    last_error = ""
    
    for model_name in models_to_try:
        try:
            # Modeli yükle
            model = genai.GenerativeModel(model_name)
            
            # Cevap iste
            response = model.generate_content([prompt, image])
            
            # Eğer buraya geldiyse çalışmış demektir
            st.toast(f"✅ Başarılı Model: {model_name}", icon="🤖")
            return response.text
            
        except Exception as e:
            # Hata verirse bir sonrakine geç
            last_error = e
            continue
            
    # Hiçbiri çalışmazsa hata döndür
    st.error(f"Tüm modeller denendi ama başarısız oldu. Son hata: {last_error}")
    return None

# --- ANALİZ FONKSİYONU ---
def analyze_image_safe(image):
    prompt = """
    Bu resmi analiz et. Mural projelerini tablo verisi olarak çıkar.
    ÇIKTI FORMATI (Sadece saf JSON listesi):
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
    
    # Akıllı fonksiyonu çağır
    raw_text = get_response_from_any_model(prompt, image)
    
    if raw_text:
        try:
            # JSON Temizliği
            cleaned_text = raw_text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)
        except:
            return []
    else:
        return []

# --- ARAYÜZ ---
with st.container():
    uploaded_files = st.file_uploader("Resimleri Yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Tabloya Dönüştür 🚀"):
        
        progress_bar = st.progress(0, text="Uygun model aranıyor ve analiz ediliyor...")
        
        for i, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                results = analyze_image_safe(img)
                
                if results:
                    for res in results:
                        st.session_state.data.append(res)
                else:
                    st.warning(f"{file.name}: Veri çekilemedi (Resim net olmayabilir).")
                    
            except Exception as e:
                st.error(f"Dosya işleme hatası: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        progress_bar.empty()
        st.success("İşlem Tamamlandı!")

# --- TABLO ALANI ---
st.divider()
st.subheader("📋 Proje Listesi")

# Tablo Verisi
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
else:
    df = pd.DataFrame(columns=["Proje", "Tarih", "Bütçe", "Konum", "Link", "Notlar"])

# Tabloyu Çiz
st.data_editor(
    df,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="🔗 Git"),
        "Tarih": st.column_config.DateColumn("Tarih", format="DD.MM.YYYY"),
    },
    use_container_width=True,
    num_rows="dynamic",
    key="mural_table"
)
