import streamlit as st
import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_PATH = "token.pkl"

def authenticate():
    creds = None

    # Si ya hay token almacenado, lo usamos
    if os.path.exists(TOKEN_PATH):
        creds = pickle.load(open(TOKEN_PATH, "rb"))

    # Si no existe o ya no es válido, iniciamos el flujo
    if not creds or not creds.valid:
        # Configuración extraída de st.secrets (tu client_secrets.json)
        client_config = {
            "installed": {
                "client_id": st.secrets["installed"]["client_id"],
                "project_id": st.secrets["installed"]["project_id"],
                "auth_uri": st.secrets["installed"]["auth_uri"],
                "token_uri": st.secrets["installed"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["installed"]["auth_provider_x509_cert_url"],
                "client_secret": st.secrets["installed"]["client_secret"],
                "redirect_uris": st.secrets["installed"]["redirect_uris"],
            }
        }

        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES,
        )

        # Esto abre el navegador y levanta un pequeño servidor local para recibir el callback
        creds = flow.run_local_server(port=8501, prompt="consent")

        # Guardamos el token para la próxima ejecución
        with open(TOKEN_PATH, "wb") as token_file:
            pickle.dump(creds, token_file)

        st.success("✅ Autenticación completada y token guardado")

    return creds

def list_drive_files(creds, n=5):
    try:
        service = build('drive', 'v3', credentials=creds)
        res = service.files().list(pageSize=n, fields="files(id, name)").execute()
        return res.get("files", [])
    except Exception as e:
        st.error(f"Error al listar archivos: {e}")
        return []

# --- Streamlit App ---
st.title("📁 Conexión a Google Drive con Cliente de Escritorio")

creds = authenticate()

if creds and creds.valid:
    st.success("🔓 Estás autenticado correctamente con Google Drive")
    files = list_drive_files(creds)
    if files:
        st.subheader("📂 Tus archivos en Drive:")
        for f in files:
            st.write(f"- {f['name']} (ID: {f['id']})")
    else:
        st.info("Tu Drive está vacío o no hay archivos accesibles.")
else:
    st.warning("🔒 Aún no estás autenticado o tus credenciales no son válidas.")
