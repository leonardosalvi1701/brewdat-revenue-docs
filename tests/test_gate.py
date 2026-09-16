"""O portao e a garantia estrutural do repo. Se estes testes quebram, nada mais importa."""
import pytest

from docsquad.gate import BlockedByPolicy, Executor, Proposal, ProposalKind, ProposalStore


class FakeDevOps:
    def __init__(self):
        self.calls = []

    def add_comment(self, wid, text):
        self.calls.append(("comment", wid, text))
        return {"id": 1}

    def set_state(self, wid, state):
        self.calls.append(("state", wid, state))
        return {"id": wid}


@pytest.fixture
def store(tmp_path):
    for s in ("pending", "approved", "rejected", "applied"):
        (tmp_path / s).mkdir()
    return ProposalStore(root=tmp_path)


def _comment(target="123"):
    return Proposal(kind=ProposalKind.CARD_COMMENT, target=target,
                    summary="teste", payload={"text": "ola"})


def test_pendente_nao_aplica(store):
    p = _comment()
    store.save(p)
    devops = FakeDevOps()
    with pytest.raises(BlockedByPolicy):
        Executor(devops=devops, store=store).apply(p)
    assert devops.calls == []


def test_aprovada_aplica(store):
    p = _comment()
    store.save(p)
    p = store.approve(p.id, "Leo")
    devops = FakeDevOps()
    Executor(devops=devops, store=store).apply(p)
    assert devops.calls[0][0] == "comment"
    assert store.load(p.id).status == "applied"


def test_aprovacao_exige_identificacao(store):
    p = _comment()
    store.save(p)
    with pytest.raises(ValueError):
        store.approve(p.id, "   ")


def test_transicao_bloqueada_mesmo_aprovada(store):
    """Fechar card e decisao humana. Nem aprovacao destrava."""
    p = Proposal(kind=ProposalKind.CARD_TRANSITION, target="123", summary="fechar",
                 payload={"from_state": "Em Validacao", "to_state": "Concluido"})
    store.save(p)
    p = store.approve(p.id, "Leo")
    devops = FakeDevOps()
    with pytest.raises(BlockedByPolicy, match="bloqueada por politica"):
        Executor(devops=devops, store=store).apply(p)
    assert devops.calls == []


def test_transicao_fora_da_lista_branca(store):
    p = Proposal(kind=ProposalKind.CARD_TRANSITION, target="123", summary="x",
                 payload={"from_state": "Aberto", "to_state": "Concluido"})
    store.save(p)
    p = store.approve(p.id, "Leo")
    with pytest.raises(BlockedByPolicy):
        Executor(devops=FakeDevOps(), store=store).apply(p)


def test_notebook_fora_do_prefixo(store):
    p = Proposal(kind=ProposalKind.NOTEBOOK_WRITE, target="/Repos/producao/critico",
                 summary="x", payload={"content": "print(1)"})
    store.save(p)
    p = store.approve(p.id, "Leo")
    with pytest.raises(BlockedByPolicy, match="fora dos prefixos"):
        Executor(databricks=object(), store=store).apply(p)


class FakeDatabricks:
    def __init__(self, usuario="pessoa@teste"):
        self.usuario = usuario
        self.calls = []

    def resolver(self, path):
        return path.replace("{usuario}", self.usuario)

    def import_notebook(self, path, content, language="PYTHON", overwrite=False):
        self.calls.append(path)
        return {"path": path}


def _notebook(store, alvo):
    p = Proposal(kind=ProposalKind.NOTEBOOK_WRITE, target=alvo,
                 summary="x", payload={"content": "print(1)"})
    store.save(p)
    return store.approve(p.id, "Leo")


def test_notebook_na_pasta_do_proprio_usuario(store):
    p = _notebook(store, "/Workspace/Users/pessoa@teste/teste/nb")
    dbx = FakeDatabricks()
    Executor(databricks=dbx, store=store).apply(p)
    assert dbx.calls == ["/Workspace/Users/pessoa@teste/teste/nb"]


def test_notebook_na_pasta_de_outro_usuario(store):
    p = _notebook(store, "/Workspace/Users/outra@teste/teste/nb")
    dbx = FakeDatabricks()
    with pytest.raises(BlockedByPolicy, match="fora dos prefixos"):
        Executor(databricks=dbx, store=store).apply(p)
    assert dbx.calls == []


def test_prefixo_com_usuario_sem_resolver_falha_fechado(store):
    """Sem como saber quem aplica, `{usuario}` nao pode virar curinga."""
    p = _notebook(store, "/Workspace/Users/{usuario}/teste/nb")
    with pytest.raises(BlockedByPolicy, match="fora dos prefixos"):
        Executor(databricks=object(), store=store).apply(p)


@pytest.mark.parametrize("alvo", [
    "/Repos/teste/docs/../../producao/critico",
    "/Repos/teste/docs//nb",
    "Repos/teste/docs/nb",
])
def test_notebook_caminho_nao_normalizado(store, alvo):
    p = _notebook(store, alvo)
    dbx = FakeDatabricks()
    with pytest.raises(BlockedByPolicy, match="normalizado"):
        Executor(databricks=dbx, store=store).apply(p)
    assert dbx.calls == []


def test_notebook_prefixo_vizinho_nao_passa(store):
    """`/Repos/teste/docs` nao libera `/Repos/teste/docs-outro`."""
    p = _notebook(store, "/Repos/teste/docs-outro/nb")
    dbx = FakeDatabricks()
    with pytest.raises(BlockedByPolicy, match="fora dos prefixos"):
        Executor(databricks=dbx, store=store).apply(p)
    assert dbx.calls == []


def test_recusada_nao_vira_aprovada(store):
    p = _comment()
    store.save(p)
    store.reject(p.id, "texto generico demais")
    with pytest.raises(ValueError):
        store.approve(p.id, "Leo")


def test_criacao_de_card_fora_dos_tipos(store):
    """Criar card e escrita externa e precisa de politica como qualquer outra."""
    p = Proposal(kind=ProposalKind.CARD_CREATE, target="novo", summary="x",
                 payload={"type": "Epic", "title": "qualquer coisa"})
    store.save(p)
    p = store.approve(p.id, "Leo")
    with pytest.raises(BlockedByPolicy, match="fora dos tipos declarados"):
        Executor(devops=FakeDevOps(), store=store).apply(p)


def test_criacao_de_card_sem_titulo(store):
    p = Proposal(kind=ProposalKind.CARD_CREATE, target="novo", summary="x",
                 payload={"type": "Task", "title": "   "})
    store.save(p)
    p = store.approve(p.id, "Leo")
    with pytest.raises(BlockedByPolicy, match="titulo preenchido"):
        Executor(devops=FakeDevOps(), store=store).apply(p)


def test_todo_tipo_de_proposta_tem_politica(store):
    """Um ProposalKind novo sem checagem declarada deve ser recusado, nao passar."""
    from docsquad.gate.executor import Executor as Ex
    ex = Ex(store=store)
    declarados = {
        ProposalKind.CARD_COMMENT, ProposalKind.CARD_TRANSITION,
        ProposalKind.CARD_CREATE, ProposalKind.NOTEBOOK_WRITE,
    }
    assert set(ProposalKind) == declarados, (
        "ProposalKind novo detectado. Declare a politica dele em Executor.apply "
        "antes de usar."
    )
