import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langchain_gigachat.chat_models import GigaChat
from act_generate import LLMAgent, generate_pdf_act  # <-- импортируй свой класс

st.set_page_config(page_title="Генератор Акта", layout="wide")

st.title("🧾 Генератор PDF-Акта на основе реквизитов")

if "agent" not in st.session_state:
    model = GigaChat(
        model="GigaChat-2-Max",
        verify_ssl_certs=False
    )
    st.session_state.agent = LLMAgent(model, tools=[generate_pdf_act])

agent: LLMAgent = st.session_state.agent

# Загрузка файла
uploaded_file = st.file_uploader("📄 Загрузите документ с реквизитами (docx)", type=["docx"])
if uploaded_file:
    file_id = agent.upload_file(uploaded_file)
    st.success("Файл загружен!")

# Ввод пользовательского сообщения
user_input = st.text_area("✍️ Напишите запрос (например: Сформируй акт)", height=150)

# Отправка запроса
if st.button("📨 Отправить"):
    if not uploaded_file:
        st.warning("Пожалуйста, загрузите файл с реквизитами.")
    elif not user_input.strip():
        st.warning("Введите сообщение.")
    else:
        with st.spinner("Генерация ответа..."):
            response = agent.invoke(content=user_input, attachments=[file_id])
            st.success("Ответ получен!")
            st.markdown("**Ответ:**")
            st.write(response)
