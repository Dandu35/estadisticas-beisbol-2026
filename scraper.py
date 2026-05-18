import requests
from bs4 import BeautifulSoup
import re
import json
import time

def obtener_datos_liga():
    base_url = "https://stats.fenabs.es/2026/b_division1/stats/{:02d}.htm"
    partido_num = 1
    jugadores_stats = {}

    # Expresión regular para detectar las líneas de bateo de los jugadores
    patron_bateo = re.compile(r"^([A-Z\s]+[a-z]*\s[A-Z][a-z]?)\s+(dh|p|c|1b|2b|3b|ss|lf|cf|rf|ph|pr|rf/cf|ss/p|2b/p|3b/ss|p/pr|p/2b|2b/3b|3b/ss|cf/2b|ss/3b|rf/cf)\s+([\d\s]+)$")

    print("Iniciando la extracción de datos desde la web de la federación...")

    while True:
        url = base_url.format(partido_num)
        response = requests.get(url)
        
        # Si la web responde 404 significa que ese partido aún no se ha jugado o no está subido
        if response.status_code == 404:
            print(f"Final de la lista alcanzado. No hay partido número {partido_num}.")
            break
            
        if response.status_code == 200:
            print(f"Procesando Partido {partido_num}: {url}")
            response.encoding = 'utf-8' # Evita problemas con eñes y acentos
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_tag = soup.find('pre')
            
            if pre_tag:
                lineas = pre_tag.get_text().split("\n")
                for linea in lineas:
                    match = patron_bateo.match(linea.strip())
                    if match:
                        nombre = match.group(1).strip()
                        if nombre == "Totals": 
                            continue
                        
                        stats_num = match.group(3).split()
                        if len(stats_num) >= 14:
                            # Extraemos los datos según el orden de las columnas de la federación
                            ab  = int(stats_num[0])
                            r   = int(stats_num[1])
                            h   = int(stats_num[2])
                            rbi = int(stats_num[3])
                            bb  = int(stats_num[7])
                            so  = int(stats_num[13])

                            # Si el jugador aparece por primera vez, lo registramos
                            if nombre not in jugadores_stats:
                                jugadores_stats[nombre] = {"ab": 0, "r": 0, "h": 0, "rbi": 0, "bb": 0, "so": 0, "partidos": 0}
                            
                            # Acumulamos los totales del jugador
                            jugadores_stats[nombre]["ab"] += ab
                            jugadores_stats[nombre]["r"] += r
                            jugadores_stats[nombre]["h"] += h
                            jugadores_stats[nombre]["rbi"] += rbi
                            jugadores_stats[nombre]["bb"] += bb
                            jugadores_stats[nombre]["so"] += so
                            jugadores_stats[nombre]["partidos"] += 1

        # Espera un instante para respetar el servidor de la federación
        time.sleep(0.2)
        partido_num += 1

    # Guardamos el archivo final machacando el json de prueba que pusimos antes
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(jugadores_stats, f, ensure_ascii=False, indent=4)
    print("¡Archivo datos.json actualizado con éxito!")

if __name__ == "__main__":
    obtener_datos_liga()
