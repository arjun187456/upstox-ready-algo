from __future__ import annotations

import argparse

from .broker.paper import PaperBroker
from .broker.upstox_live import UpstoxLiveBroker
from .config import load_config
from .engine import run_strategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upstox ready algo bot")
    parser.add_argument("run", nargs="?", default="run")
    parser.add_argument("--mode", choices=["paper", "live"], default=None)
    parser.add_argument("--data-source", choices=["simulated", "upstox"], default=None)
    parser.add_argument("--iterations", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()

    if args.mode:
        config.app_mode = args.mode
    if args.data_source:
        config.data_source = args.data_source

    if config.app_mode == "live":
        if not config.upstox_access_token:
            raise RuntimeError("UPSTOX_ACCESS_TOKEN is required in live mode")
        broker = UpstoxLiveBroker(config.upstox_access_token)
    else:
        broker = PaperBroker(config.initial_capital)

    summary = run_strategy(config, broker, args.iterations)
    print("\nRun Summary")
    print(summary)


if __name__ == "__main__":
    main()
