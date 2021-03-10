import logging  # type: ignore
from logging.handlers import TimedRotatingFileHandler
# custom modules
from config.constants import Logs


# overriding computeRollover from the logging module to roll-over the logfile exactly on the hour
class WholeIntervalRotatingFileHandler(TimedRotatingFileHandler):
    def computeRollover(self, current_time: int) -> int:
        if self.when[0] == 'W' or self.when == 'MIDNIGHT':  # type: ignore
            # use existing computation
            return super().computeRollover(current_time)  # type: ignore
        # round time up to nearest next multiple of the interval
        return ((current_time // self.interval) + 1) * self.interval  # type:ignore


log_handler = WholeIntervalRotatingFileHandler('logs/logfile', when='MIDNIGHT')
log_formatter = logging.Formatter(Logs.FMT, datefmt=Logs.DATE_FMT)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
