import re  # Agrega esta línea al principio del archivo con los otros import

def check_site():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client(headers=headers, timeout=20.0) as client:
            response = client.get(URL)
            if response.status_code == 200:
                content = response.text
                
                # BUSCADOR DE EXPEDIENTES:
                # Busca el formato NW-202 seguido de cualquier número o guion
                match = re.search(r"NW-202\d-\d+", content)
                
                if match:
                    current_idu_range = match.group(0) # Esto captura algo como "NW-2026-001234"
                    print(f"Rango detectado actual: {current_idu_range}")
                    
                    # Usamos el rango de IDUs como nuestra "huella digital"
                    current_hash = current_idu_range 
                    
                    old_hash = ""
                    if os.path.exists("last_hash.txt"):
                        with open("last_hash.txt", "r") as f:
                            old_hash = f.read().strip()
                    
                    # Solo avisa si el NUMERO DE EXPEDIENTE cambió
                    if current_hash != old_hash:
                        with open("last_hash.txt", "w") as f:
                            f.write(current_hash)
                        
                        # Personalizamos el mensaje con el nuevo rango detectado
                        mensaje = f"🚨 <b>¡Nuevos IDUs habilitados!</b>\n\nActualizado hasta: <code>{current_idu_range}</code>\n\n<a href='{URL}'>Clic aquí para acceder</a>"
                        send_msg(mensaje) # Asegúrate que tu función send_msg acepte un texto o usa la fija
                        return True
                else:
                    print("No se encontró ningún patrón de expediente NW-202X.")
            else:
                print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return False
    return False

if __name__ == "__main__":
    check_site()
