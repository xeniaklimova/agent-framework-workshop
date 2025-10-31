import json

# Create a proper Jupyter notebook structure
notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Read the XML content and parse cells
with open("Single-Agent.ipynb.bak", "r", encoding="utf-8") as f:
    content = f.read()

# Simple parser for VSCode.Cell format
import re

cells = re.findall(r'<VSCode\.Cell[^>]*language="([^"]+)"[^>]*>(.*?)</VSCode\.Cell>', content, re.DOTALL)

for lang, cell_content in cells:
    cell = {
        "cell_type": "markdown" if lang == "markdown" else "code",
        "metadata": {},
        "source": cell_content.strip().split('\n')
    }
    if cell["cell_type"] == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    notebook["cells"].append(cell)

# Write the proper JSON format
with open("Single-Agent.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1)

print(f"Converted {len(notebook['cells'])} cells to proper Jupyter format")
