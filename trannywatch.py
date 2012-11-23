from logging import getLogger, basicConfig
from tranny import config

def main():
    log = getLogger("tranny.main")
    log.info("Tranny initializing")

if __name__ == "__main__":
    log_level = config.getint('log', 'level')
    basicConfig(level=log_level)
    main()