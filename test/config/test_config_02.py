import json
import os

from .. import test_module

Config = test_module.config.Config


def test_root_user_from_file(tmp_path):
    config_file = os.path.join(tmp_path, "cfg.json")
    with open(config_file, "w") as f:
        json.dump({"root_user_name": "root", "root_password": "secret"}, f)
    config = Config(config_file)
    assert config.root_user_name == "root"
    assert config.root_password == "secret"


def test_env_overrides_file(tmp_path, monkeypatch):
    monkeypatch.setenv(Config.ENV_CONNECTION_STRING, "postgresql://env/db")
    config_file = os.path.join(tmp_path, "cfg2.json")
    with open(config_file, "w") as f:
        json.dump({"connection_string": "sqlite:///file.db"}, f)
    config = Config(config_file)
    assert config.connection_string == "postgresql://env/db"
