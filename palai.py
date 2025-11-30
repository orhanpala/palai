import streamlit as st
import google.generativeai as genai

# --- YAPILANDIRMA ---
API_KEY = "AIzaSyAngV0YDtdwAE8t1HuPhVRmD3Ml22kYiB4"  
MODEL_ADI = "gemini-2.5-pro"

st.set_page_config(
    page_title="PALAİ",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TASARIM (CSS) ---
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
    }
    
    /* Input Alanı */
    .centered-input .stTextInput > div > div > input {
        background-color: #1E1F20;
        color: white;
        border-radius: 24px;
        padding: 12px 20px;
        border: 1px solid #3c4043;
        font-size: 18px;
    }
    
    input { caret-color: #4285F4; }

    /* Başlık Stili */
    .big-title {
        text-align: center;
        font-size: 7em !important;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.5em;
        color: #9aa0a6;
        font-weight: 300;
        margin-top: -10px;
        margin-bottom: 40px;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI BAĞLANTISI ---
def get_model():
    try:
        genai.configure(api_key=API_KEY)
        return genai.GenerativeModel(MODEL_ADI)
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

model = get_model()

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- YARDIMCI FONKSİYON: GÜVENLİ CEVAP ÜRETME ---
def stream_cevap_yazdir(prompt_input):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_input)

    # Asistan cevabı (Streaming)
    if model:
        with st.chat_message("assistant", avatar="✨"):
            placeholder = st.empty()
            full_response = ""
            try:
                response_stream = model.generate_content(prompt_input, stream=True)
                
                # --- DÜZELTİLEN KISIM BAŞLANGIÇ ---
                for chunk in response_stream:
                    # Gelen parçada metin var mı diye kontrol et (Hata önleyici)
                    if chunk.parts:
                        text_parcasi = chunk.text
                        full_response += text_parcasi
                        placeholder.markdown(full_response + "▌")
                # --- DÜZELTİLEN KISIM BİTİŞ ---
                
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                # Eğer anlık bir hata olursa bile ekrana çökme mesajı basma,
                # ne kadar yazdıysa onu göster.
                if full_response:
                    placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error(f"Bir hata oluştu: {e}")

# ==========================================
#              ARAYÜZ MANTIĞI
# ==========================================

# DURUM 1: HİÇ MESAJ YOKSA (GİRİŞ EKRANI)
if len(st.session_state.messages) == 0:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="big-title">PALAİ</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Orhan Pala | Yapay Zeka Asistanı</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        def baslangic_submit():
            input_val = st.session_state.baslangic_input
            if input_val:
                # Not: Burada rerun yapmadan önce session state'e ekleyip döngüye girmesini sağlıyoruz
                # Ancak fonksiyon içinde rerun çağırmak yerine, input'u alıp aşağıya paslayacağız.
                # Streamlit yapısı gereği en temiz yöntem, burada mesajı ekleyip sayfayı yenilemektir.
                st.session_state.temp_input = input_val

        st.text_input(
            "Ara", 
            placeholder="PALAİ'ye bir şeyler sor...", 
            key="baslangic_input", 
            label_visibility="collapsed",
            on_change=baslangic_submit
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Eğer yukarıdaki input'tan değer geldiyse işlemi başlat
        if "temp_input" in st.session_state and st.session_state.temp_input:
            temp_text = st.session_state.temp_input
            del st.session_state.temp_input # Temizle
            stream_cevap_yazdir(temp_text)
            st.rerun()

        # Örnek öneriler butonları
        c1, c2, c3 = st.columns(3)
        if c1.button("🔒 Güvenlik", use_container_width=True):
            stream_cevap_yazdir("Siber güvenlik nedir?")
            st.rerun()
        if c2.button("🐍 Python", use_container_width=True):
            stream_cevap_yazdir("Basit bir Python kodu yaz.")
            st.rerun()
        if c3.button("✨ Fikir", use_container_width=True):
            stream_cevap_yazdir("Proje fikri ver.")
            st.rerun()

# DURUM 2: SOHBET MODU
else:
    with st.sidebar:
        if st.button("➕ Yeni Sohbet", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    st.markdown("### PALAİ 🤖")
    
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "👤" if role == "user" else "✨"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Sohbete devam et..."):
        stream_cevap_yazdir(prompt)