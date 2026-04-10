import random
from rich.console import Console
from rich.spinner import Spinner as RichSpinner
from rich.live import Live
from rich.text import Text

# Shared console instance used across the whole app
console = Console()

QUOTES = [
    "Consulting the mainframe…",
    "Synthesizing logic…",
    "Bending the matrix…",
    "Drinking virtual coffee…",
    "Compiling thoughts…",
    "Evaluating your code…",
    "Simulating outcomes…",
    "Reversing the polarity…",
    "Aligning the vectors…",
    "Traversing the graph…",
    "Reading your source code…",
    "Assembling the bytes…",
]


class Spinner:
    """Context manager that shows a rich animated spinner while Lambda is thinking."""

    def __init__(self, message: str = "Thinking"):
        self._label = random.choice(QUOTES) if random.random() > 0.3 else message
        self._live = None

    def __enter__(self):
        renderable = RichSpinner(
            "dots",
            text=Text(f" {self._label}", style="dim cyan italic"),
            style="bold cyan",
        )
        self._live = Live(
            renderable,
            console=console,
            refresh_per_second=15,
            transient=True,
        )
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)
