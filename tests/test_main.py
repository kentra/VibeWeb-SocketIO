from app.main import app
from app.config import settings


def test_app_created():
    assert app is not None


def test_settings_defaults():
    assert settings.host == "0.0.0.0"
    assert settings.port > 0
    assert settings.cors_origins == "*"
    assert settings.ping_timeout == 60
    assert settings.ping_interval == 25
