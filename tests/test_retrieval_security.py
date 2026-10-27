import pytest

from pystreammcp.retrieval.errors import RetrievalError
from pystreammcp.retrieval.security import (
    check_markdown_image_refs,
    make_display_path,
    resolve_ingest_path,
    validate_qmd_url,
)


def test_outside_root_rejected(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    outside = tmp_path / "x.md"
    outside.write_text("x")
    with pytest.raises(RetrievalError, match="outside") as exc:
        resolve_ingest_path(str(outside), (root.resolve(),), (".md",), 1024)
    assert exc.value.code == "path_outside_allowed_roots"


def test_symlink_rejected_even_inside_root(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    real = root / "a.md"
    real.write_text("x")
    link = root / "b.md"
    link.symlink_to(real)
    with pytest.raises(RetrievalError) as exc:
        resolve_ingest_path(str(link), (root.resolve(),), (".md",), 1024)
    assert exc.value.code == "symlink_not_allowed"


def test_html_rejected_unconditionally(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    html = root / "a.html"
    html.write_text("<p>x</p>")
    with pytest.raises(RetrievalError) as exc:
        resolve_ingest_path(str(html), (root.resolve(),), (".html",), 1024)
    assert exc.value.code == "unsupported_extension"


def test_extension_and_size(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    exe = root / "a.exe"
    exe.write_text("x")
    big = root / "b.md"
    big.write_bytes(b"x" * 2048)
    with pytest.raises(RetrievalError) as e1:
        resolve_ingest_path(str(exe), (root.resolve(),), (".md",), 4096)
    assert e1.value.code == "unsupported_extension"
    with pytest.raises(RetrievalError) as e2:
        resolve_ingest_path(str(big), (root.resolve(),), (".md",), 1024)
    assert e2.value.code == "file_too_large"


def test_markdown_image_outside_root_rejected_and_remote_ignored(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (tmp_path / "outside.png").write_bytes(b"png")
    doc = root / "a.md"
    doc.write_text("![x](../outside.png)\n![r](https://example.com/a.png)\n")
    with pytest.raises(RetrievalError) as exc:
        check_markdown_image_refs(doc.resolve(), (root.resolve(),))
    assert exc.value.code == "path_outside_allowed_roots"


def test_display_path_is_root_qualified(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    f = root / "a" / "b.md"
    f.parent.mkdir()
    f.write_text("x")
    assert make_display_path(f.resolve(), (root.resolve(),)) == "docs/a/b.md"


def test_remote_qmd_url_requires_opt_in():
    with pytest.raises(RetrievalError, match="loopback"):
        validate_qmd_url("https://qmd.example.com", allow_remote=False)
    validate_qmd_url("http://127.0.0.1:8181", allow_remote=False)
    validate_qmd_url("https://qmd.example.com", allow_remote=True)
