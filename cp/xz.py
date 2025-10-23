import os
import lzma
import tarfile
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time

console = Console()

def compress_xz(folder_path, parent_dir):
    if os.path.isdir(folder_path):
        console.print("[yellow]XZ with maximum mero compression for folders...[/yellow]\n")
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar.xz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with XZ maximum mero compression...", total=100)
            
            with tarfile.open(output_file, "w:xz", preset=9) as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.015)
        
        console.print(f"\n[bold green]XZ compression completed with maximum mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    else:
        output_file = os.path.join(parent_dir, os.path.basename(folder_path) + ".xz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with XZ maximum mero compression...", total=100)
            
            with open(folder_path, 'rb') as f_in:
                with lzma.open(output_file, 'wb', preset=9) as f_out:
                    f_out.write(f_in.read())
                    for i in range(100):
                        progress.update(task, advance=1)
                        time.sleep(0.015)
        
        console.print(f"\n[bold green]XZ compression completed with maximum mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
