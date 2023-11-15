from dependencies import authenticator
import pandas as pd

from abc import abstractmethod
from typing import Any

class BaseExtractor:
    """Set requirements for child 'XYZExtractor' classes.
    """
    def __init__(self):
        self.api_key = authenticator.api_key

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        pass