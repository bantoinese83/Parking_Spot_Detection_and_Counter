import os
import subprocess
from base_logging import Logger, ConsoleUtils

# Initialize the logger and console_utils
logger = Logger()
console_utils = ConsoleUtils()

# Load configuration from environment variables
log_level = os.getenv("LOG_LEVEL", "INFO")

# Set log level
logger.set_level(log_level)


def startup():
    try:
        logger.log_info("Application startup")
        console_utils.log_progress("Startup", 100, 100)
    except Exception as e:
        logger.log_error(f"Error occurred during startup: {str(e)}")


def run():
    try:
        logger.log_info("Application running")
        console_utils.log_progress("Running", 100, 100)

        # Run Black
        subprocess.run(["black", "."], check=True)
        logger.log_info("Black complete")

    except subprocess.CalledProcessError as e:
        logger.log_error(f"Error occurred during Black formatting: {str(e)}")
    except Exception as e:
        logger.log_error(f"Error occurred during run: {str(e)}")


def shutdown():
    try:
        logger.log_info("Application shutdown")
        console_utils.log_progress("Shutdown", 100, 100)
    except Exception as e:
        logger.log_error(f"Error occurred during shutdown: {str(e)}")
