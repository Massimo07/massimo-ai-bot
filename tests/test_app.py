import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest

import app


def test_home_route():
    client = app.app.test_client()
    resp = client.get('/')
    assert resp.data.decode() == "Massimo AI è attivo e funzionante!"


def test_bot_initialization(monkeypatch):
    monkeypatch.setenv('TELEGRAM_TOKEN', 'dummy')
    bot_module = importlib.reload(importlib.import_module('bot'))
    assert hasattr(bot_module, 'bot')

