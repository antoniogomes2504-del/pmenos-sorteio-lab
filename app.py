import streamlit as st
import random
import time
import qrcode
import sqlite3
from io import BytesIO

# 1. Configuração do Banco de Dados (SQLite)
def init_db():
    conn = sqlite3.connect('sorteio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sorteios 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, numero INTEGER)''')
    conn.commit()
    conn.close()

def salvar_numero(n):
    conn = sqlite3.connect('sorteio.db')
    c = conn.cursor()
    c.execute("INSERT INTO sorteios (numero) VALUES (?)", (n,))
    conn.commit()
    conn.close()

def ler_numeros():
    conn = sqlite3.connect('sorteio.db')
    c = conn.cursor()
    c.execute("SELECT numero FROM sorteios ORDER BY id DESC")
    numeros = [row[0] for row in c.fetchall()]
    conn.close()
    return numeros

def limpar_banco():
    conn = sqlite3.connect('sorteio.db')
    c = conn.cursor()
    c.execute("DELETE FROM sorteios")
    conn.commit()
    conn.close()

# Inicializa o banco ao abrir o app
init_db()

# 2. Interface do Usuário
st.set_page_config(page_title="Sorteio Digital", layout="wide")

# Dados atuais
historico = ler_numeros()
ultimo_sorteado = historico[0] if historico else None

st.title("🎰 Painel de Sorteio")

# Barra Lateral (Controle do Dono do Sorteio)
with st.sidebar:
    st.header("Painel de Controle")
    senha = st.text_input("Senha para liberar sorteio", type="password")
    
    st.divider()
    min_val = st.number_input("Número Mínimo", value=1)
    max_val = st.number_input("Número Máximo", value=100)
    
    st.divider()
    st.subheader("Configurar QR CODE")
    link_atual = st.text_input("Cole o link do seu site aqui", "https://seu-site.streamlit.app")
    
    qr = qrcode.make(link_atual)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf, caption="QR Code para o público")

    if senha == "123": # <--- Mude sua senha aqui
        if st.button("LIMPAR TUDO / REINICIAR"):
            limpar_banco()
            st.rerun()

# Área Principal (O que o público vê)
col1, col2 = st.columns([2, 1])

with col1:
    # Botão de sortear só aparece com a senha certa
    if senha == "123": # <--- Mesma senha aqui
        if st.button('SORTEAR PRÓXIMO NÚMERO', type="primary", use_container_width=True):
            possiveis = [n for n in range(min_val, max_val + 1) if n not in historico]
            if possiveis:
                caixa_animacao = st.empty()
                for _ in range(10):
                    caixa_animacao.metric("Sorteando...", random.choice(possiveis))
                    time.sleep(0.1)
                
                escolhido = random.choice(possiveis)
                salvar_numero(escolhido)
                st.rerun()
            else:
                st.warning("Fim dos números!")
    else:
        st.info("Aguardando o organizador realizar o sorteio...")

    if ultimo_sorteado:
        st.markdown(f"""
            <div style="text-align: center; border: 10px solid #FF4B4B; border-radius: 20px; padding: 40px; background-color: white;">
                <h2 style="color: #555;">NÚMERO SORTEADO:</h2>
                <h1 style="font-size: 150px; color: #FF4B4B; margin: 0;">{ultimo_sorteado}</h1>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("📜 Números Anteriores")
    if historico:
        for n in historico:
            st.write(f"✅ Número {n}")