import requests
from bs4 import BeautifulSoup
import json
import time

def obtener_datos_liga():
    base_url = "https://stats.fenabs.es/2026/b_division1/stats/{:02d}.htm"
    partido_num = 1
    jugadores_stats = {}

    print("Iniciando la extracción robusta por columnas...")

    # Buscaremos hasta el partido 50 por seguridad debido a los saltos de ID de la federación
    while partido_num <= 50:
        url = base_url.format(partido_num)
        response = requests.get(url)
        
        # Si da 404, simplemente pasamos al siguiente número (por si hay huecos en el calendario)
        if response.status_code == 404:
            partido_num += 1
            continue
            
        if response.status_code == 200:
            print(f"Procesando Partido {partido_num}: {url}")
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_tag = soup.find('pre')
            
            if pre_tag:
                lineas = pre_tag.get_text().split("\n")
                bloque_bateo = False
                
                for linea in lineas:
                    linea_limpia = linea.strip()
                    
                    # Detectamos dónde empiezan las tablas de bateo
                    if "ab" in linea_limpia and "r" in linea_limpia and "h" in linea_limpia and "rbi" in linea_limpia:
                        bloque_bateo = True
                        continue
                    
                    # Detectamos dónde terminan (los totales del equipo)
                    if "Totals" in linea_limpia or "Opponents" in linea_limpia:
                        bloque_bateo = False
                        continue
                    
                    # Si estamos en la zona de bateadores, procesamos la línea
                    if bloque_bateo and linea_limpia:
                        # Dividimos la línea por cualquier cantidad de espacios en blanco
                        partes = linea_limpia.split()
                        
                        # Una línea válida debe tener el nombre, la posición y las columnas de números (mínimo 12 partes)
                        if len(partes) >= 10:
                            # Buscamos dónde empiezan los números para separar el nombre del jugador
                            numeros = [p for p in partes if p.isdigit()]
                            
                            if len(numeros) >= 6:
                                # El primer número siempre es 'ab' (Turnos)
                                idx_primero = partes.index(numeros[0])
                                
                                # Todo lo que esté antes de los números es el nombre (y su posición)
                                nombre_completo = " ".join(partes[:idx_primero-1])
                                
                                # Si el nombre quedó muy corto o es basura, lo saltamos
                                if len(nombre_completo) < 3 or "Umpires" in nombre_completo:
                                    continue
                                
                                try:
                                    ab  = int(numeros[0])
                                    r   = int(numeros[1])
                                    h   = int(numeros[2])
                                    rbi = int(numeros[3])
                                    
                                    # Los boletos (bb) y ponches (so) suelen estar más adelante, nos aseguramos con índices estables
                                    bb  = int(numeros[7]) if len(numeros) > 7 else 0
                                    so  = int(numeros[13]) if len(numeros) > 13 else (int(numeros[-1]) if len(numeros) >= 10 else 0)

                                    # Guardamos/Acumulamos datos
                                    if nombre_completo not in jugadores_stats:
                                        jugadores_stats[nombre_completo] = {"ab": 0, "r": 0, "h": 0, "rbi": 0, "bb": 0, "so": 0, "partidos": 0}
                                    
                                    jugadores_stats[nombre_completo]["ab"] += ab
                                    jugadores_stats[nombre_completo]["r"] += r
                                    jugadores_stats[nombre_completo]["h"] += h
                                    jugadores_stats[nombre_completo]["rbi"] += rbi
                                    jugadores_stats[nombre_completo]["bb"] += bb
                                    jugadores_stats[nombre_completo]["so"] += so
                                    jugadores_stats[nombre_completo]["partidos"] += 1
                                except (ValueError, IndexError):
                                    continue

        time.sleep(0.1)
        partido_num += 1

    # Guardar los resultados reales
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(jugadores_stats, f, ensure_ascii=False, indent=4)
    print(f"¡Proceso terminado! Se han guardado {len(jugadores_stats)} jugadores de toda la liga.")

if __name__ == "__main__":
    obtener_datos_liga()
