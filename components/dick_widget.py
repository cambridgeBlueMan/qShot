import logging

# Configure logging for this module if not already configured globally
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

logging.info("dick_widget.py module loaded.")