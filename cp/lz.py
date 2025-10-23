import os
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time

console = Console()

def compress_lz4(folder_path, parent_dir):
    output_file = os.path.join(parent_dir, "CodeAlchemist.lz4")
    
    console.print("[yellow]LZ4 ultra-fast mero compression...[/yellow]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Compressing with LZ4 ultra-fast mero algorithm...", total=100)
        
        try:
            import lz4.frame
            
            if os.path.isfile(folder_path):
                with open(folder_path, 'rb') as f_in:
                    with lz4.frame.open(output_file, 'wb') as f_out:
                        f_out.write(f_in.read())
            else:
                import tarfile
                tar_temp = output_file.replace('.lz4', '.tar')
                with tarfile.open(tar_temp, 'w') as tar:
                    tar.add(folder_path, arcname=os.path.basename(folder_path))
                
                with open(tar_temp, 'rb') as f_in:
                    with lz4.frame.open(output_file, 'wb') as f_out:
                        f_out.write(f_in.read())
                
                os.remove(tar_temp)
            
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.005)
            
        except ImportError:
            console.print("[yellow]lz4 library not available, using alternative compression...[/yellow]")
            import gzip
            with open(folder_path, 'rb') as f_in:
                with gzip.open(output_file.replace('.lz4', '.gz'), 'wb') as f_out:
                    f_out.write(f_in.read())
            output_file = output_file.replace('.lz4', '.gz')
            
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.005)
    
    console.print(f"\n[bold green]LZ4 ultra-fast compression completed with mero algorithms![/bold green]")
    console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
    return output_file
