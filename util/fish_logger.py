import logging

logging.basicConfig(level=logging.INFO,
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(levelname)s\t%(asctime)s\t%(filename)s:%(lineno)s\t%(funcName)s\t%(message)s')

log = logging