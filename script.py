import httpx
import re
import os

# Configuración desde variables de entorno de GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://www.exteriores.gob.es/Consulados/buenosaires/es/Comunicacion/Noticias/Paginas/Articulos/202200907_NOT02.aspx"

def send_msg(texto_para_enviar):
    """Envía el mensaje formateado a Telegram"""
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": texto_para_enviar,
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
        # Usamos una versión compatible de httpx
        with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
            response = client.get(URL)
            
            if response.status_code == 200:
                content = response.text
                
                # BUSCADOR: Busca el patrón NW- seguido de años y números (ej: NW-2024-000123)
                # El patrón \d+ busca uno o más dígitos después del guion
                match = re.search(r"NW-\d{4}-\d+", content)
                
                if match:
                    current_idu = match.group(0)
                    print(f"IDU detectado actualmente: {current_idu}")
                    
                    # Leer la memoria (el IDU anterior guardado)
                    old_idu = ""
                    if os.path.exists("last_hash.txt"):
                        with open("last_hash.txt", "r") as f:
                            old_idu = f.read().strip()
                    
                    # COMPARACIÓN: Solo si el número de expediente es diferente al guardado
                    if current_idu != old_idu:
                        # Guardamos el nuevo número directamente (sin encriptar)
                        with open("last_hash.txt", "w") as f:
                            f.write(current_idu)
                        
                        # Armamos el mensaje profesional
                        mensaje = (
                            f"🚨 <b>¡Habilitados nuevos IDUs en el Consulado!</b>\n\n"
                            f"✅ Actualizado hasta: <code>{current_idu}</code>\n\n"
                            f"<a href='{URL}'>Clic aquí para acceder a la web oficial</a>"
                        )
                        
                        send_msg(mensaje)
                        print(f"Cambio detectado: de {old_idu} a {current_idu}. Mensaje enviado.")
                        return True
                    else:
                        print(f"Sin cambios. El IDU {current_idu} ya fue notificado.")
                else:
                    print("No se encontró ningún patrón de expediente NW-XXXX en la página.")
            else:
                print(f"Error de acceso a la web: Código {response.status_code}")
                
    except Exception as e:
        print(f"Error en el monitoreo: {e}")
    return False

if __name__ == "__main__":
    check_site()
