import os
import inspect


def env_path():
    """
    Find the path to the .env file.
    """
    caller_dir = os.getcwd()

    # Go up the directory tree until you find a directory with an .env file
    while not os.path.exists(os.path.join(caller_dir, '.env')):
        new_dir = os.path.dirname(caller_dir)
        if new_dir == caller_dir:
            # We've reached the root directory and there's still no .env file
            raise IOError(".env file not found.")
        caller_dir = new_dir

    return os.path.join(caller_dir, '.env')
