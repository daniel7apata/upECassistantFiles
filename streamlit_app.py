import streamlit as st
import requests
import base64

# Lectura segura del token desde Streamlit Secrets
GITHUB_TOKEN = st.secrets["github_token"]
REPO = "daniel7apata/upECassistantFiles"
BRANCH = "main"
CONTRASENIA_ACCESO = st.secrets["contrasenia_acceso"]


st.title("📤 Subir archivos para EC-Assistant")

# Cargar archivo
archivo = st.file_uploader("Selecciona un archivo para subir")

# Ruta en GitHub
ruta_en_repo = st.text_input("Ruta en el repositorio (ej: carpeta/archivo.txt)")

# Mensaje del commit
mensaje_commit = st.text_input("Mensaje del commit", value="Actualización de archivo")

contrasenia_acceso = st.text_input("Contraseña de subida")

if archivo and ruta_en_repo:
    if contrasenia_acceso == CONTRASENIA_ACCESO:
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
    else: 
        st.success("❌ Contraseña incorrecta")
