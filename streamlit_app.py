import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_resource
def get_drive_service():
    creds_dict = {
        "token": st.secrets["google_drive"]["access_token"],  # Si solo tienes access_token
        "client_id": st.secrets["google_drive"]["client_id"],
        "client_secret": st.secrets["google_drive"]["client_secret"],
        "scopes": SCOPES,
    }

    creds = Credentials.from_authorized_user_info(info=creds_dict, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def list_drive_files(service):
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files

# Uso en la app
st.title("Conexión a Google Drive con Streamlit Secrets")

try:
    drive_service = get_drive_service()
    files = list_drive_files(drive_service)
    for file in files:
        st.write(f"{file['name']} (ID: {file['id']})")
except Exception as e:
    st.error(f"Error al conectar con Google Drive: {e}")
