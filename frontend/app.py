import streamlit as st
import requests
import time

st.set_page_config(page_title="DataBot", layout="wide")
st.title("📊🧠 Smart Query Chatbot")

# Backend URL - change this to your Render backend URL
BACKEND_URL = "http://localhost:8000"  # For local development
# BACKEND_URL = "https://your-app-name.onrender.com"  # For production

# Check backend connection
def check_backend_connection():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Display connection status
if not check_backend_connection():
    st.error("⚠️ Backend server is not running. Please start the backend server first.")
    st.info("Run: `python run_backend.py` in the project directory")
    st.stop()
else:
    st.success("✅ Connected to backend server")

query = st.chat_input("Ask your question...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if query:
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Processing..."):
        try:
            res = requests.post(f"{BACKEND_URL}/query", params={"query": query})
            
            # Check for HTTP errors
            if res.status_code == 403:
                error_msg = "❌ Access Forbidden (403): Check API keys or rate limits"
                st.chat_message("assistant").write(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            elif res.status_code != 200:
                error_msg = f"❌ HTTP Error {res.status_code}: {res.text}"
                st.chat_message("assistant").write(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                response_data = res.json()
                reply = response_data.get("response", "No response.")
                st.chat_message("assistant").write(str(reply))
                st.session_state.messages.append({"role": "assistant", "content": str(reply)})
                
        except requests.exceptions.JSONDecodeError:
            error_msg = f"❌ JSON Decode Error: {res.text}"
            st.chat_message("assistant").write(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Request Error: {str(e)}"
            st.chat_message("assistant").write(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"❌ Unexpected Error: {str(e)}"
            st.chat_message("assistant").write(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Upload section
st.sidebar.header("Upload Data")
upload_file = st.sidebar.file_uploader("Upload CSV/Excel/PDF/DOCX/TXT", type=["csv", "xlsx", "xls", "pdf", "docx", "txt"])

if upload_file:
    file_extension = upload_file.name.split('.')[-1].lower()
    
    # Route based on file extension for better accuracy
    if file_extension in ["csv", "xlsx", "xls"]:
        endpoint = "upload-structured"
    elif file_extension in ["pdf", "docx", "txt"]:
        endpoint = "upload-unstructured"
    else:
        st.sidebar.error(f"❌ Unsupported file format: {file_extension}")
        st.sidebar.info("Supported formats: CSV, XLSX, XLS, PDF, DOCX, TXT")
        st.stop()

    with st.spinner("Uploading..."):
        files = {"file": (upload_file.name, upload_file, upload_file.type)}
        response = requests.post(f"{BACKEND_URL}/{endpoint}", files=files)
        
        try:
            # Check for HTTP errors first
            if response.status_code == 403:
                st.sidebar.error("❌ Access Forbidden (403): Check API keys or rate limits")
            elif response.status_code != 200:
                st.sidebar.error(f"❌ HTTP Error {response.status_code}: {response.text}")
            else:
                response_data = response.json()
                if "error" in response_data:
                    st.sidebar.error(response_data["error"])
                else:
                    st.sidebar.success(response_data.get("message", "File uploaded successfully"))
                    
        except requests.exceptions.JSONDecodeError:
            st.sidebar.error(f"❌ JSON Decode Error: {response.text}")
        except Exception as e:
            st.sidebar.error(f"❌ Upload Error: {str(e)}")
