import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="J.A.R.V.I.S",
    page_icon="🤖",
    layout="centered"
)

st.title("🦾 J.A.R.V.I.S")
st.caption("IA Futurista com Groq - Rápida e poderosa!")

# Pega a chave
groq_key = os.getenv(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)

if not groq_key:
    st.error("⚠️ Crie um arquivo .env com sua chave do Groq!")
    st.info("Vá em https://console.groq.com/keys e crie uma chave gratuita.")
    st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S pensando em alta velocidade..."):
            try:
                client = Groq(api_key=groq_key)
                
                messages = [
                    {"role": "system", "content": "Você é J.A.R.V.I.S, a IA futurista, sarcástica, leal e extremamente útil do Tony Stark. Responda sempre em português do Brasil, de forma natural, divertida e direta."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.historico]

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",   # rápido e bom no free tier
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                
            except Exception as e:
                st.error("Limite do Groq atingido ou erro temporário. Aguarde uns segundos e tente novamente.")
                resposta = "Estou com um pouco de carga agora, senhor. Tenta de novo em 10 segundos!"

    st.session_state.historico.append({"role": "assistant", "content": resposta})
