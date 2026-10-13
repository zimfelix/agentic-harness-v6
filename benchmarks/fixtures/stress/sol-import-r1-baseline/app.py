"""Public entrypoint; no installed package required."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from inventory.cli import main

if __name__ == '__main__':
    sys.exit(main())
