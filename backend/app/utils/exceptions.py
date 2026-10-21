class DemandIQException(Exception):
    """Base exception for DemandIQ AI."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class DatasetNotFoundError(DemandIQException):
    def __init__(self, message: str = "Dataset not found"):
        super().__init__(message, status_code=404)

class DatasetValidationError(DemandIQException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class ModelNotFoundError(DemandIQException):
    def __init__(self, message: str = "Model not found"):
        super().__init__(message, status_code=404)

class ModelTrainingError(DemandIQException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class ForecastError(DemandIQException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class InventoryError(DemandIQException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

