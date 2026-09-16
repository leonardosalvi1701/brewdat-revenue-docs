"""Executor: o unico ponto do sistema que escreve em sistema externo.

Regras estruturais, nao configuraveis:
  1. So aceita proposta com status 'approved' e approved_by preenchido.
  2. Revalida a politica no momento da aplicacao, nao so na geracao.
     Uma transicao bloqueada continua bloqueada mesmo aprovada por engano.
  3. Escrita em notebook so dentro dos prefixos declarados em settings, com o
     caminho normalizado. `{usuario}` no prefixo vira o login de quem aplica;
     sem como resolver, o prefixo nao vale.
  4. Criacao de card so com tipo declarado em settings e titulo preenchido.
  5. Nenhum agente importa este modulo. A separacao e fisica, nao contratual.

Toda escrita externa passa por uma checagem de politica propria. Um tipo de
proposta sem checagem seria um buraco no portao, entao a ausencia de checagem
e erro, nao omissao aceitavel.
"""
from __future__ import annotations

import posixpath

from ..config import settings
from .proposal import Proposal, ProposalKind, ProposalStore


class BlockedByPolicy(RuntimeError):
    """Levantada quando a politica recusa aplicar mesmo com aprovacao humana."""


class Executor:
    def __init__(self, devops=None, databricks=None, store: ProposalStore | None = None):
        self.devops = devops
        self.databricks = databricks
        self.store = store or ProposalStore()
        self.cfg = settings()

    # ---------- validacoes de politica ----------

    def _check_approved(self, p: Proposal) -> None:
        if p.status != "approved":
            raise BlockedByPolicy(
                f"Proposta {p.id} tem status '{p.status}'. So 'approved' e aplicavel."
            )
        if not p.approved_by:
            raise BlockedByPolicy(f"Proposta {p.id} sem aprovador identificado.")

    def _check_transition(self, p: Proposal) -> None:
        origem = p.payload.get("from_state")
        destino = p.payload.get("to_state")
        bloqueadas = [tuple(t) for t in self.cfg["devops"].get("transicoes_bloqueadas", [])]
        permitidas = [tuple(t) for t in self.cfg["devops"].get("transicoes_permitidas", [])]
        if (origem, destino) in bloqueadas:
            raise BlockedByPolicy(
                f"Transicao {origem} -> {destino} e bloqueada por politica. "
                "Fechamento de card e decisao humana, feita na interface do DevOps."
            )
        if (origem, destino) not in permitidas:
            raise BlockedByPolicy(
                f"Transicao {origem} -> {destino} nao esta na lista de permitidas."
            )

    def _check_card_create(self, p: Proposal) -> None:
        tipo = p.payload.get("type")
        permitidos = self.cfg["devops"].get("tipos", [])
        if tipo not in permitidos:
            raise BlockedByPolicy(
                f"Tipo de work item '{tipo}' fora dos tipos declarados: {permitidos}"
            )
        if not str(p.payload.get("title", "")).strip():
            raise BlockedByPolicy("Criacao de card exige titulo preenchido.")

    def _prefixos_escrita(self) -> list[str]:
        """Prefixos de escrita com `{usuario}` trocado pelo login de quem aplica.

        Falha fechada: sem cliente capaz de resolver o login, o prefixo com
        `{usuario}` e descartado, e nao comparado cru.
        """
        out = []
        for pref in self.cfg["databricks"].get("escrita_permitida", []):
            if "{usuario}" in pref:
                resolver = getattr(self.databricks, "resolver", None)
                if resolver is None:
                    continue
                pref = resolver(pref)
            out.append(posixpath.normpath(pref))
        return out

    def _check_notebook_path(self, p: Proposal) -> None:
        alvo = p.target
        # `..` ou barra dupla fariam um caminho passar no prefixo e cair fora
        # dele no workspace. Caminho que muda ao normalizar e recusado.
        if not alvo.startswith("/") or posixpath.normpath(alvo) != alvo:
            raise BlockedByPolicy(f"Caminho '{alvo}' nao esta normalizado.")
        prefixos = self._prefixos_escrita()
        # prefixo + "/" para que `.../docs` nao libere `.../docs-outro`.
        if not any(alvo.startswith(pref.rstrip("/") + "/") for pref in prefixos):
            raise BlockedByPolicy(
                f"Caminho '{alvo}' fora dos prefixos de escrita permitida: {prefixos}"
            )

    # ---------- aplicacao ----------

    def apply(self, proposal: Proposal, dry_run: bool = False) -> dict:
        self._check_approved(proposal)

        politica = {
            ProposalKind.CARD_COMMENT: None,  # comentario nao altera estado nem cria item
            ProposalKind.CARD_TRANSITION: self._check_transition,
            ProposalKind.CARD_CREATE: self._check_card_create,
            ProposalKind.NOTEBOOK_WRITE: self._check_notebook_path,
        }
        if proposal.kind not in politica:
            raise BlockedByPolicy(
                f"Tipo de proposta '{proposal.kind}' sem politica declarada."
            )
        checagem = politica[proposal.kind]
        if checagem is not None:
            checagem(proposal)

        if dry_run:
            return {"dry_run": True, "would_apply": proposal.summary}

        handler = {
            ProposalKind.CARD_COMMENT: self._apply_card_comment,
            ProposalKind.CARD_TRANSITION: self._apply_card_transition,
            ProposalKind.CARD_CREATE: self._apply_card_create,
            ProposalKind.NOTEBOOK_WRITE: self._apply_notebook_write,
        }[proposal.kind]

        result = handler(proposal)
        self.store.mark_applied(proposal, result)
        return result

    def _apply_card_comment(self, p: Proposal) -> dict:
        return self.devops.add_comment(int(p.target), p.payload["text"])

    def _apply_card_transition(self, p: Proposal) -> dict:
        return self.devops.set_state(int(p.target), p.payload["to_state"])

    def _apply_card_create(self, p: Proposal) -> dict:
        return self.devops.create_work_item(
            item_type=p.payload["type"],
            title=p.payload["title"],
            description=p.payload.get("description", ""),
            parent_id=p.payload.get("parent_id"),
            iteration=p.payload.get("iteration"),
        )

    def _apply_notebook_write(self, p: Proposal) -> dict:
        return self.databricks.import_notebook(
            path=p.target,
            content=p.payload["content"],
            language=p.payload.get("language", "PYTHON"),
            overwrite=True,
        )
