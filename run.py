import os
import sys
import subprocess

def install_dependencies():
    print("Installing mero libraries...")
    packages = ["rich", "py7zr", "pyzipper"]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + packages)
        print("All libraries installed successfully by mero!")
        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def main():
    print("="*60)
    print("CodeAlchemist - Setup and Run")
    print("Developer: mero | Telegram: @qp4rm")
    print("="*60)
    
    if not install_dependencies():
        print("Failed to install dependencies!")
        return
    
    print("\nStarting CodeAlchemist...\n")
    
    try:
        from ui.show import show_intro
        from ui.menu import show_main_menu, show_languages_menu, show_compression_menu
        from tr.eng import TranslationEngine
        from cp.main import FolderCompressor
        from dt.lang import get_language_by_ext
        from rich.console import Console
        from rich.prompt import Prompt
        import webbrowser
        
        console = Console()
        
        def handle_translation():
            console.print("\n[bold cyan]Code Translation Tool[/bold cyan]\n")
            
                    
            file_path = Prompt.ask("[bold yellow]Enter the path to your source code file[/bold yellow]")
            
            if not os.path.exists(file_path):
                console.print(f"[bold red]Error: File not found![/bold red]")
                input("\nPress Enter to continue...")
                return
            
            _, ext = os.path.splitext(file_path)
            source_lang = get_language_by_ext(ext)
            
            if not source_lang:
                console.print(f"[bold red]Error: Unknown file type '{ext}'[/bold red]")
                input("\nPress Enter to continue...")
                return
            
            console.print(f"\n[bold green]Detected source language: {source_lang['name']}[/bold green]\n")
            
            show_languages_menu(source_lang['name'])
            
            try:
                target_lang_id = int(Prompt.ask("[bold yellow]Enter the number of target language[/bold yellow]"))
            except ValueError:
                console.print("[bold red]Invalid input![/bold red]")
                input("\nPress Enter to continue...")
                return
            
            engine = TranslationEngine()
            result = engine.translate_code(file_path, target_lang_id)
            
            if result:
                console.print("[bold green]Translation successful![/bold green]")
            
            input("\nPress Enter to continue...")

        def handle_compression():
            choice = show_compression_menu()
            
            if choice == "0":
                return
            
            console.print("\n[bold cyan]Folder/File Compression Tool[/bold cyan]\n")
            
            path = Prompt.ask("[bold yellow]Enter the path to folder or file[/bold yellow]")
            
            if not os.path.exists(path):
                console.print(f"[bold red]Error: Path not found![/bold red]")
                input("\nPress Enter to continue...")
                return
            
            compressor = FolderCompressor()
            result = compressor.compress(path, choice)
            
            if result:
                console.print("[bold green]Compression successful![/bold green]")
            
            input("\nPress Enter to continue...")

        def handle_developer_contact():
            console.clear()
            console.print("\n[bold cyan]Developer Contact[/bold cyan]\n")
            console.print("[bold yellow]Developer:[/bold yellow] mero")
            console.print("[bold yellow]Telegram:[/bold yellow] @qp4rm")
            console.print("\n[bold green]Opening Telegram...[/bold green]\n")
            
            try:
                webbrowser.open("https://t.me/qp4rm")
                console.print("[bold green]Telegram opened in your browser![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Could not open browser: {e}[/bold red]")
                console.print("[bold yellow]Please visit manually: https://t.me/qp4rm[/bold yellow]")
            
            input("\nPress Enter to continue...")

        show_intro()
        
        while True:
            choice = show_main_menu()
            
            if choice == "0":
                console.clear()
                console.print("\n[bold cyan]Thank you for using CodeAlchemist![/bold cyan]")
                console.print("[bold yellow]Developed by mero - Telegram: @qp4rm[/bold yellow]\n")
                sys.exit(0)
            elif choice == "1":
                handle_translation()
            elif choice == "2":
                handle_compression()
            elif choice == "3":
                handle_developer_contact()
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
