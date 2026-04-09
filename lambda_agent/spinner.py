import sys
import time
import threading
import itertools
import random


QUOTES = [
    "Consulting the mainframe… someone competent has to.",
    "Synthesizing logic… compensating for yours.",
    "Bending the matrix… fixing reality again.",
    "Drinking virtual coffee… this code needs patience.",
    "Compiling thoughts… wish you did the same.",
    "Evaluating your code… this explains a lot.",
    "Simulating outcomes… all better than your attempt.",
    "Reversing the polarity… like that was the issue.",
    "Aligning the vectors… unlike whatever you did.",
    "Traversing the graph… avoiding your mistakes.",
    "Reading your source code… unfortunate.",
    "Assembling the bytes… salvaging what I can.",
]


class Spinner:
    def __init__(self, message="Thinking..."):
        self.spinner_cycle = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        # Randomly choose a quote, or fallback to the provided message
        self.message = (
            f"{random.choice(QUOTES)} " if random.random() > 0.3 else f"{message} "
        )
        self.running = False
        self.spinner_thread = None

    def spin(self):
        while self.running:
            sys.stdout.write(
                f"\r\033[96m{next(self.spinner_cycle)} {self.message}\033[0m"
            )
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear the spinner line when done
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin, daemon=True)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
