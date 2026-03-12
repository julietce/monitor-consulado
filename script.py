import httpx
import hashlib
import os

# Configuración desde variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://www.exteriores.gob.es/Consulados/buenosaires/es/Comunicacion/Noticias/Paginas/Articulos/202200907_NOT02.aspx"

def send_msg(text):
    # Usamos una petición simple compatible con todas las versiones
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    with httpx.Client() as client:
        client.post(telegram_url, json={"chat_id": CHAT_ID, "text": text})

def check_site():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    
    # Quitamos el parámetro http2=True que es el que suele dar error en versiones nuevas
    try:
        with httpx.Client(headers=headers, timeout=20.0) as client:
            response = client.get(URL)
            if response.status_code == 200:
                current_content = response.text
                current_hash = hashlib.sha256(current_content.encode()).hexdigest()
                
                # Leer hash anterior
                old_hash = ""
                if os.path.exists("last_hash.txt"):
                    with open("last_hash.txt", "r") as f:
                        old_hash = f.read().strip()
                
                # Comparar
                if True:  # current_hash != old_hash:
                    with open("last_hash.txt", "w") as f:
                        f.write(current_hash)
                    
                    send_msg(f"🚨 ¡Cambio detectado en el Consulado!\nVerifica aquí: {URL}")
                    return True
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    check_site()
