# Retrieval benchmark

`retrieval_bench.py` measures the retrieval path without changing indexes or
printing document content or secrets.

## Modes

- **fake** (default): an in-script backend exercises routing, service dispatch,
  serialization, and metrics only. No network, model, or dependency is loaded.
- **qmd**: opt in with `--qmd-url`. Collections come from
  `PYSTREAMMCP_QMD_COLLECTIONS`.
- **rag**: opt in with `--rag`. Uses `RetrievalService.from_env()` and never
  ingests documents.

QMD and RAG scores are not comparable and this harness does not combine their
quality measurements.

## Corpus setup

The fake mode needs no corpus. For QMD, index the documents with QMD first and
start its HTTP service:

```bash
qmd mcp --http
export PYSTREAMMCP_QMD_COLLECTIONS=notes,docs
```

For RAG, configure the normal retrieval environment and an existing
`rag_storage` directory; do not run ingestion as part of the benchmark.

## Commands

```bash
python benchmarks/retrieval_bench.py --help
python benchmarks/retrieval_bench.py --queries 20 --json
python benchmarks/retrieval_bench.py --queries 20 --warmup 2 --query "deployment" --json
python benchmarks/retrieval_bench.py --qmd-url http://127.0.0.1:8181 --json
python benchmarks/retrieval_bench.py --rag --json
```

## Metrics

The JSON object reports `mode`, `sample_count`, `hit_count`, `empty_count`,
`error_count`, `timeout_count`, `p50_ms`, `p95_ms`, `p99_ms`, `mean_ms`, and
`throughput_qps`.

Warmup requests are excluded from the timing samples. Cold-start latency is
visible by running with `--warmup 0`; warm latency uses the default warmup of
one request.

Quality metrics (precision, recall, ranking quality) are future work. This
harness reports latency and error counts only and makes no fabricated quality
baseline.
