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
        with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
            response = client.get(URL)
            
            if response.status_code == 200:
                content = response.text
                
                # BUSCADOR: Encuentra todos los patrones NW-XXXX-XXXXXXX
                matches = re.findall(r"NW-\d{4}-\d+", content)
                
                # Necesitamos al menos dos para tener el "Desde" y el "Hasta"
                if len(matches) >= 2:
                    current_desde = matches[0]
                    current_hasta = matches[1] 
                    print(f"Rango detectado: {current_desde} - {current_hasta}")
                    
                    # Seguimos usando el 'Hasta' como memoria para detectar cambios
                    old_idu = ""
                    if os.path.exists("last_hash.txt"):
                        with open("last_hash.txt", "r") as f:
                            old_idu = f.read().strip()
                    
                    # Si el límite 'Hasta' cambió, informamos el rango completo
                    if current_hasta != old_idu:
                        with open("last_hash.txt", "w") as f:
                            f.write(current_hasta)
                        
                        # Mensaje con el rango completo solicitado
                        mensaje = (
                            f"🚨 <b>¡Nuevos IDUs habilitados!</b>\n\n"
                            f"📅 <b>Rango:</b>\n"
                            f"Desde: <code>{current_desde}</code>\n"
                            f"Hasta: <code>{current_hasta}</code>\n\n"
                            f"🔗 <a href='{URL}'>Acceder a la web oficial</a>"
                        )
                        
                        send_msg(mensaje)
                        print(f"Notificación enviada: {current_desde} al {current_hasta}")
                        return True
                    else:
                        print(f"Sin cambios en el rango (Sigue en {current_hasta}).")
                else:
                    print(f"Se encontraron solo {len(matches)} expedientes. No se puede armar el rango.")
            else:
                print(f"Error de acceso: Código {response.status_code}")
                
    except Exception as e:
        print(f"Error en el monitoreo: {e}")
    return False

if __name__ == "__main__":
    check_site()
