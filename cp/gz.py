import os
import gzip
import tarfile
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time

console = Console()

def compress_gzip(folder_path, parent_dir):
    if os.path.isdir(folder_path):
        console.print("[yellow]GZIP with mero optimization for folders...[/yellow]\n")
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar.gz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with GZIP mero algorithm...", total=100)
            
            with tarfile.open(output_file, "w:gz", compresslevel=9) as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.01)
        
        console.print(f"\n[bold green]GZIP compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    else:
        output_file = os.path.join(parent_dir, os.path.basename(folder_path) + ".gz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with GZIP mero algorithm...", total=100)
            
            with open(folder_path, 'rb') as f_in:
                with gzip.open(output_file, 'wb', compresslevel=9) as f_out:
                    f_out.write(f_in.read())
                    for i in range(100):
                        progress.update(task, advance=1)
                        time.sleep(0.01)
        
        console.print(f"\n[bold green]GZIP compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
