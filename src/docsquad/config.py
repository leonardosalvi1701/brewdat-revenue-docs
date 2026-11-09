"""Carregamento de configuracao e segredos.

A politica do portao vem de `config/settings.yaml`, que descreve o processo real
da squad e muda quando o processo muda. Os testes do portao nao podem depender
desse arquivo: se dependessem, uma mudanca legitima de processo quebraria a
garantia central do repo, e a tentacao seria afrouxar o teste.

Por isso o caminho e sobrescrivel por `DOCSQUAD_SETTINGS`. Producao usa o padrao;
os testes apontam para uma fixture propria com um processo estavel e ficticio.

A identidade de cada pessoa (`usuarios`) nao fica no `settings.yaml`, que e
versionado e compartilhado. Ela mora em `config/usuarios.local.yaml`, fora do
git, e e juntada ao settings na leitura. Com `DOCSQUAD_SETTINGS` definido, o
arquivo local so entra se `DOCSQUAD_USUARIOS` apontar para ele: assim os
testes nao dependem da maquina de quem roda.
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


USUARIOS_LOCAL = "config/usuarios.local.yaml"
USUARIOS_EXEMPLO = "config/usuarios.example.yaml"


def _caminho_usuarios() -> str | None:
    if os.getenv("DOCSQUAD_USUARIOS"):
        return os.getenv("DOCSQUAD_USUARIOS")
    if os.getenv("DOCSQUAD_SETTINGS"):
        return None
    padrao = ROOT / USUARIOS_LOCAL
    return str(padrao) if padrao.exists() else None


@lru_cache(maxsize=8)
def _settings(caminho: str, usuarios: str | None) -> dict:
    base = dict(_load_yaml(caminho) or {})
    if usuarios:
        locais = (_load_yaml(usuarios) or {}).get("usuarios") or {}
        base["usuarios"] = {**(base.get("usuarios") or {}), **locais}
    return base


def settings() -> dict:
    return _settings(
        os.getenv("DOCSQUAD_SETTINGS") or str(ROOT / "config" / "settings.yaml"),
        _caminho_usuarios(),
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
    """Perfil SSO definido no settings, unica fonte usada pelo codigo."""
    nome = (settings().get("databricks", {}).get("perfil") or "").strip()
    return nome, "config/settings.yaml" if nome else ""


def path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)
