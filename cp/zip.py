import os
import zipfile
try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from cr.tmpl import get_readme_credits
import time

console = Console()

def compress_zip(folder_path, parent_dir, password=None):
    output_file = os.path.join(parent_dir, "CodeAlchemist.zip")
    files = get_all_files(folder_path)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Compressing with ZIP mero algorithm...", total=len(files) + 1)
        
        if password and HAS_PYZIPPER:
            with pyzipper.AESZipFile(output_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(password.encode('utf-8'))
                
                zipf.writestr("CREDITS.txt", get_readme_credits())
                progress.update(task, advance=1)
                time.sleep(0.02)
                
                for file in files:
                    arcname = os.path.relpath(file, os.path.dirname(folder_path))
                    zipf.write(file, arcname)
                    progress.update(task, advance=1)
                    time.sleep(0.01)
        else:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                zipf.writestr("CREDITS.txt", get_readme_credits())
                progress.update(task, advance=1)
                time.sleep(0.02)
                
                for file in files:
                    arcname = os.path.relpath(file, os.path.dirname(folder_path))
                    zipf.write(file, arcname)
                    progress.update(task, advance=1)
                    time.sleep(0.01)
            
            if password:
                console.print("[yellow]Password protection requires pyzipper library. File compressed without password.[/yellow]")
    
    console.print(f"\n[bold green]ZIP compression completed with mero algorithms![/bold green]")
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
