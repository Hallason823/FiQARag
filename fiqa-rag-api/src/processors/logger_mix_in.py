import logging

"""Provides a dynamically named, encapsulated logger property to any inheriting subclass."""
class LoggerMixIn:

    #Returns a standard logging instance named automatically after the executing class.
    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(self.__class__.__name__)