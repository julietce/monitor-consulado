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
        # follow_redirects=True para asegurar que llegamos a la página final
        with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
            response = client.get(URL)
            
            if response.status_code == 200:
                content = response.text
                
                # BUSCADOR: Encuentra todos los patrones NW-XXXX-XXXXXXX
                matches = re.findall(r"NW-\d{4}-\d+", content)
                
                # Seleccionamos el segundo encuentro (el "Hasta")
                if len(matches) >= 2:
                    current_hasta = matches[1] 
                    print(f"IDU 'Hasta' detectado: {current_hasta}")
                    
                    # Leer la memoria (el IDU anterior)
                    old_idu = ""
                    if os.path.exists("last_hash.txt"):
                        with open("last_hash.txt", "r") as f:
                            old_idu = f.read().strip()
                    
                    # COMPARACIÓN: Solo si el límite 'Hasta' cambió
                    if current_hasta != old_idu:
                        # Guardamos el nuevo valor en la memoria
                        with open("last_hash.txt", "w") as f:
                            f.write(current_hasta)
                        
                        # Mensaje personalizado
                        mensaje = (
                            f"🚨 <b>¡Habilitados nuevos IDUs en el Consulado!</b>\n\n"
                            f"📍 <b>Habilitado HASTA:</b> <code>{current_hasta}</code>\n\n"
                            f"<a href='{URL}'>Clic aquí para acceder a la web oficial</a>"
                        )
                        
                        send_msg(mensaje)
                        print(f"Cambio detectado: Notificado hasta {current_hasta}.")
                        return True
                    else:
                        print(f"Sin cambios. El límite {current_hasta} ya estaba registrado.")
                else:
                    print(f"Se encontraron {len(matches)} IDUs. Se necesitan al menos 2 para identificar el 'Hasta'.")
            else:
                print(f"Error de acceso: Código {response.status_code}")
                
    except Exception as e:
        print(f"Error en el monitoreo: {e}")
    return False

if __name__ == "__main__":
    check_site()
