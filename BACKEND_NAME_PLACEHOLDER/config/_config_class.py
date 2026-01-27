class Config:

    DB_CONNECTION_STRING: str = "sqlite:///:memory:"

    __instance: Config | None = None

    def __init__(self, file_name: str | None = None):
        if Config.__instance:
            raise RuntimeError("Don't Call constructor!")
        self._connection_string: str = Config.DB_CONNECTION_STRING
        if file_name:
            self.load(file_name)

    def load(self, filename: str) -> None:
        raise NotImplementedError(f"loading file {filename} not yet implemented.")

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @classmethod
    def get_instance(cls, file_name: str | None = None) -> Config:
        if not cls.__instance:
            cls.__instance = Config(file_name)
        return cls.__instance
