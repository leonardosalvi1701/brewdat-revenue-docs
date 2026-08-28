"""Carregamento de configuracao e segredos.

A politica do portao vem de `config/settings.yaml`, que descreve o processo real
da squad e muda quando o processo muda. Os testes do portao nao podem depender
desse arquivo: se dependessem, uma mudanca legitima de processo quebraria a
garantia central do repo, e a tentacao seria afrouxar o teste.

Por isso o caminho e sobrescrivel por `DOCSQUAD_SETTINGS`. Producao usa o padrao;
os testes apontam para uma fixture propria com um processo estavel e ficticio.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")


@lru_cache(maxsize=8)
def _load_yaml(caminho: str) -> dict:
    with open(caminho, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def settings() -> dict:
    return _load_yaml(
        os.getenv("DOCSQUAD_SETTINGS") or str(ROOT / "config" / "settings.yaml")
    )


def glossario() -> dict:
    return _load_yaml(
        os.getenv("DOCSQUAD_GLOSSARIO") or str(ROOT / "config" / "glossario.yaml")
    )


def env(key: str, required: bool = True) -> str:
    value = os.getenv(key, "")
    if required and not value:
        raise RuntimeError(
            f"Variavel {key} ausente. Copie .env.example para .env e preencha."
        )
    return value


def path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)
