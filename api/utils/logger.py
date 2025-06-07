import logging
import sys

# Configure the logger
logger = logging.getLogger("MCPClient")
logger.setLevel(logging.DEBUG)

# File handler with Debug level
file_handler = logging.FileHandler("mcp_client.log")  # this line creates a file handler
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Console handler with Info level
console_handler = logging.StreamHandler(
    sys.stdout
)  # this line creates a console handler. sys.stdout is used to print to the console
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)
