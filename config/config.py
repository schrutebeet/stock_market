from pathlib import Path
from utils.error_handling import DriverError
from utils.detect_os import detect_os

class Config:
    def __init__(self) -> None:
        self.os = detect_os()

    def get_chrome_driver_path(self) -> Path:

        project_dir = Path(__file__).parent.parent

        if self.os == "windows":
            chromedriver_path = project_dir / Path("drivers/chrome-win64/chrome.exe")
        elif self.os == "linux":
            chromedriver_path = Path("/usr/local/bin/chromedriver")
        else:
            raise DriverError

        return chromedriver_path