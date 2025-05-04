from google_auth_oauthlib.flow import InstalledAppFlow
import streamlit as st
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_resource
def get_drive_service():
    # Crear diccionario similar a credentials.json
    creds_dict = {
        "installed": {
            "client_id": st.secrets["google_drive"]["client_id"],
            "client_secret": st.secrets["google_drive"]["client_secret"],
            "auth_uri": st.secrets["google_drive"]["auth_uri"],
            "token_uri": st.secrets["google_drive"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_drive"]["auth_provider_x509_cert_url"],
            "redirect_uris": [st.secrets["google_drive"]["redirect_uri"]],
            "project_id": st.secrets["google_drive"]["project_id"]
        }
    }

    # Guardar temporalmente como JSON
    with open("temp_credentials.json", "w") as f:
        json.dump(creds_dict, f)

    flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    service = build("drive", "v3", credentials=creds)
    return service

st.title("Leer archivos de Google Drive")

if st.button("Conectar"):
    service = get_drive_service()
    results = service.files().list(pageSize=10, fields="files(name, id)").execute()
    files = results.get('files', [])
    for f in files:
        st.write(f"{f['name']} ({f['id']})")
