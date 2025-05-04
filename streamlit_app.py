import streamlit as st
import os
import io
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_resource
def get_drive_service():
    creds = None

    # Usa el token si ya existe (para no autenticar cada vez)
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)

    # Si no hay token, haz autenticación
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

st.title("Lector de Archivos de Google Drive")

if st.button("Conectar y listar archivos"):
    service = get_drive_service()
    results = service.files().list(
        pageSize=10, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        st.write("No hay archivos.")
    else:
        st.write("Archivos encontrados:")
        for item in items:
            st.write(f"{item['name']} ({item['id']})")

        # Ejemplo: descargar el primero
        file_id = items[0]['id']
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)
        st.write("Contenido del archivo descargado:")
        st.text(fh.read().decode('utf-8'))
