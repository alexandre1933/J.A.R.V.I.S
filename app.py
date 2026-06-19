import streamlit as st
import os
from groq import Groq
from datetime import datetime

st.set_page_config(
    page_title="J.A.R.V.I.S",
    page_icon="🤖",
    layout="centered"
)

st.title("🦾 J.A.R.V.I.S")
st.caption("IA Futurista com Visão - Agora aceita fotos!")

# Chave do Groq
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Chave do Groq não configurada!")
    st.info("Adicione GROQ_API_KEY nos Secrets do Streamlit (Gerenciar aplicativo → Secrets)")
    st.stop()

# Histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# Mostra histórico
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and "image" in msg:
            st.image(msg["image"], width=300)
            st.write(msg["content"])
        else:
            st.markdown(msg["content"])

# Input de texto + foto
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Digite sua mensagem...")

with col2:
    uploaded_file = st.file_uploader("📸", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if prompt or uploaded_file is not None:
    # Adiciona mensagem do usuário
    user_message = {"role": "user", "content": prompt or "Descreva esta imagem"}
    
    if uploaded_file is not None:
        user_message["image"] = uploaded_file
        st.session_state.historico.append(user_message)
        with st.chat_message("user"):
            st.image(uploaded_file, width=300)
            if prompt:
                st.write(prompt)
    else:
        st.session_state.historico.append(user_message)
        with st.chat_message("user"):
            st.write(prompt)

    # Resposta da IA
    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S analisando..."):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [
                    {"role": "system", "content": "Você é J.A.R.V.I.S, IA futurista sarcástica e útil. Responda em português do Brasil."}
                ]

                # Monta as mensagens com imagem se houver
                for msg in st.session_state.historico:
                    if msg["role"] == "user" and "image" in msg:
                        # Para visão no Groq
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": msg.get("content", "Descreva esta imagem")},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{msg['image'].getvalue()}"}}  # Simplificado
                            ]
                        })
                    else:
                        messages.append({"role": msg["role"], "content": msg["content"]})

                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",   # Modelo com visão
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                
            except Exception as e:
                st.error("Erro ao processar imagem ou limite atingido. Tente novamente.")
                resposta = "Desculpe, tive dificuldade pra analisar isso agora."

    st.session_state.historico.append({"role": "assistant", "content": resposta})
