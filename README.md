REPS Data Downloader Pro

### 📺 Demostración del Proceso

[![Demostración de la Automatización del REPS](https://lh3.googleusercontent.com/pw/AP1GczMzmQWvoAoMQm7F0MrZEUzEe_DVIS0sYyoctfv0g6NRwQco7OIp1cHKN5jnldgnFdNZw2RH1h3P0JJ0B6YKYcdBc8YH88qKrJkqcPc1Tkma6bBi5PFdnbVPX_QoPopKKa27X7mZp56SWx01nBDEwAdIcg=w593-h679-s-no-gm?authuser=0)](https://youtu.be/HoRUFzeIc0U)

Haga clic en la imagen para ver el script en acción.

📝 Descripción del Proyecto
Este proyecto es una herramienta de automatización robusta diseñada para la extracción masiva y sistemática de los listados oficiales de Prestadores de Servicios de Salud (PSS) habilitados a nivel nacional, directamente desde el portal del Registro Especial de Prestadores de Servicios de Salud (REPS) del Ministerio de Salud y Protección Social de Colombia.

El script utiliza Python y Selenium para navegar la compleja interfaz y obtener las bases de datos por departamento, ofreciendo una solución clave para el análisis de datos de salud pública.

✨ Características Destacadas
Tu script incluye las siguientes funcionalidades avanzadas que lo hacen más confiable y fácil de usar:

Gestión Automática del Driver: Gracias a webdriver-manager, el script detecta la versión de tu navegador Chrome y descarga/configura automáticamente el Chromedriver compatible. Esto elimina los errores comunes de compatibilidad y la necesidad de mantenimiento manual.

Descarga por Departamento: Permite la opción de descargar todos los departamentos o solo un listado específico a través de un menú interactivo en la consola.

Ruta de Descarga Personalizada: Configura el directorio de destino automáticamente para asegurar que los archivos se guarden en una ruta definida y persistente (configurable en el main).

Proceso Asistido: Simula la navegación de un usuario (ingresar, cerrar modal, ir a Registro Actual, hacer clic en SERVICIOS, buscar, y exportar a Excel).

Manejo de Tiempos y Logs: Utiliza WebDriverWait y logging para manejar los tiempos de carga, detectar errores y ofrecer un seguimiento claro del progreso del proceso.

Renombrado y Limpieza: El script se encarga de esperar a que la descarga se complete y luego renombra el archivo de manera clara con el nombre del departamento.

🛠️ Requisitos
Python 3.x

Google Chrome (navegador instalado)

⚙️ Instalación
Sigue estos pasos para poner en marcha el proyecto:

1. Clonar el Repositorio
Bash

git clone https://github.com/tu-usuario/reps-data-downloader-col.git
cd reps-data-downloader-col
2. Instalar Dependencias
Es crucial instalar las librerías necesarias, incluyendo selenium y webdriver-manager:

Bash

pip install -r requirements.txt
Nota: Debes crear un archivo requirements.txt con el siguiente contenido:

selenium
webdriver-manager
▶️ Uso
El script utiliza una interfaz de consola para elegir el modo de descarga.

1. Configuración de Ruta (Opcional)
Si deseas cambiar la carpeta donde se guardarán los archivos, edita la variable download_path dentro de la función main() en el script principal (main.py o el nombre que le hayas dado):

Python

# main.py
def main():
    downloader = MinSaludDownloader(
        # CAMBIA ESTA RUTA POR TU UBICACIÓN DESEADA:
        download_path=r"D:\Proyectos\Scripts Python\Cuida\Reps\D" 
    )
    # ...
2. Ejecutar el Script
Ejecuta el script principal desde tu terminal:

Bash

python tu_script_principal.py 
# (ej. python minsalud_downloader.py)
Al ejecutar, se presentará el menú:

=== AUTOMATIZACIÓN DE DESCARGAS MINSALUD ===
1. Descargar todos los departamentos
2. Descargar departamentos específicos
3. Salir

Seleccione una opción (1-3): 
📂 Estructura de la Descarga
Los archivos se guardarán en la ruta configurada en la variable download_path. El script gestiona el renombrado de los archivos para que sean fácilmente identificables.

<Tu_Ruta_Descarga>/
├── Amazonas.xlsx
├── Antioquia.xlsx
├── Bogota.xlsx
└── ... (Archivos renombrados por departamento)
⚠️ Advertencia y Limitaciones
La velocidad de descarga depende de la carga del servidor del Ministerio de Salud. Se han incluido pausas (time.sleep) para reducir la probabilidad de bloqueo por exceso de peticiones.

Cualquier cambio en la estructura del sitio web del REPS (ID de botones, URLs, clases CSS) puede requerir una actualización del código de web scraping.

🤝 Contribución
Si encuentras fallas o deseas optimizar el proceso (por ejemplo, implementando threading o asyncio para la concurrencia), ¡tus Pull Requests son bienvenidas!

Haz un Fork del repositorio.

Crea una nueva rama (git checkout -b feature/mejora-rendimiento).

Realiza tus cambios y haz Commit.

Abre un Pull Request.

⚖️ Licencia
Distribuido bajo la Licencia MIT. Consulta el archivo LICENSE para más información.
