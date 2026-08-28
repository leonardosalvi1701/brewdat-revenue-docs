"""Aponta a configuracao para a fixture antes de qualquer import de docsquad.

Sem isto, os testes do portao leriam `config/settings.yaml` e passariam a
depender do processo vigente da squad.
"""
import os
from pathlib import Path

os.environ["DOCSQUAD_SETTINGS"] = str(Path(__file__).parent / "fixtures" / "settings.yaml")
