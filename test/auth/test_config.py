import json
import logging

from BACKEND_NAME_PLACEHOLDER.config import Config


def _write(tmp_path, data, name="cfg.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return str(path)


def _clear_env(monkeypatch):
    for var in ("CONNECTION_STRING", "LOG_LEVEL", "ADMIN_USER", "ADMIN_PASSWORD", "SECRET_KEY"):
        monkeypatch.delenv(var, raising=False)


def test_defaults(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    cfg = Config(str(tmp_path / "missing.json"))  # file does not exist -> defaults
    assert cfg.connection_string == Config.DB_CONNECTION_STRING
    assert cfg.admin_user == "admin"
    assert cfg.admin_password is None
    assert cfg.secret_key is None
    assert cfg.log_level is None


def test_loads_from_file(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    path = _write(
        tmp_path,
        {
            "connection_string": "postgresql://admin:pw@localhost/db",
            "log_level": "INFO",
            "admin_user": "RootUser",
            "admin_password": "secretpw",
            "secret_key": "abc123",
        },
    )
    cfg = Config(path)
    assert cfg.connection_string == "postgresql://admin:pw@localhost/db"
    assert cfg.admin_user == "RootUser"
    assert cfg.admin_password == "secretpw"
    assert cfg.secret_key == "abc123"
    assert cfg.log_level == logging.INFO


def test_env_overrides_file(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setenv("CONNECTION_STRING", "sqlite:///from_env.sqlite")
    monkeypatch.setenv("ADMIN_PASSWORD", "envpw")
    path = _write(
        tmp_path,
        {"connection_string": "sqlite:///from_file.sqlite", "admin_password": "filepw"},
        name="cfg_env.json",
    )
    cfg = Config(path)
    assert cfg.connection_string == "sqlite:///from_env.sqlite"
    assert cfg.admin_password == "envpw"


def test_get_instance_is_singleton_per_file(tmp_path):
    path = _write(tmp_path, {"admin_user": "x"}, name="single.json")
    a = Config.get_instance(path)
    b = Config.get_instance(path)
    assert a is b
