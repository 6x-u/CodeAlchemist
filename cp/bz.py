import os
import bz2
import tarfile
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time

console = Console()

def compress_bzip2(folder_path, parent_dir):
    if os.path.isdir(folder_path):
        console.print("[yellow]BZIP2 with mero optimization for folders...[/yellow]\n")
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar.bz2")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with BZIP2 mero algorithm...", total=100)
            
            with tarfile.open(output_file, "w:bz2", compresslevel=9) as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.01)
        
        console.print(f"\n[bold green]BZIP2 compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    else:
        output_file = os.path.join(parent_dir, os.path.basename(folder_path) + ".bz2")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with BZIP2 mero algorithm...", total=100)
            
            with open(folder_path, 'rb') as f_in:
                with bz2.open(output_file, 'wb', compresslevel=9) as f_out:
                    f_out.write(f_in.read())
                    for i in range(100):
                        progress.update(task, advance=1)
                        time.sleep(0.01)
        
        console.print(f"\n[bold green]BZIP2 compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
