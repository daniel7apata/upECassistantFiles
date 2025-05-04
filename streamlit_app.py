import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import pickle
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None

    if os.path.exists("token.pkl"):
        creds = pickle.load(open("token.pkl", "rb"))

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

        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                with open("token.pkl", "wb") as token_file:
                    pickle.dump(creds, token_file)
                st.success("✅ Autenticación completada automáticamente")
            except Exception as e:
                st.error(f"❌ Error al autenticar: {e}")
        else:
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.markdown(f"[🔐 Haz clic aquí para autenticarte con Google]({auth_url})")

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


def download_file(file_id, service):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    fh.seek(0)
    return fh  # Devuelve un BytesIO listo para leer o cargar
    

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





if creds:
    service = build("drive", "v3", credentials=creds)

    file_id = "1UtK5l4WNK-4XG_iGckqC5Era3PDOJ80VL4KpjlVkt84"  # reemplaza con el ID real
    file_content = download_file(file_id, service)

    # Ejemplo: leer CSV si es un archivo de texto
    import pandas as pd
    df = pd.read_csv(file_content)
    st.write("📄 Contenido del archivo:")
    st.dataframe(df)
