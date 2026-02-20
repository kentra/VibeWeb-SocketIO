from app.main import app
from app.config import settings


def test_app_created():
    assert app is not None


def test_settings_defaults():
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.cors_origins == "*"
