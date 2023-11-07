from dependencies import authenticator
import pandas as pd

from abc import abstractmethod

class BaseExtractor:
    """Set requirements for child 'XYZExtractor' classes.
    """
    def __init__(self, symbol: str, function: str):
        self.symbol = symbol
        self.api_key = authenticator.api_key
        self.function = function.upper()

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        pass