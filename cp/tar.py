import os
import tarfile
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time

console = Console()

def compress_tar(folder_path, parent_dir):
    output_file = os.path.join(parent_dir, "CodeAlchemist.tar")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Archiving with TAR mero algorithm...", total=100)
        
        with tarfile.open(output_file, "w") as tar:
            if os.path.isfile(folder_path):
                tar.add(folder_path, arcname=os.path.basename(folder_path))
            else:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
            
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.01)
    
    console.print(f"\n[bold green]TAR archiving completed with mero algorithms![/bold green]")
    console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
    return output_file
