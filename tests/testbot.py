import pytest
from core import bot, store

@pytest.fixture
def fake(monkeypatch):
    dados = []
    monkeypatch.setattr(bot, "USERS", {"111": "Ana"})
    monkeypatch.setattr(store, "rows", lambda: dados)
    monkeypatch.setattr(store, "has_message", lambda mid: False)
    monkeypatch.setattr(store, "add", lambda r: dados.append(r))
    return dados

def test_valores_variados(fake):
    bot.handle("/aporte 200", 111, 1)
    bot.handle("/aporte 100", 111, 2)
    bot.handle("aportei 350,75", 111, 3)
    bot.handle("200", 111, 4)
    assert [r["amount"] for r in fake] == [200.0, 100.0, 350.75, 200.0]

def test_milhar_e_rejeicoes(fake):
    assert bot.to_float("1.234") == 1234.0
    assert bot.to_float("1.234,56") == 1234.56
    bot.handle("/aporte 0", 111, 5)
    bot.handle("/aporte 999999", 111, 6)
    assert fake == []