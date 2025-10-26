import logging
import os

def setup_logger(log_dir, log_file):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    
    # Файловый обработчик
    file_handler = logging.FileHandler(f"{log_dir}/{log_file}", mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Отключаем логи urllib3
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    
    return logger
