from __future__ import annotations

import json
import logging
import os

"""
A class for managing application configuration.

Provides a singleton pattern and loads settings from a JSON config file and/or
environment variables. Precedence: environment variable > config file > default.

Settings:
    connection_string : database connection string
    log_level         : logging level (name, e.g. "DEBUG")
    admin_user        : name of the initial root/admin user
    admin_password    : password of the initial root/admin user
    secret_key        : secret used to sign JWTs

Environment variables:
    CONNECTION_STRING, LOG_LEVEL, ADMIN_USER, ADMIN_PASSWORD, SECRET_KEY
Config file location can be set via the CONFIG_FILE environment variable.
"""


class Config:
    DB_CONNECTION_STRING: str = "sqlite:///:memory:"
    DEFAULT_ADMIN_USER: str = "admin"
    __instances: dict[str, "Config"] = {}

    KEY_CONNECTION_STRING: str = "connection_string"
    KEY_LOG_LEVEL: str = "log_level"
    KEY_ADMIN_USER: str = "admin_user"
    KEY_ADMIN_PASSWORD: str = "admin_password"
    KEY_SECRET_KEY: str = "secret_key"

    # config-key -> environment-variable name
    _ENV_VARS: dict[str, str] = {
        KEY_CONNECTION_STRING: "CONNECTION_STRING",
        KEY_LOG_LEVEL: "LOG_LEVEL",
        KEY_ADMIN_USER: "ADMIN_USER",
        KEY_ADMIN_PASSWORD: "ADMIN_PASSWORD",
        KEY_SECRET_KEY: "SECRET_KEY",
    }

    def __init__(self, file_name: str = ""):
        if file_name in Config.__instances:
            raise RuntimeError("Don't Call constructor!")
        Config.__instances[file_name] = self

        # 1) defaults
        self._connection_string: str = Config.DB_CONNECTION_STRING
        self._log_level: int | None = None
        self._admin_user: str = Config.DEFAULT_ADMIN_USER
        self._admin_password: str | None = None
        self._secret_key: str | None = None

        # 2) config file
        if file_name:
            self._load(file_name)

        # 3) environment variables (override file)
        self._load_env()

    def _load(self, filename: str) -> None:
        if not os.path.isfile(filename):
            return
        with open(filename, "r") as f:
            config_file: dict[str, str] = json.load(f)  # pyright: ignore[reportAny]
        if Config.KEY_CONNECTION_STRING in config_file:
            self._connection_string = config_file[Config.KEY_CONNECTION_STRING]
        if Config.KEY_ADMIN_USER in config_file:
            self._admin_user = config_file[Config.KEY_ADMIN_USER]
        if Config.KEY_ADMIN_PASSWORD in config_file:
            self._admin_password = config_file[Config.KEY_ADMIN_PASSWORD]
        if Config.KEY_SECRET_KEY in config_file:
            self._secret_key = config_file[Config.KEY_SECRET_KEY]
        if Config.KEY_LOG_LEVEL in config_file:
            self._set_log_level(config_file[Config.KEY_LOG_LEVEL])

    def _load_env(self) -> None:
        if value := os.getenv(self._ENV_VARS[Config.KEY_CONNECTION_STRING]):
            self._connection_string = value
        if value := os.getenv(self._ENV_VARS[Config.KEY_ADMIN_USER]):
            self._admin_user = value
        if value := os.getenv(self._ENV_VARS[Config.KEY_ADMIN_PASSWORD]):
            self._admin_password = value
        if value := os.getenv(self._ENV_VARS[Config.KEY_SECRET_KEY]):
            self._secret_key = value
        if value := os.getenv(self._ENV_VARS[Config.KEY_LOG_LEVEL]):
            self._set_log_level(value)

    def _set_log_level(self, level_name: str) -> None:
        if isinstance(level_name, str):
            level_mappings = logging.getLevelNamesMapping()
            if level_name in level_mappings:
                self._log_level = level_mappings[level_name]

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @property
    def log_level(self) -> int | None:
        return self._log_level

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def admin_password(self) -> str | None:
        return self._admin_password

    @property
    def secret_key(self) -> str | None:
        return self._secret_key

    @classmethod
    def get_instance(cls, file_name: str = "") -> "Config":
        """
        Returns the Config instance for the given file name (singleton).
        If no file name is given, the CONFIG_FILE environment variable is used.
        """
        if not file_name and "CONFIG_FILE" in os.environ:
            file_name = os.environ["CONFIG_FILE"]
        if file_name in cls.__instances:
            return cls.__instances[file_name]
        return Config(file_name)