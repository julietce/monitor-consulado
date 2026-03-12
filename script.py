import httpx
import hashlib
import os

# Configuración desde variables secretas de GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://www.exteriores.gob.es/Consulados/buenosaires/es/Comunicacion/Noticias/Paginas/Articulos/202200907_NOT02.aspx"

def check_site():
    headers = {"User-Agent": "Mozilla/5.0"}
    # Usamos httpx < 0.28.0 como prefieres
    with httpx.Client(timeout=20.0) as client:
        response = client.get(URL)
        if response.status_code == 200:
            content = response.text
            # Creamos una huella digital del contenido
            current_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Comparamos con el último hash guardado
            if os.path.exists("last_hash.txt"):
                with open("last_hash.txt", "r") as f:
                    old_hash = f.read()
            else:
                old_hash = ""

            if current_hash != old_hash:
                # Si cambió, guardamos el nuevo y avisamos
                with open("last_hash.txt", "w") as f:
                    f.write(current_hash)
                send_msg("🚨 ¡Cambio detectado en la página del Consulado! Revisar turnos aquí: " + URL)
                return True
    return False

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    httpx.post(url, json={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    check_site()
