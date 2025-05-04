import streamlit as st
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import pickle

# Obtén las credenciales desde las variables de entorno
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    if os.path.exists("token.pkl"):
        creds = pickle.load(open("token.pkl", "rb"))
    else:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET,
            scopes=SCOPES,
            redirect_uri="http://localhost:8501"
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.write(f"[Haz clic aquí para autenticarte]({auth_url})")

        code = st.text_input("Pega aquí el código de autorización")
        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
            pickle.dump(creds, open("token.pkl", "wb"))
    return creds

def list_drive_files(creds):
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

st.title("Conectar a Google Drive")

creds = authenticate()
if creds:
    files = list_drive_files(creds)
    for file in files:
        st.write(f"{file['name']} (ID: {file['id']})")
