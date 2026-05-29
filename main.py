import asyncio
import csv
import argparse
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table

from checker import process_url_batch

console = Console()

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def get_clean_domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")

def is_same_domain(base_domain: str, target_url: str) -> bool:
    return base_domain == get_clean_domain(target_url)

async def crawl(start_url: str, max_depth: int = 1):
    base_domain = get_clean_domain(start_url)
    visited = set()
    to_visit = {start_url}
    final_results = {}

    for depth in range(max_depth + 1):
        current_queue = list(to_visit - visited)
        to_visit.clear()

        if not current_queue:
            break

        console.print(f"\n[bold cyan]Nivel {depth}[/bold cyan] → Analizando {len(current_queue)} URLs...")

        # Marcamos como visitadas antes del batch para evitar duplicados concurrentes
        visited.update(current_queue)
        
        # Ejecución 100% asíncrona
        batch_responses = await process_url_batch(current_queue)

        for url, status, msg, extracted_links in batch_responses:
            final_results[url] = (status, msg)

            # Si la página es accesible y pertenece al mismo dominio, añadimos sus hijos a la cola
            if status == 200 and is_same_domain(base_domain, url):
                for link in extracted_links:
                    if link not in visited:
                        to_visit.add(link)
                        
        # Pequeño respiro entre niveles para comportamiento más humano
        await asyncio.sleep(0.5)

    return [(url, data[0], data[1]) for url, data in final_results.items()]

def export_to_csv(results: list, filename: str = "report.csv") -> None:
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Status Code", "Message"])
            for url, status, msg in results:
                writer.writerow([url, status, msg])
        console.print(f"\n[green]📁 Reporte guardado correctamente en: {filename}[/green]")
    except IOError as e:
        console.print(f"[red]Error al escribir el archivo CSV: {e}[/red]")

def render_results(results: list, show_all: bool = False) -> None:
    stats = {"ok": 0, "redirect": 0, "broken": 0, "error": 0}
    table = Table(title="Resultados del Análisis", title_style="bold magenta")
    
    table.add_column("Estado", justify="center")
    table.add_column("Código", justify="center")
    table.add_column("URL")

    for url, status, msg in results:
        if status == 200:
            stats["ok"] += 1
            icon, style = "✓", "green"
        elif status in (301, 302):
            stats["redirect"] += 1
            icon, style = "→", "yellow"
        elif status in (404, 410):
            stats["broken"] += 1
            icon, style = "✗", "red"
        else:
            stats["error"] += 1
            icon, style = "⚠", "bold red"

        if show_all or status != 200:
            table.add_row(f"[{style}]{icon}[/{style}]", str(status), url)

    if table.rows:
        console.print(table)

    console.print("\n[bold]RESUMEN DE COBERTURA[/bold]")
    console.print(f" [green]✓ Correctos:[/green]    {stats['ok']}")
    console.print(f" [yellow]→ Redirecciones:[/yellow] {stats['redirect']}")
    console.print(f" [red]✗ Rotos (404):[/red]  {stats['broken']}")
    console.print(f" [bold red]⚠ Errores/Otros:[/bold red] {stats['error']}")

async def main():
    parser = argparse.ArgumentParser(description="Link Checker Crawler Asíncrono")
    parser.add_argument("url", nargs="?", help="URL base a escanear")
    parser.add_argument("--depth", type=int, default=1, help="Profundidad de navegación")
    parser.add_argument("--all", action="store_true", help="Muestra enlaces válidos en la tabla de consola")
    parser.add_argument("--export", action="store_true", help="Exportar resultados a un archivo CSV")

    args = parser.parse_args()
    
    target_url = args.url or input("Introduce la URL inicial: ").strip()
    if not target_url:
        console.print("[red]Debes especificar una URL válida.[/red]")
        return

    target_url = normalize_url(target_url)
    
    console.print(f"[bold]Iniciando rastreo en:[/bold] {target_url}")
    results = await crawl(target_url, args.depth)
    
    render_results(results, show_all=args.all)

    if args.export:
        export_to_csv(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Proceso cancelado por el usuario.[/yellow]")