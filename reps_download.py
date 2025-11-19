#!/usr/bin/env python3
"""
Script para automatizar la descarga de datos de prestadores de servicios de salud
por departamento desde el portal de MinSalud Colombia.
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinSaludDownloader:
    def __init__(self, download_path=r"D:\Proyectos\Scripts Python\Cuida\Reps\D"):
        """
        Inicializar el descargador de MinSalud
        
        Args:
            download_path (str): Ruta donde se guardarán las descargas
        """
        self.download_path = os.path.abspath(download_path)
        self.base_url = "https://prestadores.minsalud.gov.co/habilitacion/work.aspx?tOut=true"
        self.driver = None
        self.setup_download_directory()
        
    def verify_driver_path(self):
        """Verificar que el ChromeDriver existe en la ruta especificada"""
        if not os.path.exists(self.driver_path):
            raise FileNotFoundError(f"ChromeDriver no encontrado en: {self.driver_path}")
        logger.info(f"ChromeDriver encontrado en: {self.driver_path}")
    
    def setup_download_directory(self):
        """Crear directorio de descargas si no existe"""
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
            logger.info(f"Directorio de descargas creado: {self.download_path}")
    
    def setup_driver(self):
        """Configurar el driver de Chrome con opciones de descarga"""
        chrome_options = Options()
        
        # Configuraciones para descargas automáticas
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Opcional: ejecutar en modo headless (sin ventana del navegador)
        # chrome_options.add_argument("--headless")
        
        # Otras opciones útiles
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Usar webdriver_manager para descargar automáticamente el driver correcto
        logger.info("Descargando ChromeDriver compatible con tu versión de Chrome...")
        service = Service(ChromeDriverManager().install())
            
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()
        logger.info(f"Driver configurado automáticamente. Descargas en: {self.download_path}")
        
    def get_departamentos_list(self):
        """Obtener la lista completa de departamentos del select"""
        try:
            # Esperar a que el select esté disponible
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_ddsede_departamento"))
            )
            
            select = Select(select_element)
            departamentos = []
            
            for option in select.options:
                if option.get_attribute("value") and option.get_attribute("value").strip():
                    departamentos.append({
                        'codigo': option.get_attribute("value"),
                        'nombre': option.text.strip()
                    })
            
            logger.info(f"Se encontraron {len(departamentos)} departamentos")
            return departamentos
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de departamentos: {e}")
            return []
    
    def navigate_to_servicios_page(self):
        """Navegar a la página de servicios"""
        try:
            # Ir a la página principal
            logger.info("Navegando a la página principal...")
            self.driver.get(self.base_url)
            
            # Esperar a que cargue la página y cerrar modal si aparece
            time.sleep(2)
            try:
                cerrar_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-bs-dismiss="modal"]'))
                )
                cerrar_btn.click()
                logger.info("Modal cerrado")
                time.sleep(1)
            except TimeoutException:
                logger.info("No se encontró modal para cerrar, continuando...")
            
            # Hacer clic en "Ingresar"
            ingresar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[value="Ingresar"]'))
            )
            ingresar_btn.click()
            logger.info("Clic en 'Ingresar' realizado")
            
            # Hacer clic en "Registro Actual"
            registro_actual_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Registro Actual"))
            )
            registro_actual_link.click()
            logger.info("Clic en 'Registro Actual' realizado")
            
            # Cambiar a la nueva ventana/pestaña
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Hacer clic en "SERVICIOS"
            servicios_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_btn_servicios_reps"))
            )
            servicios_btn.click()
            logger.info("Clic en 'SERVICIOS' realizado")
            
            # Esperar a que cargue la página de servicios
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_ddsede_departamento"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error navegando a la página de servicios: {e}")
            return False
    
    def wait_for_download_and_rename(self, departamento_nombre, timeout=30):
        """
        Esperar a que se complete la descarga y renombrar el archivo
        
        Args:
            departamento_nombre (str): Nombre del departamento para renombrar el archivo
            timeout (int): Tiempo máximo de espera en segundos
        """
        try:
            # Obtener lista de archivos antes de la descarga
            archivos_antes = set(os.listdir(self.download_path)) if os.path.exists(self.download_path) else set()
            
            # Esperar a que aparezca un nuevo archivo
            start_time = time.time()
            nuevo_archivo = None
            
            while time.time() - start_time < timeout:
                if os.path.exists(self.download_path):
                    archivos_actuales = set(os.listdir(self.download_path))
                    archivos_nuevos = archivos_actuales - archivos_antes
                    
                    # Buscar archivos .xls o .xlsx nuevos que no sean temporales
                    for archivo in archivos_nuevos:
                        if (archivo.lower().endswith(('.xls', '.xlsx')) and 
                            not archivo.startswith('~') and 
                            not archivo.endswith('.crdownload')):
                            nuevo_archivo = archivo
                            break
                    
                    if nuevo_archivo:
                        break
                
                time.sleep(1)
            
            if nuevo_archivo:
                # Construir rutas completas
                ruta_original = os.path.join(self.download_path, nuevo_archivo)
                extension = os.path.splitext(nuevo_archivo)[1]
                nombre_nuevo = f"{departamento_nombre}{extension}"
                ruta_nueva = os.path.join(self.download_path, nombre_nuevo)
                
                # Renombrar el archivo
                try:
                    # Si ya existe un archivo con ese nombre, eliminarlo
                    if os.path.exists(ruta_nueva):
                        os.remove(ruta_nueva)
                        logger.info(f"Archivo existente eliminado: {nombre_nuevo}")
                    
                    os.rename(ruta_original, ruta_nueva)
                    logger.info(f"Archivo renombrado: {nuevo_archivo} → {nombre_nuevo}")
                    return True
                    
                except OSError as e:
                    logger.error(f"Error renombrando archivo: {e}")
                    return False
            else:
                logger.error(f"No se detectó descarga para {departamento_nombre}")
                return False
                
        except Exception as e:
            logger.error(f"Error esperando descarga para {departamento_nombre}: {e}")
            return False
        """
        Descargar datos de un departamento específico
        
        Args:
            departamento (dict): Diccionario con 'codigo' y 'nombre' del departamento
        """
        try:
            logger.info(f"Procesando departamento: {departamento['nombre']} (código: {departamento['codigo']})")
            
            # Seleccionar el departamento
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_ddsede_departamento"))
            )
            select = Select(select_element)
            select.select_by_value(departamento['codigo'])
            
            # Esperar un momento para que se procese la selección
            time.sleep(1)
            
            # Hacer clic en buscar
            buscar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_ctl0_ibBuscarHdr"))
            )
            buscar_btn.click()
            logger.info(f"Búsqueda iniciada para {departamento['nombre']}")
            
            # Esperar a que aparezcan los resultados en la tabla
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_dgServiciosSedes"))
            )
            
            # Esperar un poco más para asegurar que los datos se carguen completamente
            time.sleep(2)
            
            # Hacer clic en el botón de exportar a Excel
            excel_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_ibExcel"))
            )
            excel_btn.click()
            logger.info(f"Descarga iniciada para {departamento['nombre']}")
            
            # Esperar un momento para que se inicie la descarga
            time.sleep(3)
            
            # Verificar si se creó el archivo (opcional)
            expected_filename = f"{departamento['nombre']}.xls"
            expected_path = os.path.join(self.download_path, expected_filename)
            
            # Esperar un poco más para la descarga
            time.sleep(2)
            
            logger.info(f"Descarga completada para {departamento['nombre']}")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout procesando departamento {departamento['nombre']}")
            return False
        except Exception as e:
            logger.error(f"Error procesando departamento {departamento['nombre']}: {e}")
            return False
    
    def download_departamento_data(self, departamento):
        """
        Descargar datos de un departamento específico
        
        Args:
            departamento (dict): Diccionario con 'codigo' y 'nombre' del departamento
        """
        try:
            logger.info(f"Procesando departamento: {departamento['nombre']} (código: {departamento['codigo']})")
            
            # Seleccionar el departamento
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_ddsede_departamento"))
            )
            select = Select(select_element)
            select.select_by_value(departamento['codigo'])
            
            # Esperar un momento para que se procese la selección
            time.sleep(1)
            
            # Hacer clic en buscar
            buscar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_ctl0_ibBuscarHdr"))
            )
            buscar_btn.click()
            logger.info(f"Búsqueda iniciada para {departamento['nombre']}")
            
            # Esperar a que aparezcan los resultados en la tabla
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_dgServiciosSedes"))
            )
            
            # Esperar un poco más para asegurar que los datos se carguen completamente
            time.sleep(2)
            
            # Hacer clic en el botón de exportar a Excel
            excel_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_ibExcel"))
            )
            excel_btn.click()
            logger.info(f"Descarga iniciada para {departamento['nombre']}")
            
            # Esperar a que se complete la descarga y renombrar el archivo
            if self.wait_for_download_and_rename(departamento['nombre']):
                logger.info(f"Descarga completada y renombrada para {departamento['nombre']}")
                return True
            else:
                logger.error(f"Fallo en descarga o renombrado para {departamento['nombre']}")
                return False
            
        except TimeoutException:
            logger.error(f"Timeout procesando departamento {departamento['nombre']}")
            return False
        except Exception as e:
            logger.error(f"Error procesando departamento {departamento['nombre']}: {e}")
            return False

    def download_all_departamentos(self, max_concurrent=1):
        """
        Descargar datos de todos los departamentos
        
        Args:
            max_concurrent (int): Número máximo de descargas concurrentes (por ahora solo 1)
        """
        try:
            # Configurar driver
            self.setup_driver()
            
            # Navegar a la página de servicios
            if not self.navigate_to_servicios_page():
                logger.error("No se pudo navegar a la página de servicios")
                return
            
            # Obtener lista de departamentos
            departamentos = self.get_departamentos_list()
            if not departamentos:
                logger.error("No se pudieron obtener los departamentos")
                return
            
            logger.info(f"Iniciando descarga de {len(departamentos)} departamentos...")
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, departamento in enumerate(departamentos, 1):
                logger.info(f"Progreso: {i}/{len(departamentos)} - {departamento['nombre']}")
                
                if self.download_departamento_data(departamento):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                
                # Pausa entre descargas para no sobrecargar el servidor
                if i < len(departamentos):
                    logger.info("Esperando antes de la siguiente descarga...")
                    time.sleep(3)
            
            logger.info(f"Proceso completado. Exitosas: {successful_downloads}, Fallidas: {failed_downloads}")
            
        except Exception as e:
            logger.error(f"Error en el proceso principal: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def download_specific_departamentos(self, departamentos_nombres):
        """
        Descargar datos de departamentos específicos
        
        Args:
            departamentos_nombres (list): Lista de nombres de departamentos a descargar
        """
        try:
            # Configurar driver
            self.setup_driver()
            
            # Navegar a la página de servicios
            if not self.navigate_to_servicios_page():
                logger.error("No se pudo navegar a la página de servicios")
                return
            
            # Obtener lista completa de departamentos
            todos_departamentos = self.get_departamentos_list()
            if not todos_departamentos:
                logger.error("No se pudieron obtener los departamentos")
                return
            
            # Filtrar departamentos solicitados
            departamentos_a_descargar = [
                dept for dept in todos_departamentos 
                if dept['nombre'].lower() in [nombre.lower() for nombre in departamentos_nombres]
            ]
            
            if not departamentos_a_descargar:
                logger.error("No se encontraron departamentos que coincidan con los nombres proporcionados")
                return
            
            logger.info(f"Descargando {len(departamentos_a_descargar)} departamentos específicos...")
            
            for departamento in departamentos_a_descargar:
                self.download_departamento_data(departamento)
                time.sleep(3)  # Pausa entre descargas
                
        except Exception as e:
            logger.error(f"Error en descarga específica: {e}")
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Función principal del script"""
    
    # Crear instancia del descargador con ruta personalizada
    downloader = MinSaludDownloader(
        download_path=r"D:\Proyectos\Scripts Python\Cuida\Reps\D"
    )
    
    print("=== AUTOMATIZACIÓN DE DESCARGAS MINSALUD ===")
    print("1. Descargar todos los departamentos")
    print("2. Descargar departamentos específicos")
    print("3. Salir")
    
    opcion = input("\nSeleccione una opción (1-3): ").strip()
    
    if opcion == "1":
        print("\nIniciando descarga de todos los departamentos...")
        print(f"Los archivos se guardarán en: {downloader.download_path}")
        confirmacion = input("¿Continuar? (s/n): ").strip().lower()
        
        if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
            downloader.download_all_departamentos()
        else:
            print("Operación cancelada.")
            
    elif opcion == "2":
        print("\nIngrese los nombres de los departamentos separados por comas:")
        print("Ejemplo: Antioquia, Cundinamarca, Valle del Cauca")
        departamentos_input = input("Departamentos: ").strip()
        
        if departamentos_input:
            departamentos_lista = [dept.strip() for dept in departamentos_input.split(',')]
            print(f"\nDescargando departamentos: {', '.join(departamentos_lista)}")
            print(f"Los archivos se guardarán en: {downloader.download_path}")
            
            confirmacion = input("¿Continuar? (s/n): ").strip().lower()
            if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
                downloader.download_specific_departamentos(departamentos_lista)
            else:
                print("Operación cancelada.")
        else:
            print("No se ingresaron departamentos.")
            
    elif opcion == "3":
        print("Saliendo...")
    else:
        print("Opción no válida.")


