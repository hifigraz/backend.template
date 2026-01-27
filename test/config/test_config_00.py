import BACKEND_NAME_PLACEHOLDER


def test_config_00() -> None:
    config = BACKEND_NAME_PLACEHOLDER.config.Config.get_instance()
    assert config

    assert "sqlite:///:memory:" == config.connection_string
