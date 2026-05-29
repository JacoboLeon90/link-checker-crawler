# 🔗 Async Link Checker & Crawler

[ES] Un rastreador web de alto rendimiento desarrollado en Python. Utiliza programación asíncrona para verificar enlaces en segundos, detectando enlaces rotos, redirecciones y errores de servidor.

[EN] A high-performance web crawler developed in Python. It utilizes asynchronous programming to verify links in seconds, detecting broken links, redirects, and server errors.

---

## 🇪🇸 Español

### ✨ Por qué este proyecto
A diferencia de otros scripts síncronos convencionales, este crawler utiliza asyncio y aiohttp, lo que permite realizar múltiples peticiones HTTP de forma ambiguas concurrentemente sin bloquear el hilo principal. Es una herramienta ideal para auditorías rápidas de SEO técnico y mantenimiento web.

### 🚀 Características
- Asincronía Real: Peticiones no bloqueantes para máxima velocidad de ejecución.
- Análisis por Niveles: Extrae y valida enlaces internos respetando la profundidad (depth) configurada.
- Seguridad Integrada (Anti-SSRF): Filtra automáticamente IPs privadas y hosts locales para evitar escaneos internos involuntarios.
- Interfaz Limpia en Consola: Reportes visuales organizados mediante la librería Rich.
- Exportación de Datos: Generación automática de reportes detallados en formato CSV.
- Control de Concurrencia: Uso de semáforos asíncronos para mitigar bloqueos o baneos por parte de los servidores remotos.

### 🛠️ Instalación

1. Clona el repositorio:
   git clone https://github.com/JacoboLeon90/link-checker-crawler.git
   cd link-checker-crawler

2. Configura el entorno virtual e instala las dependencias:
   python -m venv venv
   source venv/bin/activate  # En Windows usa: venv\Scripts\activate
   pip install -r requirements.txt

### 💻 Uso

   python main.py https://tuweb.com --depth 2 --export

**Parámetros:**
- url: URL inicial para comenzar el rastreo.
- --depth: Niveles de navegación (por defecto 1).
- --all: Muestra todos los enlaces en la tabla (por defecto solo muestra errores y redirecciones).
- --export: Genera un archivo report.csv con los resultados.

---

## 🇬🇧 English

### ✨ Why this project
Unlike conventional synchronous scripts, this crawler leverages asyncio and aiohttp, enabling concurrent HTTP requests without blocking the main execution thread. It is an ideal tool for quick technical SEO audits and website maintenance.

### 🚀 Features
- True Asynchrony: Non-blocking requests for maximum execution speed.
- Multi-level Analysis: Extracts and validates internal links according to the configured depth.
- Built-in Security (Anti-SSRF): Automatically filters private IPs and local hosts to prevent unintended internal scanning.
- Clean Console UI: Visual and organized reports powered by the Rich library.
- Data Export: Automatic generation of detailed reports in CSV format.
- Concurrency Control: Utilizes asynchronous semaphores to mitigate rate-limiting or IP bans from remote servers.

### 🛠️ Installation

1. Clone the repository:
   git clone https://github.com/JacoboLeon90/link-checker-crawler.git
   cd link-checker-crawler

2. Set up the virtual environment and install dependencies:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt

### 💻 Usage

   python main.py https://yourwebsite.com --depth 2 --export

**Parameters:**
- url: Starting URL to begin the crawl.
- --depth: Navigation levels (default is 1).
- --all: Displays all links in the terminal table (by default, it only shows errors and redirects).
- --export: Generates a report.csv file with the results.

---

## 🛡️ Notas de Desarrollo / Development Notes
- [ES] El sistema de filtrado ignora automáticamente redes sociales conocidas y archivos multimedia estáticos (.pdf, .png, .zip, etc.) para centrarse estrictamente en la estructura de navegación de la web.
- [EN] The filtering system automatically ignores known social networks and static media files (.pdf, .png, .zip, etc.) to focus strictly on the website's crawlable navigation structure.

## 📄 Licencia / License
MIT License
