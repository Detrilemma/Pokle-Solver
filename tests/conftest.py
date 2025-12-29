"""Pytest configuration for pokle_solver tests.

Adds the src directory to sys.path so tests can import the package
without requiring installation.
"""

import sys
from pathlib import Path

# Add src directory to Python path for testing without installation
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
