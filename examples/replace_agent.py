"""Tiny demo agent for the PatchGym calculator example.

This is intentionally not a general agent. It shows the shell-command contract:
PatchGym runs the command inside the repository snapshot, and the command edits
files in place.
"""

from pathlib import Path


path = Path("calculator.py")
text = path.read_text()
path.write_text(text.replace("return lower\n    return value", "return upper\n    return value", 1))
