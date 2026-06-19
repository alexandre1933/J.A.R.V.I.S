import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="J.A.R.V.I.S", page_icon="🤖", layout="centered")

st.title("🦾 J.A.R.V.I.S")
st.caption("IA Futurista com Voz em Português")

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Controles
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    prompt = st.chat_input("Digite ou fale...")

with col2:
    if st.button("🎤 Falar", use_container_width=True):
        st.info("🔴 Ouvindo...")

with col3:
    if st.button("🔊 Jarvis Falar", use_container_width=True):
        if st.session_state.historico and st.session_state.historico[-1]["role"] == "assistant":
            ultima = st.session_state.historico[-1]["content"]
            st.markdown(f"""
                <script>
                    const utterance = new SpeechSynthesisUtterance("{ultima.replace('"', '').replace("'", "")}");
                    utterance.lang = 'pt-BR';
                    utterance.pitch = 0.85;     // Tom mais grave (estilo Jarvis)
                    utterance.rate = 1.05;      // Velocidade elegante
                    utterance.volume = 0.95;
                    speechSynthesis.speak(utterance);
                </script>
            """, unsafe_allow_html=True)

if prompt:
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S processando..."):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [
                    {"role": "system", "content": "Você é J.A.R.V.I.S, a IA do Tony Stark. Responda sempre em português do Brasil, de forma sarcástica, educada e inteligente."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.historico]

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.75,
                    max_tokens=900
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                
                # Voz Jarvis em Português
                st.markdown(f"""
                    <script>
                        const speakJarvis = new SpeechSynthesisUtterance(`{resposta.replace('"', '').replace("'", "")}`);
                        speakJarvis.lang = 'pt-BR';
                        speakJarvis.pitch = 0.85;
                        speakJarvis.rate = 1.05;
                        speechSynthesis.speak(speakJarvis);
                    </script>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("Erro ao conectar...")
                resposta = "Desculpe senhor, tive um pequeno problema técnico."

    st.session_state.historico.append({"role": "assistant", "content": resposta})
