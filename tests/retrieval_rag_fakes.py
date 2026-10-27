import asyncio
import importlib.util
import sys
import types


class FakeQueryParam:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def install_fake_lightrag(monkeypatch):
    mod = types.ModuleType("lightrag")
    mod.__path__ = []
    mod.QueryParam = FakeQueryParam
    monkeypatch.setitem(sys.modules, "lightrag", mod)
    real = importlib.util.find_spec
    monkeypatch.setattr(
        "importlib.util.find_spec",
        lambda name, *a, **k: object()
        if name in {"raganything", "lightrag"}
        else real(name, *a, **k),
    )
    return mod


class FakeDocStatus:
    def __init__(self, records=None):
        self.records = records or {}

    async def get_by_id(self, doc_id):
        return self.records.get(doc_id)


class FakeTextChunks:
    def __init__(self, records=None):
        self.records = records or {}
        self.calls = []

    async def get_by_ids(self, ids):
        self.calls.append(list(ids))
        return [self.records[i] for i in ids if i in self.records]


class FakeLightRAG:
    def __init__(self, payload=None, delay=0.0, page_records=None):
        self.payload = payload or {
            "status": "success",
            "message": "ok",
            "data": {
                "chunks": [
                    {
                        "content": "alpha beta",
                        "file_path": "/docs/a.md",
                        "chunk_id": "c1",
                        "reference_id": "r1",
                    }
                ],
                "entities": [],
                "relationships": [],
                "metadata": {"processing_info": {"total_chunks": 1}},
            },
        }
        self.delay = delay
        self.query_calls = []
        self.text_chunks = FakeTextChunks(page_records or {})
        self.doc_status = FakeDocStatus()

    async def aquery_data(self, query, param):
        self.query_calls.append((query, param))
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.payload


class FakeRagEngine:
    def __init__(self, lightrag):
        self.lightrag = lightrag
        self.calls = []

    async def process_document_complete(self, **kwargs):
        self.calls.append(kwargs)
        self.lightrag.doc_status.records[kwargs["doc_id"]] = {
            "status": "processed"
        }
