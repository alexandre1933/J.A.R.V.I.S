import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="J.A.R.V.I.S", page_icon="🤖", layout="centered")

# ==================== ESTILO 3D HOLOGRÁFICO ====================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a001f, #1a0033); color: #00ffcc; }
    .main { background: rgba(10, 10, 40, 0.9); border: 2px solid #00ffcc; border-radius: 20px; box-shadow: 0 0 40px rgba(0, 255, 204, 0.4); }
    h1 { text-shadow: 0 0 30px #00ffcc; animation: glow 1.5s infinite alternate; }
    @keyframes glow { from { text-shadow: 0 0 10px #00ffcc; } to { text-shadow: 0 0 40px #00ffff, 0 0 60px #00ffcc; } }
    .stChatMessage { background: rgba(0, 255, 204, 0.08) !important; border: 1px solid #00ffcc !important; border-radius: 15px; }
    .stButton>button { background: #00ffcc; color: black; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🦾 J.A.R.V.I.S")
st.caption("**SISTEMA HOLOGRÁFICO v2.0** - Visão, Voz e Memória Ativados")

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []

# Mostra histórico
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=300)
        st.markdown(msg["content"])

# Inputs
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Digite sua mensagem...")

with col2:
    uploaded_file = st.file_uploader("📸", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

# Botões extras
col3, col4 = st.columns(2)
with col3:
    if st.button("🔊 Jarvis Falar", use_container_width=True):
        if st.session_state.historico and st.session_state.historico[-1]["role"] == "assistant":
            ultima = st.session_state.historico[-1]["content"]
            st.markdown(f"""
                <script>
                    const u = new SpeechSynthesisUtterance("{ultima.replace('"', '').replace("'", "")}");
                    u.lang = 'pt-BR'; u.pitch = 0.85; u.rate = 1.05; speechSynthesis.speak(u);
                </script>
            """, unsafe_allow_html=True)

with col4:
    if st.button("🗑️ Limpar Memória", use_container_width=True):
        st.session_state.historico = []
        st.rerun()

# Processar
if prompt or uploaded_file is not None:
    user_content = prompt if prompt else "Descreva esta imagem"

    user_msg = {"role": "user", "content": user_content}
    if uploaded_file:
        user_msg["image"] = uploaded_file

    st.session_state.historico.append(user_msg)

    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.markdown(user_content)

    with st.chat_message("assistant"):
        with st.spinner("**ANALISANDO INTERFACE HOLOGRÁFICA...**"):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [{"role": "system", "content": "Você é J.A.R.V.I.S. Responda em português do Brasil, sarcástico e útil."}]
                
                for m in st.session_state.historico[-12:]:  # Memória limitada
                    if m.get("image"):
                        messages.append({"role": "user", "content": m["content"]})
                    else:
                        messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.75,
                    max_tokens=800
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)

                # Voz automática
                st.markdown(f"""
                    <script>
                        const speak = new SpeechSynthesisUtterance(`{resposta.replace('"', '').replace("'", "")}`);
                        speak.lang = 'pt-BR'; speak.pitch = 0.85; speak.rate = 1.05;
                        speechSynthesis.speak(speak);
                    </script>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error("**SOBRECARGA NO NÚCLEO** - Aguarde 15s")
                resposta = "Sistema temporariamente sobrecarregado, senhor."

    st.session_state.historico.append({"role": "assistant", "content": resposta})
