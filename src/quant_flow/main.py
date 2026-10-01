from quant_flow.cli import parse_args
from quant_flow.screening import screen_symbols

from pathlib import Path

def main() -> None:
    screen_symbols(parse_args(), Path(__file__).resolve().parents[2] / "outputs")

if __name__ == "__main__":
    main()
