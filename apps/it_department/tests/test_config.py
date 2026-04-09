from it_department.config import load_config
from it_department.llm_factory import get_role_models


def test_role_models_fallback(monkeypatch):
    monkeypatch.setenv("DEFAULT_MODEL", "fallback-model")
    monkeypatch.delenv("PM_MODEL", raising=False)
    monkeypatch.delenv("BA_MODEL", raising=False)
    config = load_config()
    models = get_role_models(config)
    assert models.pm == "fallback-model"
    assert models.ba == "fallback-model"
