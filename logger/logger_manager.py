# logger_manager.py
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LoggerManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir="logs", max_file_size=5*1024*1024, backup_count=5):
        if not hasattr(self, 'initialized'):
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(exist_ok=True)
            self.max_file_size = max_file_size
            self.backup_count = backup_count
            self.loggers = {}
            self.initialized = True
    
    def get_logger(self, name=__name__, level=logging.DEBUG):
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if logger.handlers:
            self.loggers[name] = logger
            return logger
        
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        log_file = self.log_dir / f"{name.replace('.', '_')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        logger.propagate = False
        
        self.loggers[name] = logger
        return logger