if __name__ == "__main__":
    main()


# ===== EJEMPLO DE USO DIRECTO =====
def ejemplo_uso_directo():
    r"""
    Ejemplo de cómo usar la clase directamente en código
    """
    # Crear instancia
    downloader = MinSaludDownloader(download_path=r"D:\Proyectos\Scripts Python\Cuida\Reps\D")
    
    # Opción 1: Descargar todos los departamentos
    # downloader.download_all_departamentos()
    
    # Opción 2: Descargar departamentos específicos
    departamentos_deseados = ["Antioquia", "Cundinamarca", "Valle del Cauca"]
    downloader.download_specific_departamentos(departamentos_deseados)


# ===== VERSIÓN CON MÚLTIPLES VENTANAS (EXPERIMENTAL) =====
class MinSaludDownloaderMultiWindow(MinSaludDownloader):
    """
    Versión experimental que puede manejar múltiples ventanas simultáneamente
    """
    
    def download_concurrent_departamentos(self, departamentos_batch, max_windows=3):
        """
        Descargar múltiples departamentos usando múltiples ventanas
        
        Args:
            departamentos_batch (list): Lista de departamentos a descargar
            max_windows (int): Número máximo de ventanas a abrir simultáneamente
        """
        try:
            self.setup_driver()
            
            # Navegar a la página inicial
            if not self.navigate_to_servicios_page():
                return
            
            # Obtener lista completa de departamentos
            todos_departamentos = self.get_departamentos_list()
            departamentos_a_procesar = [
                dept for dept in todos_departamentos 
                if dept['nombre'] in departamentos_batch
            ]
            
            # Procesar en lotes
            for i in range(0, len(departamentos_a_procesar), max_windows):
                batch = departamentos_a_procesar[i:i+max_windows]
                logger.info(f"Procesando lote {i//max_windows + 1}: {[d['nombre'] for d in batch]}")
                
                # Abrir nueva ventana para cada departamento en el lote
                windows_handles = []
                for j, departamento in enumerate(batch):
                    if j > 0:  # Para ventanas adicionales
                        self.driver.execute_script("window.open('about:blank', '_blank');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        self.navigate_to_servicios_page()
                    
                    windows_handles.append(self.driver.current_window_handle)
                
                # Procesar cada ventana
                for window_handle, departamento in zip(windows_handles, batch):
                    self.driver.switch_to.window(window_handle)
                    self.download_departamento_data(departamento)
                
                # Cerrar ventanas adicionales
                for window_handle in windows_handles[1:]:
                    self.driver.switch_to.window(window_handle)
                    self.driver.close()
                
                # Volver a la ventana principal
                self.driver.switch_to.window(windows_handles[0])
                
                # Pausa entre lotes
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error en descarga concurrente: {e}")
        finally:
            if self.driver:
                self.driver.quit()


# ===== INSTRUCCIONES DE INSTALACIÓN =====
"""
INSTRUCCIONES SIMPLIFICADAS:

1. Instalar las dependencias necesarias:
   pip install selenium webdriver-manager

2. Ejecutar el script:
   python reps_download.py

¡ESO ES TODO!

CÓMO FUNCIONA:
- webdriver-manager detectará automáticamente tu versión de Chrome (139.0.7258.155)
- Descargará el ChromeDriver compatible correspondiente
- Lo guardará en caché para futuros usos
- Los archivos se descargarán en: D:\Proyectos\Scripts Python\Cuida\Reps\D

VENTAJAS:
- No necesitas mantener manualmente el ChromeDriver actualizado
- Siempre usará la versión correcta para tu Chrome
- Se actualiza automáticamente cuando Chrome se actualice
- Más simple y confiable

PRIMERA EJECUCIÓN:
- La primera vez descargará el driver (puede tomar unos segundos)
- Las siguientes ejecuciones serán más rápidas porque usa el driver en caché
"""