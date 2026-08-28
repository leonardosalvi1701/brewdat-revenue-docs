"""Propostas de escrita.

Uma proposta e um arquivo JSON descrevendo uma acao que ALGUEM quer executar
num sistema externo. Gerar proposta nao executa nada. O agente so sabe chegar
ate aqui; ele nao tem acesso ao Executor.

Ciclo de vida das pastas:
    pending/   gerada, aguardando humano
    approved/  humano aprovou e se identificou
    rejected/  humano recusou, com motivo
    applied/   executor aplicou, com resultado registrado
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from ..config import path


class ProposalKind(str, Enum):
    CARD_COMMENT = "card_comment"
    CARD_TRANSITION = "card_transition"
    CARD_CREATE = "card_create"
    NOTEBOOK_WRITE = "notebook_write"


STATUSES = ("pending", "approved", "rejected", "applied")


@dataclass
class Proposal:
    kind: ProposalKind
    target: str                      # id do card, ou caminho do notebook
    summary: str                     # uma linha, o que sera feito
    payload: dict                    # conteudo especifico do tipo
    rationale: str = ""              # por que o agente propos isto
    sources: list = field(default_factory=list)  # commits, cards, notebooks usados
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    status: str = "pending"
    approved_by: str | None = None
    approved_at: str | None = None
    rejection_reason: str | None = None
    result: dict | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Proposal":
        d = dict(d)
        d["kind"] = ProposalKind(d["kind"])
        return cls(**d)


class ProposalStore:
    """Persistencia em disco. Deliberadamente simples e auditavel via git."""

    def __init__(self, root: Path | None = None):
        self.root = root or path("proposals")

    def _file(self, status: str, pid: str) -> Path:
        return self.root / status / f"{pid}.json"

    def _find(self, pid: str) -> tuple[str, Path]:
        for status in STATUSES:
            f = self._file(status, pid)
            if f.exists():
                return status, f
        raise FileNotFoundError(f"Proposta {pid} nao encontrada.")

    def save(self, proposal: Proposal) -> Path:
        target = self._file(proposal.status, proposal.id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(proposal.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return target

    def load(self, pid: str) -> Proposal:
        _, f = self._find(pid)
        return Proposal.from_dict(json.loads(f.read_text(encoding="utf-8")))

    def list(self, status: str = "pending") -> list[Proposal]:
        folder = self.root / status
        if not folder.exists():
            return []
        out = []
        for f in sorted(folder.glob("*.json")):
            out.append(Proposal.from_dict(json.loads(f.read_text(encoding="utf-8"))))
        return out

    def _move(self, proposal: Proposal, new_status: str) -> Path:
        old_status, old_file = self._find(proposal.id)
        proposal.status = new_status
        new_file = self.save(proposal)
        if old_file != new_file:
            old_file.unlink()
        return new_file

    def approve(self, pid: str, approver: str) -> Proposal:
        p = self.load(pid)
        if p.status != "pending":
            raise ValueError(f"Proposta {pid} esta em '{p.status}', nao em 'pending'.")
        if not approver.strip():
            raise ValueError("Aprovacao exige identificacao do aprovador.")
        p.approved_by = approver.strip()
        p.approved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._move(p, "approved")
        return p

    def reject(self, pid: str, reason: str) -> Proposal:
        p = self.load(pid)
        if p.status != "pending":
            raise ValueError(f"Proposta {pid} esta em '{p.status}', nao em 'pending'.")
        p.rejection_reason = reason
        self._move(p, "rejected")
        return p

    def mark_applied(self, proposal: Proposal, result: dict) -> Proposal:
        proposal.result = result
        self._move(proposal, "applied")
        return proposal
