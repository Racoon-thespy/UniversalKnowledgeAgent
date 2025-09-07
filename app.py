import streamlit as st
import os
from src.chatbot import UniversalChatbot

# Page configuration
st.set_page_config(
    page_title="Universal Document Intelligence Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Initialize chatbot
@st.cache_resource(show_spinner="Loading chatbot...")
def load_chatbot():
    return UniversalChatbot()

# Main App
def main():
    st.title("🤖 Universal Document Intelligence Chatbot")
    st.subheader("Upload documents and ask questions — I'll search both your docs and the web!")

    chatbot = load_chatbot()

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Sidebar - File Upload
    with st.sidebar:
        st.header("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.uploaded_files:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        success = chatbot.process_uploaded_file(uploaded_file)
                        if success:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                            st.success(f"✅ {uploaded_file.name} processed!")

        if st.session_state.uploaded_files:
            st.subheader("📚 Uploaded Files")
            for filename in st.session_state.uploaded_files:
                st.text(f"• {filename}")


    # Main Chat Interface
    st.header("💬 Chat")

    # Show conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📌 Sources"):
                    for source in message["sources"]:
                        st.text(f"• {source}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents or anything else..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.answer_query(prompt)

                st.markdown(response["answer"])

                # Route indicator
                route_emoji = {"document": "📄", "web": "🌐", "hybrid": "🔄"}
                st.caption(f"Route used: {route_emoji.get(response['route_used'], '❓')} {response['route_used']}")

                # Sources
                if response["sources"]:
                    with st.expander("📌 Sources"):
                        for source in response["sources"]:
                            st.text(f"• {source}")

                # Store assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response["sources"],
                })

# Run
if __name__ == "__main__":
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/vector_db", exist_ok=True)
    main()
