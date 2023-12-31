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

class ValueOutOfBoundsException(Exception):
    def __init__(self):
        message = ("Argument 'period' out of bounds. Check accepted values.")
        super().__init__(message)

class APIError(Exception):
    def __init__(self):
        message = ("Successfully connected to AlphaVantage API, but an error ocurred anyway.\n"\
                   "Please, check logger for more information.")
        super().__init__(message)

class DriverError(Exception):
    def __init__(self, *args: object) -> None:
        message = ("The webdriver is missing for this type of OS.")
        super().__init__(*args)