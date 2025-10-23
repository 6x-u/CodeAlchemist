from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from dt.lang import LANGUAGES

console = Console()

def show_main_menu():
    console.clear()
    
    table = Table(title="[bold cyan]CodeAlchemist - Main Menu[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Number", style="cyan", width=10)
    table.add_column("Option", style="green")
    
    table.add_row("1", "Code Translation (Language to Language)")
    table.add_row("2", "Folder Compression")
    table.add_row("3", "Developer Contact")
    table.add_row("0", "Exit")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", choices=["0", "1", "2", "3"])
    return choice

def show_languages_menu(current_lang=None):
    console.clear()
    
    console.print(Panel(
        "[bold green]Available Programming Languages[/bold green]",
        border_style="cyan"
    ))
    console.print()
    
    cols = 3
    rows = (len(LANGUAGES) + cols - 1) // cols
    
    for row in range(rows):
        line_parts = []
        for col in range(cols):
            idx = row + col * rows
            if idx < len(LANGUAGES):
                lang = LANGUAGES[idx]
                num_str = f"[cyan]{lang['id']:2d}.[/cyan]"
                
                if current_lang and lang['name'] == current_lang:
                    lang_str = f"[bold yellow]{lang['name']}[/bold yellow] [green](Current)[/green]"
                else:
                    lang_str = f"[white]{lang['name']}[/white]"
                
                line_parts.append(f"{num_str} {lang_str:<30}")
        
        console.print("  ".join(line_parts))
    
    console.print()

def show_compression_menu():
    console.clear()
    
    table = Table(title="[bold cyan]Compression Options[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Number", style="cyan", width=10)
    table.add_column("Format", style="green")
    table.add_column("Description", style="white")
    
    table.add_row("1", "ZIP", "Standard compression with password support")
    table.add_row("2", "RAR", "High compression ratio")
    table.add_row("3", "7Z", "Ultra compression with mero algorithms")
    table.add_row("4", "GZIP", "Fast compression for files")
    table.add_row("5", "BZIP2", "Strong compression with advanced algorithms")
    table.add_row("6", "XZ", "Maximum compression with powerful algorithms")
    table.add_row("7", "TAR", "Archive format with mero optimization")
    table.add_row("8", "LZ4", "Ultra-fast compression")
    table.add_row("9", "ZSTD", "Modern compression algorithm")
    table.add_row("0", "Back to Main Menu")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("[bold yellow]Choose compression format[/bold yellow]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
    return choice
