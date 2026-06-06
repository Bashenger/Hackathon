import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# 1. Load environment variables
load_dotenv()

# Ensure API Key is available
if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ_API_KEY in your environment/ .env file!")
    st.stop()

# 2. Configure the Streamlit Page Layout
st.set_page_config(page_title="Intelligent Multi-Mode Agent", layout="wide")
st.title("🤖 Intelligent Multi-Mode AI Agent")
st.caption("Powered by Groq & LangChain | Innovation Sprint 2026")

# 3. Initialize the Groq LLM Client
# Using 'llama3-8b-8192' for blazing fast token generation speeds
@st.cache_resource
def init_llm():
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0.7,
        streaming=True  # Enables token-by-token streaming UI
    )

llm = init_llm()

# 4. Initialize Streamlit Session State for Chat History (Short-Term Memory UI)
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Hello! I am your multi-mode assistant. Ask me anything!")
    ]

# 5. Sidebar Layout for Status and Metadata
with st.sidebar:
    st.header("System Status")
    st.success("Connected to Groq API")
    st.info("Current Mode: **Mode 1 - General Chat**")  # Will be made dynamic in Phase 3
    
    # Quick clear button to reset conversational session state
    if st.button("Clear Chat History"):
        st.session_state.messages = [AIMessage(content="Hello! I am your multi-mode assistant. Ask me anything!")]
        st.rerun()

# 6. Render Existing Chat History to UI
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# 7. Handle User Chat Input
if user_query := st.chat_input("Ask a general knowledge question..."):
    
    # Display human message immediately
    st.chat_message("user").write(user_query)
    st.session_state.messages.append(HumanMessage(content=user_query))
    
    # Generate Assistant response container for streaming output
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream chunks from Groq API via LangChain backend
        try:
            # For Phase 1, we pass the entire raw history directly to the LLM
            for chunk in llm.stream(st.session_state.messages):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            
            # Finalize response markdown without the cursor block
            response_placeholder.markdown(full_response)
            st.session_state.messages.append(AIMessage(content=full_response))
            
        except Exception as e:
            st.error(f"An error occurred while calling Groq API: {str(e)}")