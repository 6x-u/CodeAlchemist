import os
import py7zr
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from cr.tmpl import get_readme_credits
import time
import io

console = Console()

def compress_7z(folder_path, parent_dir):
    output_file = os.path.join(parent_dir, "CodeAlchemist.7z")
    files = get_all_files(folder_path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Compressing with 7Z ultra mero compression...", total=len(files) + 1)
        
        with py7zr.SevenZipFile(output_file, 'w') as archive:
            credits_bytes = io.BytesIO(get_readme_credits().encode('utf-8'))
            archive.writef(credits_bytes, "CREDITS.txt")
            progress.update(task, advance=1)
            time.sleep(0.05)
            
            if os.path.isfile(folder_path):
                archive.write(folder_path, os.path.basename(folder_path))
                progress.update(task, advance=1)
            else:
                for file in files:
                    arcname = os.path.relpath(file, os.path.dirname(folder_path))
                    archive.write(file, arcname)
                    progress.update(task, advance=1)
                    time.sleep(0.02)
    
    console.print(f"\n[bold green]7Z compression completed with mero algorithms![/bold green]")
    console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
    return output_file

def get_all_files(folder_path):
    files = []
    if os.path.isfile(folder_path):
        return [folder_path]
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files
