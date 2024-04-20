# colors.py

class Colors:
    GREEN = '\033[92m'  # Green text
    BLUE = '\033[94;1m'  # Bright blue text
    RED = '\033[91m'    # Red text
    YELLOW = '\033[93m' # Yellow text
    END = '\033[0m'     # Reset to default color

def print_green(msg):
    """
    Print a given message in green color on a terminal.

    Args:
    msg (str): The message to be printed.
    """
    print(f"{Colors.GREEN}{msg}{Colors.END}")


def print_blue (msg):
    print(f"{Colors.BLUE}{msg}{Colors.END}")

def print_red (msg):
    print(f"{Colors.RED}{msg}{Colors.END}")

def print_yellow(msg):
    """
    Print a given message in yellow color on a terminal.

    Args:
    msg (str): The message to be printed.
    """
    print(f"{Colors.YELLOW}{msg}{Colors.END}")
