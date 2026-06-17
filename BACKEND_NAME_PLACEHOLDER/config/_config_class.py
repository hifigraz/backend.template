import json
import logging
import os

"""
A class for managing application configuration.

Configuration values can be supplied in three ways, with the following
precedence (highest wins):

    1. Environment variables  (e.g. DATABASE_URL, ROOT_USER_NAME, ...)
    2. A JSON configuration file (path given directly or via CONFIG_FILE)
    3. Built-in defaults

Supported settings:
    - database connection string
    - root user (user name, password, display name)
    - log level

Attributes:
    DB_CONNECTION_STRING (str): Default SQLite in-memory database connection string.
    __instances (dict[str, Config]): A dictionary storing instances of this class keyed by
                                     their associated file names (singleton per file name).
"""


class Config:

    DB_CONNECTION_STRING: str = "sqlite:///:memory:"
    __instances: dict[str, "Config"] = {}

    # JSON keys (config file)
    KEY_CONNECTION_STRING: str = "connection_string"
    KEY_LOG_LEVEL: str = "log_level"
    KEY_ROOT_USER_NAME: str = "root_user_name"
    KEY_ROOT_PASSWORD: str = "root_password"
    KEY_ROOT_NAME: str = "root_name"

    # Environment variable names (override the config file)
    ENV_CONNECTION_STRING: str = "DATABASE_URL"
    ENV_LOG_LEVEL: str = "LOG_LEVEL"
    ENV_ROOT_USER_NAME: str = "ROOT_USER_NAME"
    ENV_ROOT_PASSWORD: str = "ROOT_PASSWORD"
    ENV_ROOT_NAME: str = "ROOT_NAME"

    def __init__(self, file_name: str = ""):
        if file_name in Config.__instances:
            raise RuntimeError("Don't Call constructor!")
        Config.__instances[file_name] = self

        # 1. defaults
        self._connection_string: str = Config.DB_CONNECTION_STRING
        self._log_level: int | None = None
        self._root_user_name: str | None = None
        self._root_password: str | None = None
        self._root_name: str | None = None

        # 2. config file (overrides defaults)
        if file_name:
            self._load(file_name)

        # 3. environment variables (override everything)
        self._load_env()

    def _load(self, filename: str) -> None:
        """Load configuration values from a JSON file. Missing keys keep their default."""
        if not os.path.isfile(filename):
            return
        with open(filename, "r") as f:
            config_file: dict[str, str] = json.load(f)  # pyright: ignore[reportAny]

        if Config.KEY_CONNECTION_STRING in config_file:
            self._connection_string = config_file[Config.KEY_CONNECTION_STRING]
        if Config.KEY_LOG_LEVEL in config_file:
            self._apply_log_level(config_file[Config.KEY_LOG_LEVEL])
        if Config.KEY_ROOT_USER_NAME in config_file:
            self._root_user_name = config_file[Config.KEY_ROOT_USER_NAME]
        if Config.KEY_ROOT_PASSWORD in config_file:
            self._root_password = config_file[Config.KEY_ROOT_PASSWORD]
        if Config.KEY_ROOT_NAME in config_file:
            self._root_name = config_file[Config.KEY_ROOT_NAME]

    def _load_env(self) -> None:
        """Override configuration values from environment variables (highest precedence)."""
        if Config.ENV_CONNECTION_STRING in os.environ:
            self._connection_string = os.environ[Config.ENV_CONNECTION_STRING]
        if Config.ENV_LOG_LEVEL in os.environ:
            self._apply_log_level(os.environ[Config.ENV_LOG_LEVEL])
        if Config.ENV_ROOT_USER_NAME in os.environ:
            self._root_user_name = os.environ[Config.ENV_ROOT_USER_NAME]
        if Config.ENV_ROOT_PASSWORD in os.environ:
            self._root_password = os.environ[Config.ENV_ROOT_PASSWORD]
        if Config.ENV_ROOT_NAME in os.environ:
            self._root_name = os.environ[Config.ENV_ROOT_NAME]

    def _apply_log_level(self, level_name: str | None) -> None:
        """Translate a textual log level (e.g. "DEBUG") into the numeric logging level."""
        if level_name and isinstance(level_name, str):
            level_mappings = logging.getLevelNamesMapping()
            if level_name in level_mappings:
                self._log_level = level_mappings[level_name]

    @property
    def connection_string(self) -> str:
        """The database connection string."""
        return self._connection_string

    @property
    def log_level(self) -> int | None:
        """The numeric log level, or None if not specified."""
        return self._log_level

    @property
    def root_user_name(self) -> str | None:
        """The root user's user name, or None if not configured."""
        return self._root_user_name

    @property
    def root_password(self) -> str | None:
        """The root user's password, or None if not configured."""
        return self._root_password

    @property
    def root_name(self) -> str | None:
        """The root user's display name, or None if not configured."""
        return self._root_name

    @classmethod
    def get_instance(cls, file_name: str = "") -> "Config":
        """
        Returns an instance of the Config class with the given file name. If no file name is provided,
        it will use the default connection string. If an instance already exists for the provided file
        name, it will return that instance instead of creating a new one.

        :param file_name: The file name of the configuration file (optional)
        :return: An instance of the Config class
        """
        if not file_name and "CONFIG_FILE" in os.environ:
            file_name = os.environ["CONFIG_FILE"]
        if file_name in cls.__instances:
            return cls.__instances[file_name]
        return Config(file_name)
