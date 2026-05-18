import requests
from bs4 import BeautifulSoup
import re
import json
import time

def obtener_datos_liga():
    base_url = "https://stats.fenabs.es/2026/b_division1/stats/{:02d}.htm"
    partido_num = 1
    jugadores_stats = {}

    print("Iniciando la extracción flexible de datos desde la web de la federación...")

    while True:
        url = base_url.format(partido_num)
        response = requests.get(url)
        
        # Fin de los partidos disponibles
        if response.status_code == 404:
            print(f"Final de la lista alcanzado. No hay partido número {partido_num}.")
            break
            
        if response.status_code == 200:
            print(f"Procesando Partido {partido_num}: {url}")
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_tag = soup.find('pre')
            
            if pre_tag:
                lineas = pre_tag.get_text().split("\n")
                for linea in lineas:
                    linea_limpia = linea.strip()
                    
                    # Saltar líneas vacías o totales
                    if not linea_limpia or "Totals" in linea_limpia or "Opponents" in linea_limpia:
                        continue
                    
                    # Nueva estrategia ultra-flexible:
                    # Buscamos cualquier texto que empiece por letras (nombre) seguido de una posición (letras/barras) y luego números
                    match = re.match(r"^([A-Z\s,.'-]+[a-z]*\s[A-Z][a-z]?)\s+([a-zA-Z0-9/]+)\s+([\d\s]+)$", linea_limpia)
                    
                    if match:
                        nombre = match.group(1).strip()
                        stats_num = match.group(3).split()
                        
                        # Nos aseguramos de que realmente sea una fila con estadísticas (mínimo 10 columnas de números)
                        if len(stats_num) >= 12:
                            try:
                                ab  = int(stats_num[0])
                                r   = int(stats_num[1])
                                h   = int(stats_num[2])
                                rbi = int(stats_num[3])
                                bb  = int(stats_num[7])
                                so  = int(stats_num[13]) if len(stats_num) > 13 else int(stats_num[-1])

                                # Inicializar jugador si es nuevo
                                if nombre not in jugadores_stats:
                                    jugadores_stats[nombre] = {"ab": 0, "r": 0, "h": 0, "rbi": 0, "bb": 0, "so": 0, "partidos": 0}
                                
                                # Sumar estadísticas
                                jugadores_stats[nombre]["ab"] += ab
                                jugadores_stats[nombre]["r"] += r
                                jugadores_stats[nombre]["h"] += h
                                jugadores_stats[nombre]["rbi"] += rbi
                                jugadores_stats[nombre]["bb"] += bb
                                jugadores_stats[nombre]["so"] += so
                                jugadores_stats[nombre]["partidos"] += 1
                            except ValueError:
                                # Si algún dato no es un número, ignoramos la línea de forma segura
                                continue

        # Breve pausa por cortesía al servidor
        time.sleep(0.2)
        partido_num += 1

    # Guardar el archivo final
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(jugadores_stats, f, ensure_ascii=False, indent=4)
    print(f"¡Proceso terminado! Se han guardado {len(jugadores_stats)} jugadores.")

if __name__ == "__main__":
    obtener_datos_liga()
