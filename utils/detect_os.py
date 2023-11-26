import platform

def detect_os():
    system_name = platform.system()

    if system_name == "Linux":
        return "linux"
    elif system_name == "Windows":
        return "windows"
    elif system_name == "Darwin":
        return "macos"
    else:
        raise OSError(f"Unsupported operating system: {system_name}")

operating_sys = detect_os()