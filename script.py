import httpx
import hashlib
import os

# Configuración desde variables de entorno de GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://www.exteriores.gob.es/Consulados/buenosaires/es/Comunicacion/Noticias/Paginas/Articulos/202200907_NOT02.aspx"

def send_msg():
    # Volvemos al formato HTML que es el más robusto para links largos
    texto_html = f'🚨 <b>¡Habilitados nuevos IDUs en el Consulado!</b>\n\n<a href="{URL}">Clic aquí para acceder</a>'
    
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": texto_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        with httpx.Client() as client:
            client.post(telegram_url, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def check_site():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client(headers=headers, timeout=20.0) as client:
            response = client.get(URL)
            if response.status_code == 200:
                current_content = response.text
                current_hash = hashlib.sha256(current_content.encode()).hexdigest()
                
                # Leer memoria del último cambio
                old_hash = ""
                if os.path.exists("last_hash.txt"):
                    with open("last_hash.txt", "r") as f:
                        old_hash = f.read().strip()
                
                # COMPARACIÓN REAL (Solo avisa si hay cambios)
                if current_hash != old_hash:
                    with open("last_hash.txt", "w") as f:
                        f.write(current_hash)
                    
                    send_msg()
                    print("Cambio detectado y mensaje enviado.")
                    return True
                else:
                    print("Sin cambios en la página.")
            else:
                print(f"Error de acceso: Código {response.status_code}")
    except Exception as e:
        print(f"Error en el monitoreo: {e}")
    return False

if __name__ == "__main__":
    check_site()
