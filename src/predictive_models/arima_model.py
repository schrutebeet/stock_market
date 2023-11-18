from src.predictive_models.base import BaseModel
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from typing import Tuple, Any

class ArimaModel(BaseModel): 
    
    def __init__(self, p: int, d: int , q: int) -> None:
        self.p = p
        self.d = d
        self.q = q
    
    def __str__(self) -> str:
        return f"Instance of an ARIMA model with ({self.p}, {self.d}, {self.q}) order"

    def forecast(self, test_data: pd.Series) -> Tuple[Any, Any, Any]:
        forecast, stderr, conf_int = self.model.forecast(steps=len(test_data))
        return (forecast, stderr, conf_int)

    def fit(self, train_data: pd.Series) -> None:
        """Fit the training data into the model.

        Args:
            train_data (pd.Series): Training data found in the Stock class.
        """
        model = ARIMA(train_data, order=(self.p, self.d, self.q))
        self.model = model.fit()
    

