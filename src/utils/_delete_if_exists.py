import os

from loguru import logger


def delete_if_exists(filepath):
    """Deletes a file if it exists.

    Args:
        filepath: The path to the file.
    """
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.debug(f"File `{filepath}` deleted successfully.")
        except OSError:
            logger.debug(f"Error deleting file `{filepath}`: ", exc_info=True)
    else:
        logger.debug(f"File `{filepath}` does not exist.")
