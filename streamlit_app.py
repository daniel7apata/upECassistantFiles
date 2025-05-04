import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_resource
def get_drive_service():
    creds = Credentials(
        token=None,
        refresh_token=st.secrets["google_drive"]["refresh_token"],
        token_uri=st.secrets["google_drive"]["token_uri"],
        client_id=st.secrets["google_drive"]["client_id"],
        client_secret=st.secrets["google_drive"]["client_secret"],
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service

st.title("Leer archivos de Google Drive (Producción)")

if st.button("Conectar"):
    service = get_drive_service()
    results = service.files().list(pageSize=10, fields="files(name, id)").execute()
    files = results.get('files', [])
    for f in files:
        st.write(f"{f['name']} ({f['id']})")
