#!/usr/bin/env python3
"""
Simple launcher script for Sidekick AI.
Run this file to start the application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    from src.main import main
    main()
