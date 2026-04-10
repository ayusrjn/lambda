from .agent import Agent
from . import config
from .spinner import console
import os

from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import box
from rich.align import Align


BANNER = r"""
██╗      █████╗ ███╗   ███╗██████╗ ██████╗  █████╗
██║     ██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗
██║     ███████║██╔████╔██║██████╔╝██║  ██║███████║
██║     ██╔══██║██║╚██╔╝██║██╔══██╗██║  ██║██╔══██║
███████╗██║  ██║██║ ╚═╝ ██║██████╔╝██████╔╝██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝
"""


def print_banner():
    banner_text = Text(BANNER, style="bold cyan", justify="center")
    subtitle = Text(
        "  Minimal AI Coding Agent  ·  Type 'exit' to quit  ",
        style="dim white",
        justify="center",
    )

    panel = Panel(
        Align.center(Text.assemble(banner_text, "\n", subtitle)),
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    )
    console.print(panel)


def print_user_message(text: str):
    label = Text(" YOU ", style="bold black on bright_yellow")
    content = Text(f"  {text}", style="bright_white")
    console.print()
    console.print(Text.assemble(label, content))


def print_lambda_message(text: str):
    console.print()
    label = Text(" LAMBDA ", style="bold black on cyan")
    console.print(label)
    console.print(
        Panel(
            Markdown(text),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )


def main():
    print_banner()

    try:
        if not config.API_KEY:
            from .cli_setup import run_setup

            config.API_KEY, config.MODEL_NAME = run_setup()
            os.environ["API_KEY"] = config.API_KEY
            os.environ["MODEL_NAME"] = config.MODEL_NAME

        agent = Agent()

        console.print(
            Rule("[bold cyan]Session Started[/bold cyan]", style="cyan"),
        )

        while True:
            try:
                # Styled prompt — uses plain input to keep cursor on same line
                user_input = Prompt.ask(
                    "\n[bold bright_yellow]  You[/bold bright_yellow]",
                    console=console,
                )

                if user_input.lower() in ["exit", "quit"]:
                    console.print()
                    console.print(
                        Panel(
                            "[bold cyan]Goodbye! Lambda signing off.[/bold cyan]",
                            border_style="cyan",
                            box=box.ROUNDED,
                        )
                    )
                    break

                if not user_input.strip():
                    continue

                response = agent.chat(user_input)
                print_lambda_message(response)

            except KeyboardInterrupt:
                console.print()
                console.print("[bold cyan]\nGoodbye![/bold cyan]")
                break

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Failed to initialize Lambda:[/bold red]\n{str(e)}",
                border_style="red",
                box=box.ROUNDED,
            )
        )


if __name__ == "__main__":
    main()
