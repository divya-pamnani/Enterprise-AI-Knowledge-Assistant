"""
app.py
Enterprise AI Knowledge Assistant
"""

import os
import streamlit as st

from rag_engine import RAGEngine
import config

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# LOAD CSS
# --------------------------------------------------

def load_css():

    if os.path.exists("style.css"):

        with open("style.css") as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

load_css()

# --------------------------------------------------
# INITIALIZE BOT
# --------------------------------------------------

@st.cache_resource
def load_bot():

    return RAGEngine()

bot = load_bot()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

if "kb_ready" not in st.session_state:

    st.session_state.kb_ready = False

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown(
    f"""
<div class="title">
🤖 {config.APP_NAME}
</div>

<div class="subtitle">
Enterprise Retrieval-Augmented Generation Assistant
</div>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("📂 Knowledge Base")

    uploaded_files = st.file_uploader(

        "Upload Documents",

        type=["pdf", "docx", "txt"],

        accept_multiple_files=True

    )

    if st.button(
        "🚀 Build Knowledge Base",
        use_container_width=True
    ):

        # Remove old files

        for file in config.UPLOAD_DIR.glob("*"):

            file.unlink()

        # Save uploaded files

        if uploaded_files:

            progress = st.progress(0)

            for i, uploaded in enumerate(uploaded_files):

                save_path = (
                    config.UPLOAD_DIR /
                    uploaded.name
                )

                with open(
                    save_path,
                    "wb"
                ) as f:

                    f.write(
                        uploaded.getbuffer()
                    )

                progress.progress(
                    (i + 1) / len(uploaded_files)
                )

            with st.spinner(
                "Building Knowledge Base..."
            ):

                stats = bot.ingest()

            st.session_state.kb_ready = True

            st.success(
                f"""
✅ Knowledge Base Created!

Documents : {stats['documents']}

Chunks : {stats['chunks']}
"""
            )

        else:

            st.warning(
                "Please upload at least one document."
            )

    st.divider()

    st.subheader("📊 Statistics")

    try:
        documents = len([f for f in config.UPLOAD_DIR.iterdir() if f.is_file()])
        chunks = bot.store.count()

        st.metric("📄 Documents", documents)
        st.metric("📚 Indexed Chunks", chunks)

    except Exception:
        st.metric("📄 Documents", 0)
        st.metric("📚 Indexed Chunks", 0)

    st.divider()

    if st.button(
        "🗑 Reset Knowledge Base",
        use_container_width=True
    ):

        bot.store.reset()

        for file in config.UPLOAD_DIR.glob("*"):

            file.unlink()

        st.session_state.messages = []

        st.session_state.kb_ready = False

        st.success(
            "Knowledge Base Reset."
        )

        st.rerun()

    if st.button(
        "🧹 Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()
        # --------------------------------------------------
# CHAT AREA
# --------------------------------------------------

st.divider()

# Welcome message

if len(st.session_state.messages) == 0:

    with st.chat_message("assistant"):

        st.markdown(
            """
👋 **Welcome!**

I'm your **Enterprise AI Knowledge Assistant**.

I can answer questions from your uploaded:

- 📄 PDF
- 📝 DOCX
- 📃 TXT

Upload your documents from the sidebar and click **Build Knowledge Base**.
"""
        )

# --------------------------------------------------
# Display Chat History
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if "sources" in message:

                with st.expander("📚 Sources"):

                    for source in message["sources"]:

                        st.write("•", source)

            if "confidence" in message:

                confidence = message["confidence"]

                if confidence >= 80:

                    color = "🟢"

                elif confidence >= 60:

                    color = "🟡"

                else:

                    color = "🔴"

                st.caption(
                    f"{color} Confidence: {confidence}%"
                )

            if "time" in message:

                st.caption(
                    f"⏱ Response Time: {message['time']} sec"
                )

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

question = st.chat_input(
    "Ask anything about your documents..."
)

# --------------------------------------------------
# Ask Question
# --------------------------------------------------

if question:

    if bot.store.count() == 0:

        st.warning(
            "Please build the Knowledge Base first."
        )

        st.stop()

    # Save user message

    st.session_state.messages.append(

        {

            "role": "user",

            "content": question

        }

    )

    with st.chat_message("user"):

        st.markdown(question)

    # Assistant Response

    with st.chat_message("assistant"):

        placeholder = st.empty()

        with st.spinner("Thinking..."):

            try:

                response = bot.ask(question)

            except Exception as e:

                st.error(e)

                st.stop()

        placeholder.markdown(
            response["answer"]
        )

        # Sources

        with st.expander("📚 Sources Used"):

            for source in response["sources"]:

                st.write("•", source)

        # Confidence

        confidence = response["confidence"]

        if confidence >= 80:

            st.success(
                f"Confidence : {confidence}%"
            )

        elif confidence >= 60:

            st.warning(
                f"Confidence : {confidence}%"
            )

        else:

            st.error(
                f"Confidence : {confidence}%"
            )

        # Response Time

        st.caption(
            f"⏱ Generated in {response['time']} sec"
        )

    # Save assistant message

    st.session_state.messages.append(

        {

            "role": "assistant",

            "content": response["answer"],

            "sources": response["sources"],

            "confidence": response["confidence"],

            "time": response["time"]

        }

    )

    st.rerun()
    # --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

try:
    documents = len([f for f in config.UPLOAD_DIR.iterdir() if f.is_file()])
    chunks = bot.store.count()
except Exception:
    documents = 0
    chunks = 0

with col1:
    st.metric("📄 Documents", documents)

with col2:
    st.metric("📚 Indexed Chunks", chunks)

with col3:
    st.metric(
        "💬 Chat Messages",
        len(st.session_state.messages)
    )

# --------------------------------------------------
# DOWNLOAD CHAT
# --------------------------------------------------

if st.session_state.messages:

    chat_text = ""

    for msg in st.session_state.messages:

        role = msg["role"].capitalize()

        content = msg["content"]

        chat_text += f"{role}\n"
        chat_text += "-" * 50 + "\n"
        chat_text += content + "\n\n"

    st.download_button(
        label="📥 Download Chat History",
        data=chat_text,
        file_name="chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

# --------------------------------------------------
# ABOUT PROJECT
# --------------------------------------------------

with st.expander("ℹ About This Project"):

    st.markdown(f"""
### 🤖 {config.APP_NAME}

This application is an **Enterprise Retrieval-Augmented Generation (RAG)** assistant.

### Features

- 📄 PDF Support
- 📝 DOCX Support
- 📃 TXT Support
- 🔍 Semantic Search
- 🧠 ChromaDB Vector Database
- 🤖 Ollama (Llama 3.2)
- 📚 Source Citation
- 📊 Confidence Score
- 💬 ChatGPT-style Interface

### Tech Stack

- Python
- Streamlit
- Ollama
- ChromaDB
- Sentence Transformers

Version: **{config.APP_VERSION}**
""")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
<div style='text-align:center;color:gray;padding:15px;'>

Made with ❤️ using

<b>Python • Streamlit • Ollama • ChromaDB • Sentence Transformers</b>

</div>
""",
    unsafe_allow_html=True
)