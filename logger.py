from datetime import datetime
from enum import Enum


class Level(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    IPC = "IPC"


class Logger:
    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def log(self, level: str, message: str):
        print(f"[{self._timestamp()}] {level}: {message}")

    def info(self, message: str):
        self.log(Level.INFO.value, message)

    def warning(self, message: str):
        self.log(Level.WARNING.value, message)

    def error(self, message: str):
        self.log(Level.ERROR.value, message)

    def ipc(self, message: str):
        self.log(Level.IPC.value, message)


logger = Logger()

# logger.ipc("peer fingerprint: 84F7E5F3BABCDC6A4AD19F3A09DB2B1CA04064F81E1D971D9F274E45E9C2355B")
# logger.info("connected to secure socket")
# logger.info("server tls certificate info: /CN=Deskflow")
# logger.info("network encryption protocol: TLSv1.3")
# logger.info("local languages: en")
# logger.info("remote languages: pt")
# logger.warning("You need to install these languages on this computer and restart Deskflow to enable support for multiple languages: pt")
# logger.ipc("connected to server")
# logger.info("entering screen")
# logger.info("clipboard was updated")
# logger.info("leaving screen")