import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="J.A.R.V.I.S", page_icon="🤖", layout="centered")

st.title("🦾 J.A.R.V.I.S")
st.caption("IA Futurista com Voz + Visão")

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

# ==================== INPUTS ====================
col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    prompt = st.chat_input("Digite sua mensagem...")

with col2:
    uploaded_file = st.file_uploader("📸 Foto", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

with col3:
    if st.button("🎤 Falar", use_container_width=True):
        st.info("🔴 Ouvindo... (em breve)")

# Botão de voz Jarvis
if st.button("🔊 Jarvis Falar", use_container_width=True):
    if st.session_state.historico and st.session_state.historico[-1]["role"] == "assistant":
        ultima = st.session_state.historico[-1]["content"]
        st.markdown(f"""
            <script>
                const u = new SpeechSynthesisUtterance("{ultima.replace('"', '').replace("'", "")}");
                u.lang = 'pt-BR';
                u.pitch = 0.85;
                u.rate = 1.05;
                speechSynthesis.speak(u);
            </script>
        """, unsafe_allow_html=True)

# ==================== PROCESSAR MENSAGEM ====================
if prompt or uploaded_file is not None:
    user_content = prompt if prompt else "Descreva esta imagem"

    # Salva mensagem do usuário
    user_msg = {"role": "user", "content": user_content}
    if uploaded_file:
        user_msg["image"] = uploaded_file

    st.session_state.historico.append(user_msg)

    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.markdown(user_content)

    # Resposta da IA
    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S analisando..."):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [{"role": "system", "content": "Você é J.A.R.V.I.S, IA do Tony Stark. Responda em português do Brasil, sarcástico e útil."}]

                for m in st.session_state.historico:
                    if m["role"] == "user" and m.get("image"):
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": m["content"]},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{m['image'].getvalue()}"}} # Simplificado
                            ]
                        })
                    else:
                        messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",   # Melhor modelo com visão
                    messages=messages,
                    temperature=0.75,
                    max_tokens=800
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)

                # Voz Jarvis automática
                st.markdown(f"""
                    <script>
                        const speak = new SpeechSynthesisUtterance(`{resposta.replace('"', '').replace("'", "")}`);
                        speak.lang = 'pt-BR';
                        speak.pitch = 0.85;
                        speak.rate = 1.05;
                        speechSynthesis.speak(speak);
                    </script>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Erro ou limite atingido. Tente novamente.")
                resposta = "Desculpe senhor, estou com sobrecarga agora."

    st.session_state.historico.append({"role": "assistant", "content": resposta})
