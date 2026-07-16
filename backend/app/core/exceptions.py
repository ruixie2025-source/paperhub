class AIServiceError(RuntimeError):
    """Raised when the configured AI provider cannot complete a request."""


class PDFParseError(RuntimeError):
    """Raised when a PDF cannot be parsed within the configured policy."""
