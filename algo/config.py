"""Configuration management for the trading system."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration loaded from environment variables or a .env file."""

    # Upstox API credentials
    API_KEY: str = os.getenv("UPSTOX_API_KEY", "")
    API_SECRET: str = os.getenv("UPSTOX_API_SECRET", "")
    REDIRECT_URI: str = os.getenv("UPSTOX_REDIRECT_URI", "https://127.0.0.1")
    ACCESS_TOKEN: str = os.getenv("UPSTOX_ACCESS_TOKEN", "")

    # Upstox API base URL (v2)
    BASE_URL: str = "https://api.upstox.com/v2"

    # Trading defaults
    DEFAULT_EXCHANGE: str = os.getenv("UPSTOX_DEFAULT_EXCHANGE", "NSE")
    DEFAULT_PRODUCT: str = os.getenv("UPSTOX_DEFAULT_PRODUCT", "D")  # Delivery
    DEFAULT_VALIDITY: str = os.getenv("UPSTOX_DEFAULT_VALIDITY", "DAY")

    # Strategy parameters
    SHORT_WINDOW: int = int(os.getenv("STRATEGY_SHORT_WINDOW", "5"))
    LONG_WINDOW: int = int(os.getenv("STRATEGY_LONG_WINDOW", "20"))
