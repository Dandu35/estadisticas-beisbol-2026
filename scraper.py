import requests
from bs4 import BeautifulSoup
import json
import time

def obtener_datos_liga():
    base_url = "https://stats.fenabs.es/2026/b_division1/stats/{:02d}.htm"
    jugadores_stats = {}

    print("=== INICIANDO EXTRACCIÓN POR FUERZA BRUTA ===")

    # Probamos solo con los 3 primeros partidos para diagnosticar rápido
    for partido_num in range(1, 4):
        url = base_url.format(partido_num)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Partido {partido_num} no disponible (Status: {response.status_code})")
                continue
                
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Si no encuentra <pre>, buscamos todo el texto de la página por si acaso
            texto_pagina = ""
            pre_tag = soup.find('pre')
            if pre_tag:
                texto_pagina = pre_tag.get_text()
                print(f"-> Partido {partido_num}: Encontrada etiqueta <pre> con {len(texto_pagina)} caracteres.")
            else:
                texto_pagina = soup.get_text()
                print(f"-> Partido {partido_num}: NO hay <pre>. Usando texto general de la página ({len(texto_pagina)} caracteres).")

            lineas = texto_pagina.split("\n")
            for linea in lineas:
                linea_limpia = linea.strip()
                partes = linea_limpia.split()
                
                # Buscamos filas que tengan bastantes números (característico de los jugadores)
                if len(partes) >= 8:
                    numeros = [p for p in partes if p.isdigit()]
                    # Si tiene más de 6 bloques de números, probablemente es un jugador
                    if len(numeros) >= 6:
                        # Averiguamos dónde empieza el primer número para sacar el nombre
                        idx_primero = partes.index(numeros[0])
                        nombre_propuesto = " ".join(partes[:idx_primero])
                        
                        # Limpieza rápida de nombres de equipos o totales
                        if "Totals" in nombre_propuesto or "Opponents" in nombre_propuesto or len(nombre_propuesto) < 3:
                            continue
                            
                        # Si pasa el filtro, lo guardamos con datos básicos
                        try:
                            ab = int(numeros[0])
                            h  = int(numeros[2]) if len(numeros) > 2 else 0
                            
                            # Para el diagnóstico, guardamos limpio el nombre de la posición si se coló
                            nombre_jugador = nombre_propuesto.split()[0] if len(nombre_propuesto.split()) > 0 else nombre_propuesto
                            
                            if nombre_jugador not in jugadores_stats:
                                jugadores_stats[nombre_jugador] = {"ab": 0, "r": 0, "h": 0, "rbi": 0, "bb": 0, "so": 0, "partidos": 0}
                            
                            jugadores_stats[nombre_jugador]["ab"] += ab
                            jugadores_stats[nombre_jugador]["h"] += h
                            jugadores_stats[nombre_jugador]["partidos"] += 1
                            print(f"   [OK] Capturado: {nombre_jugador} (AB: {ab})")
                        except Exception as e:
                            continue
        except Exception as e:
            print(f"Error crítico en partido {partido_num}: {e}")

    # Guardar resultados
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(jugadores_stats, f, ensure_ascii=False, indent=4)
    print(f"=== PROCESO TERMINADO. JUGADORES ENCONTRADOS: {len(jugadores_stats)} ===")

if __name__ == "__main__":
    obtener_datos_liga()
