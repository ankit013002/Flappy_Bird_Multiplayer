# Create a new file named DebugLogger.py

import logging
import os
import datetime

# Configure logging


def setup_logger():
    """Set up a logger for debugging the multiplayer functionality."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/flappy_bird_mp_{timestamp}.log"

    # Configure the logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("FlappyBird")


# Create logger instance
logger = setup_logger()

# Usage example:
# from DebugLogger import logger
# logger.debug("Pipe list received: %s", str(pipe_list))
# logger.info("Player %d connected", player_id)
# logger.error("Failed to process message: %s", str(e))
