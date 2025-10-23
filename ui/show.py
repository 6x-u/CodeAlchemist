from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time

console = Console()

def show_intro():
    intro_text = [
        ("CodeAlchemist", "bold cyan"),
        ("", ""),
        ("Welcome", "green"),
        ("to", "white"),
        ("the", "white"),
        ("most", "yellow"),
        ("powerful", "yellow"),
        ("tool", "magenta"),
        ("ya", "white"),
        ("zalame!", "green"),
        ("", ""),
        ("This", "white"),
        ("thing", "cyan"),
        ("is", "white"),
        ("literally", "yellow"),
        ("fire", "red"),
        ("bro,", "white"),
        ("", ""),
        ("It", "white"),
        ("can", "white"),
        ("translate", "green"),
        ("your", "white"),
        ("code", "cyan"),
        ("from", "white"),
        ("any", "yellow"),
        ("language", "magenta"),
        ("to", "white"),
        ("any", "yellow"),
        ("other", "white"),
        ("language", "magenta"),
        ("you", "white"),
        ("want!", "green"),
        ("", ""),
        ("Plus,", "yellow"),
        ("it", "white"),
        ("compresses", "green"),
        ("folders", "cyan"),
        ("like", "white"),
        ("crazy", "red"),
        ("with", "white"),
        ("mad", "yellow"),
        ("algorithms", "magenta"),
        ("", ""),
        ("Supports", "green"),
        ("90+", "yellow"),
        ("programming", "cyan"),
        ("languages", "magenta"),
        ("wallah!", "green"),
        ("", ""),
        ("Developed", "white"),
        ("by", "white"),
        ("mero", "bold red"),
        ("", ""),
        ("Telegram:", "cyan"),
        ("@qp4rm", "bold yellow"),
    ]
    
    console.clear()
    
    text = Text()
    for word, style in intro_text:
        if word:
            text.append(word + " ", style=style)
        else:
            text.append("\n")
    
    panel = Panel(
        text,
        title="[bold magenta]CodeAlchemist v1.0[/bold magenta]",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    lines = str(text).split('\n')
    displayed_text = Text()
    
    for line_idx, line in enumerate(lines):
        current_line = Text()
        
        for word, style in intro_text:
            if word and word in line:
                current_line.append(word + " ", style=style)
                temp_panel = Panel(
                    displayed_text + current_line,
                    title="[bold magenta]CodeAlchemist v1.0[/bold magenta]",
                    border_style="bright_blue",
                    padding=(1, 2)
                )
                console.clear()
                console.print(temp_panel)
                time.sleep(0.08)
            elif not word:
                displayed_text.append(current_line)
                displayed_text.append("\n")
                current_line = Text()
                break
        
        if current_line:
            displayed_text.append(current_line)
    
    time.sleep(1)
    console.clear()
    console.print(panel)
    console.print("\n[bold green]Press Enter to continue...[/bold green]")
    input()
