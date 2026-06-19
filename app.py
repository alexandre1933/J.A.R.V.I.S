import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="J.A.R.V.I.S", page_icon="🤖", layout="centered")

st.title("🦾 J.A.R.V.I.S")
st.caption("IA Futurista com Voz + Fotos (Versão Estável)")

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
        if msg["content"]:
            st.markdown(msg["content"])

# Inputs
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Digite sua mensagem...")

with col2:
    uploaded_file = st.file_uploader("📸", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if st.button("🔊 Jarvis Falar", use_container_width=True):
    if st.session_state.historico and st.session_state.historico[-1]["role"] == "assistant":
        ultima = st.session_state.historico[-1]["content"]
        st.markdown(f"""
            <script>
                const u = new SpeechSynthesisUtterance("{ultima.replace('"', '').replace("'", "")}");
                u.lang = 'pt-BR'; u.pitch = 0.85; u.rate = 1.05;
                speechSynthesis.speak(u);
            </script>
        """, unsafe_allow_html=True)

# Processar
if prompt or uploaded_file is not None:
    user_content = prompt if prompt else "Descreva esta imagem com detalhes"

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
        with st.spinner("J.A.R.V.I.S processando..."):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [
                    {"role": "system", "content": "Você é J.A.R.V.I.S, IA do Tony Stark. Responda em português do Brasil, sarcástico, útil e direto."}
                ]

                # Adiciona histórico (sem visão por enquanto pra evitar erro)
                for m in st.session_state.historico[:-1]:  # exclui a última pra não duplicar
                    messages.append({"role": m["role"], "content": m["content"]})

                # Adiciona a última mensagem
                if uploaded_file:
                    messages.append({"role": "user", "content": "Analise esta imagem: " + user_content})
                else:
                    messages.append({"role": "user", "content": user_content})

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",   # Modelo mais estável
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
                        speak.lang = 'pt-BR';
                        speak.pitch = 0.85;
                        speak.rate = 1.05;
                        speechSynthesis.speak(speak);
                    </script>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Limite atingido ou erro temporário. Aguarde 15 segundos e tente novamente.")
                resposta = "Senhor, estou com sobrecarga momentânea. Tente novamente em alguns segundos."

    st.session_state.historico.append({"role": "assistant", "content": resposta})
