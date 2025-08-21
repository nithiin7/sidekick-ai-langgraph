"""
Main entry point for the Sidekick AI application.
Handles application startup, configuration validation, and graceful shutdown.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.gradio_app import launch_app
from src.utils.config import config


def setup_logging() -> None:
    """Set up logging configuration."""
    # Ensure logs directory exists
    log_path = Path(config.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def validate_environment() -> bool:
    """
    Validate the environment configuration.
    
    Returns:
        True if validation passes, False otherwise
    """
    try:
        config.validate()
        return True
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your environment variables:")
        print("1. Copy env.example to .env")
        print("2. Set your OPENAI_API_KEY")
        print("3. Optionally set other API keys")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def main() -> None:
    """Main application entry point."""
    print("🚀 Starting Sidekick AI...")
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        logger.info("Environment validation passed")
        print("✅ Environment validation passed")
        
        # Launch the application
        print(f"🌐 Starting web interface on {config.APP_HOST}:{config.APP_PORT}")
        launch_app()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Sidekick AI...")
        logger.info("Application shutdown requested by user")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
