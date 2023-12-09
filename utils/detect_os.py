import platform
from utils.log_config import logger 

def detect_os():
    system_name = platform.system()
    logger.info(f"Loaded model on {system_name} operating system.")

    if system_name == "Linux":
        return "linux"
    elif system_name == "Windows":
        return "windows"
    elif system_name == "Darwin":
        return "macos"
    else:
        raise OSError(f"Unsupported operating system: {system_name}")

operating_sys = detect_os()