import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    if os.path.exists("token.pkl"):
        creds = pickle.load(open("token.pkl", "rb"))
    else:
        # Cargamos la configuración directamente desde st.secrets
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

        # Usa la primera URI como redirect
        redirect_uri = client_config["installed"]["redirect_uris"][0]
        flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)

        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Haz clic aquí para autenticarte con Google]({auth_url})")

        code = st.text_input("Pega aquí el código que recibiste")
        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
            with open("token.pkl", "wb") as token_file:
                pickle.dump(creds, token_file)

    return creds

@st.cache_resource
def get_drive_service():
    creds = authenticate()
    if creds and creds.valid:
        return build('drive', 'v3', credentials=creds)
    else:
        st.error("Credenciales no válidas. Autentícate nuevamente.")
        return None
