"""Aponta a configuracao para a fixture antes de qualquer import de docsquad.

Sem isto, os testes do portao leriam `config/settings.yaml` e passariam a
depender do processo vigente da squad.
"""
import os
from pathlib import Path

os.environ["DOCSQUAD_SETTINGS"] = str(Path(__file__).parent / "fixtures" / "settings.yaml")

# O ~/.databrickscfg de quem roda os testes nao pode decidir o resultado. Os
# testes que precisam de perfil escrevem o proprio arquivo em tmp_path.
os.environ["DATABRICKS_CONFIG_FILE"] = str(Path(__file__).parent / "sem-databrickscfg")
