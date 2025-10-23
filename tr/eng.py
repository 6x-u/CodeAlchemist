import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from dt.lang import get_language_by_ext, get_language_by_id
from cr.tmpl import get_credit_header

console = Console()

class TranslationEngine:
    def __init__(self):
        self.use_mero_engine = True
    
    def translate_code(self, source_file, target_lang_id):
        if not os.path.exists(source_file):
            console.print(f"[bold red]Error: File {source_file} not found![/bold red]")
            return None
        
        _, ext = os.path.splitext(source_file)
        source_lang = get_language_by_ext(ext)
        
        if not source_lang:
            console.print(f"[bold red]Error: Unknown file extension {ext}[/bold red]")
            return None
        
        target_lang = get_language_by_id(target_lang_id)
        
        if not target_lang:
            console.print(f"[bold red]Error: Invalid target language ID[/bold red]")
            return None
        
        console.print(f"\n[bold cyan]Translating from {source_lang['name']} to {target_lang['name']}...[/bold cyan]\n")
        
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        translated_code = self._mero_translation(source_code, source_lang, target_lang)
        
        credits = get_credit_header(target_lang['name'], target_lang['comment'])
        final_code = credits + translated_code
        
        source_dir = os.path.dirname(source_file)
        source_name = os.path.splitext(os.path.basename(source_file))[0]
        target_ext = target_lang['ext'][0]
        output_file = os.path.join(source_dir, f"{source_name}_translated{target_ext}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Saving translated file...", total=100)
            
            for i in range(100):
                progress.update(task, advance=1)
                if i % 20 == 0:
                    import time
                    time.sleep(0.05)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_code)
        
        console.print(f"\n[bold green]Translation completed successfully![/bold green]")
        console.print(f"[bold yellow]Output file: {output_file}[/bold yellow]\n")
        
        return output_file
    
    def _mero_translation(self, source_code, source_lang, target_lang):
        from tr.core import CodeTranslator
        
        translator = CodeTranslator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(
                f"[cyan]Translating {source_lang['name']} to {target_lang['name']} with mero powerful engine...",
                total=100
            )
            
            import time
            for i in range(0, 90, 10):
                progress.update(task, completed=i)
                time.sleep(0.05)
            
            translated_code = translator.smart_translate(
                source_code,
                source_lang['name'],
                target_lang['name']
            )
            
            progress.update(task, completed=100)
        
        return translated_code
