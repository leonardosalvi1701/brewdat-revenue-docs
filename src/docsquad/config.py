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
from dotenv import dotenv_values, load_dotenv

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


def perfil_databricks() -> tuple[str, str]:
    """Nome do perfil do Databricks e de onde ele veio: `.env` ou `terminal`.

    Aqui o `.env` ganha do terminal, ao contrario das demais variaveis. O
    terminal integrado da extensao do Databricks no VS Code exporta
    DATABRICKS_CONFIG_PROFILE com o perfil dela, e esse valor passava na frente
    do `.env` sem aviso. O terminal so vale quando o `.env` esta em branco, que
    e o caso de execucao automatizada.
    """
    do_arquivo = (dotenv_values(ROOT / ".env").get("DATABRICKS_CONFIG_PROFILE") or "").strip()
    if do_arquivo:
        return do_arquivo, ".env"
    do_terminal = os.getenv("DATABRICKS_CONFIG_PROFILE", "").strip()
    if do_terminal:
        return do_terminal, "terminal"
    return "", ""


def path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)
