class EmptyDataframeError(Exception):
    def __init__(self, symbol):
        message = ("AlphaVantage returned an empty DataFrame for symbol {}")
        super().__init__(message)

class TrainingLengthError(Exception):
    def __init__(self, len_training, len_window):
        message = ("Length of the training set is smaller than "
                 f"that of the window span ({len_training} vs {len_window}).")
        super().__init__(message)

class InternetError(Exception):
    def __init__(self):
        message = ("Connectivity error. Either machine is not "\
                   "connected to the internet or no driver is installed.")
        super().__init__(message)