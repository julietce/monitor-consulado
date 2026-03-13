import re # Asegúrate de tener esta línea arriba del todo con los otros import

def check_site():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client(headers=headers, timeout=20.0) as client:
            response = client.get(URL)
            if response.status_code == 200:
                content = response.text
                
                # BUSCADOR: Busca el patrón NW- seguido de años y números
                # Esto detectará "NW-2024-...", "NW-2025-...", etc.
                match = re.search(r"NW-\d{4}-\d+", content)
                
                if match:
                    current_idu = match.group(0)
                    print(f"IDU detectado: {current_idu}")
                    
                    # Leer la memoria (el IDU anterior)
                    old_idu = ""
                    if os.path.exists("last_hash.txt"):
                        with open("last_hash.txt", "r") as f:
                            old_idu = f.read().strip()
                    
                    # COMPARACIÓN: Solo si el número de expediente es diferente
                    if current_idu != old_idu:
                        with open("last_hash.txt", "w") as f:
                            f.write(current_idu) # Guardamos el texto real, no el hash
                        
                        # Enviamos el mensaje avisando cuál es el nuevo rango
                        texto = f"🚨 <b>¡Nuevos IDUs habilitados!</b>\n\nActualizado hasta: <code>{current_idu}</code>\n\n<a href='{URL}'>Clic aquí para acceder</a>"
                        send_msg(texto)
                        return True
                    else:
                        print(f"El IDU {current_idu} ya fue notificado.")
                else:
                    print("No se encontró el patrón NW-XXXX-XXXX en la página.")
            else:
                print(f"Error de acceso: {response.status_code}")
    except Exception as e:
        print(f"Error en el monitoreo: {e}")
    return False
