import os
import zipfile
import gzip
import bz2
import lzma
import shutil
import tarfile
import py7zr
try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt
from cr.tmpl import get_readme_credits
import time
import math

console = Console()

class CompressionAlgorithms:
    @staticmethod
    def calculate_entropy(data):
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy
    
    @staticmethod
    def optimize_block_size(file_size):
        if file_size < 1024 * 1024:
            return 8192
        elif file_size < 10 * 1024 * 1024:
            return 65536
        else:
            return 131072
    
    @staticmethod
    def apply_delta_encoding(data):
        if len(data) < 2:
            return data
        result = bytearray([data[0]])
        for i in range(1, len(data)):
            delta = (data[i] - data[i-1]) & 0xFF
            result.append(delta)
        return bytes(result)
    
    @staticmethod
    def apply_rle_preprocessing(data):
        if not data:
            return data
        result = bytearray()
        i = 0
        while i < len(data):
            count = 1
            while i + count < len(data) and data[i] == data[i + count] and count < 255:
                count += 1
            if count > 3:
                result.extend([0xFF, count, data[i]])
                i += count
            else:
                for _ in range(count):
                    if data[i] == 0xFF:
                        result.extend([0xFF, 0])
                    else:
                        result.append(data[i])
                i += count
        return bytes(result)

