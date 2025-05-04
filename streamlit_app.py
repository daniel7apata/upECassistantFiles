import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None

    # Verifica si ya existe un token guardado
    if os.path.exists("token.pkl"):
        creds = pickle.load(open("token.pkl", "rb"))

    # Si no hay token, se inicia el flujo OAuth
    if not creds or not creds.valid:
        client_config = {
            "installed": {
                "client_id": st.secrets["installed"]["client_id"],
                "project_id": st.secrets["installed"]["project_id"],
                "auth_uri": st.secrets["installed"]["auth_uri"],
                "token_uri": st.secrets["installed"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["installed"]["auth_provider_x509_cert_url"],
                "client_secret": st.secrets["installed"]["client_secret"],
                "redirect_uris": st.secrets["installed"]["redirect_uris"]
            }
        }

        redirect_uri = "https://blank-app-xol4ld7qw5.streamlit.app"
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[🔐 Haz clic aquí para autenticarte con Google]({auth_url})")

        code = st.text_input("🔑 Pega aquí el código que recibiste")
        if code:
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                with open("token.pkl", "wb") as token_file:
                    pickle.dump(creds, token_file)
                st.success("✅ Autenticación exitosa")
            except Exception as e:
                st.error(f"❌ Error al autenticar: {e}")

    return creds

def list_drive_files(creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=5, fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except Exception as e:
        st.error(f"❌ Error al listar archivos: {e}")
        return []

# Streamlit App
st.title("📁 Conexión a Google Drive")

creds = authenticate()

if creds and creds.valid:
    st.success("🔓 Estás autenticado con Google")
    files = list_drive_files(creds)
    if files:
        st.subheader("📂 Archivos en tu Google Drive:")
        for f in files:
            st.write(f"- {f['name']} (ID: {f['id']})")
    else:
        st.info("No se encontraron archivos en tu Drive")
else:
    st.warning("🔒 Autenticación pendiente o no válida")
