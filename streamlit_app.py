import streamlit as st
import requests
import base64

# Lectura segura del token desde Streamlit Secrets
GITHUB_TOKEN = st.secrets["github_token"]
REPO = "usuario/nombre-del-repo"
BRANCH = "main"

st.title("📤 Subir o actualizar archivo en GitHub")

# Cargar archivo
archivo = st.file_uploader("Selecciona un archivo para subir a GitHub")

# Ruta en GitHub
ruta_en_repo = st.text_input("Ruta en el repositorio (ej: carpeta/archivo.txt)")

# Mensaje del commit
mensaje_commit = st.text_input("Mensaje del commit", value="Subida desde app Streamlit")

if archivo and ruta_en_repo:
    contenido = archivo.read()
    contenido_b64 = base64.b64encode(contenido).decode("utf-8")
    url = f"https://api.github.com/repos/{REPO}/contents/{ruta_en_repo}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Verificar si ya existe el archivo
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    data = {
        "message": mensaje_commit,
        "content": contenido_b64,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    # Subida del archivo
    subir = st.button("Subir a GitHub")
    if subir:
        response = requests.put(url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            st.success("✅ Archivo subido o actualizado correctamente.")
        else:
            st.error(f"❌ Error {response.status_code}")
            st.json(response.json())