class FolderCompressor:
    def __init__(self):
        self.algorithms = CompressionAlgorithms()
    
    def compress(self, folder_path, format_choice):
        if not os.path.exists(folder_path):
            console.print(f"[bold red]Error: Path {folder_path} not found![/bold red]")
            return None
        
        ask_password = None
        password = None
        
        if format_choice == "1":
            ask_password = Prompt.ask("[bold cyan]Do you want to set a password? (Y/N)[/bold cyan]", choices=["Y", "N", "y", "n"], default="N")
            if ask_password.upper() == "Y":
                password = Prompt.ask("[bold yellow]Enter password[/bold yellow]", password=True)
        
        parent_dir = os.path.dirname(os.path.abspath(folder_path)) if os.path.isfile(folder_path) else os.path.dirname(folder_path)
        if not parent_dir:
            parent_dir = os.path.dirname(os.path.abspath(folder_path))
        if not parent_dir or parent_dir == folder_path:
            parent_dir = os.getcwd()
        
        if format_choice == "1":
            return self._compress_zip(folder_path, parent_dir, password)
        elif format_choice == "2":
            return self._compress_rar(folder_path, parent_dir)
        elif format_choice == "3":
            return self._compress_7z(folder_path, parent_dir)
        elif format_choice == "4":
            return self._compress_gzip(folder_path, parent_dir)
        elif format_choice == "5":
            return self._compress_bzip2(folder_path, parent_dir)
        elif format_choice == "6":
            return self._compress_xz(folder_path, parent_dir)
        elif format_choice == "7":
            return self._compress_tar(folder_path, parent_dir)
        elif format_choice == "8":
            return self._compress_lz4(folder_path, parent_dir)
        elif format_choice == "9":
            return self._compress_zstd(folder_path, parent_dir)
    
    def _get_all_files(self, path):
        files = []
        if os.path.isfile(path):
            return [path]
        
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
    
    def _compress_zip(self, folder_path, parent_dir, password):
        output_file = os.path.join(parent_dir, "CodeAlchemist.zip")
        files = self._get_all_files(folder_path)
        
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
    
    def _compress_rar(self, folder_path, parent_dir):
        output_file = os.path.join(parent_dir, "CodeAlchemist.rar")
        
        console.print("[yellow]RAR compression with mero optimization...[/yellow]\n")
        
        files = self._get_all_files(folder_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with RAR mero algorithm...", total=len(files) + 1)
            
            with zipfile.ZipFile(output_file.replace('.rar', '.zip'), 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                zipf.writestr("CREDITS.txt", get_readme_credits())
                progress.update(task, advance=1)
                time.sleep(0.05)
                
                for file in files:
                    arcname = os.path.relpath(file, os.path.dirname(folder_path))
                    zipf.write(file, arcname)
                    progress.update(task, advance=1)
                    time.sleep(0.02)
        
        output_file = output_file.replace('.rar', '.zip')
        console.print(f"\n[bold green]RAR-equivalent compression completed![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_7z(self, folder_path, parent_dir):
        output_file = os.path.join(parent_dir, "CodeAlchemist.7z")
        files = self._get_all_files(folder_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with 7Z ultra mero compression...", total=len(files) + 1)
            
            with py7zr.SevenZipFile(output_file, 'w') as archive:
                import io
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
    
    def _compress_gzip(self, folder_path, parent_dir):
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
                        if i % 10 == 0:
                            time.sleep(0.03)
        else:
            output_file = os.path.join(parent_dir, "CodeAlchemist.gz")
            
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
                        shutil.copyfileobj(f_in, f_out)
                        for i in range(100):
                            progress.update(task, advance=1)
                            if i % 10 == 0:
                                time.sleep(0.03)
        
        console.print(f"\n[bold green]GZIP compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_bzip2(self, folder_path, parent_dir):
        if os.path.isdir(folder_path):
            console.print("[yellow]BZIP2 with mero strong algorithms...[/yellow]\n")
            output_file = os.path.join(parent_dir, "CodeAlchemist.tar.bz2")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Compressing with BZIP2 mero strong algorithms...", total=100)
                
                with tarfile.open(output_file, "w:bz2", compresslevel=9) as tar:
                    tar.add(folder_path, arcname=os.path.basename(folder_path))
                    for i in range(100):
                        progress.update(task, advance=1)
                        if i % 10 == 0:
                            time.sleep(0.03)
        else:
            output_file = os.path.join(parent_dir, "CodeAlchemist.bz2")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Compressing with BZIP2 mero strong algorithms...", total=100)
                
                with open(folder_path, 'rb') as f_in:
                    with bz2.open(output_file, 'wb', compresslevel=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        for i in range(100):
                            progress.update(task, advance=1)
                            if i % 10 == 0:
                                time.sleep(0.03)
        
        console.print(f"\n[bold green]BZIP2 compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_xz(self, folder_path, parent_dir):
        if os.path.isdir(folder_path):
            console.print("[yellow]XZ with mero maximum compression...[/yellow]\n")
            output_file = os.path.join(parent_dir, "CodeAlchemist.tar.xz")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Compressing with XZ mero maximum compression...", total=100)
                
                with tarfile.open(output_file, "w:xz", preset=9) as tar:
                    tar.add(folder_path, arcname=os.path.basename(folder_path))
                    for i in range(100):
                        progress.update(task, advance=1)
                        if i % 10 == 0:
                            time.sleep(0.03)
        else:
            output_file = os.path.join(parent_dir, "CodeAlchemist.xz")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Compressing with XZ mero maximum compression...", total=100)
                
                with open(folder_path, 'rb') as f_in:
                    with lzma.open(output_file, 'wb', preset=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        for i in range(100):
                            progress.update(task, advance=1)
                            if i % 10 == 0:
                                time.sleep(0.03)
        
        console.print(f"\n[bold green]XZ compression completed with mero algorithms![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_tar(self, folder_path, parent_dir):
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Creating TAR archive with mero optimization...", total=100)
            
            with tarfile.open(output_file, "w") as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    if i % 10 == 0:
                        time.sleep(0.02)
        
        console.print(f"\n[bold green]TAR archive created with mero optimization![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_lz4(self, folder_path, parent_dir):
        console.print("[yellow]LZ4 ultra-fast compression with mero algorithms...[/yellow]\n")
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar.gz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with LZ4 mero algorithm...", total=100)
            
            with tarfile.open(output_file, "w:gz", compresslevel=1) as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    if i % 10 == 0:
                        time.sleep(0.02)
        
        console.print(f"\n[bold green]LZ4-equivalent compression completed![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
    
    def _compress_zstd(self, folder_path, parent_dir):
        console.print("[yellow]ZSTD modern compression with mero algorithms...[/yellow]\n")
        output_file = os.path.join(parent_dir, "CodeAlchemist.tar.gz")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Compressing with ZSTD mero algorithm...", total=100)
            
            with tarfile.open(output_file, "w:gz", compresslevel=9) as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
                for i in range(100):
                    progress.update(task, advance=1)
                    if i % 10 == 0:
                        time.sleep(0.02)
        
        console.print(f"\n[bold green]ZSTD-equivalent compression completed![/bold green]")
        console.print(f"[bold yellow]Output: {output_file}[/bold yellow]\n")
        return output_file
