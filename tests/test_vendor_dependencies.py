import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vendor" / "deps.lock.json"
EXPECTED = {
    "qmd": ("v2.8.3", "facd35e01359e59d938bc9418e93fb9318addee3", "vendor/qmd"),
    "rag-anything": ("v1.4.3", "afb67c43d391b1b1008a6fee9f020a232067b9e5", "vendor/rag-anything"),
    "lightrag": ("v1.4.16", "964f26e9a9239c1316045913328e863ec35492e4", "vendor/lightrag"),
}


def test_lock_pins_and_paths():
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    assert set(data["dependencies"]) == set(EXPECTED)
    for name, (tag, commit, path) in EXPECTED.items():
        dep = data["dependencies"][name]
        assert (dep["tag"], dep["commit"], dep["path"]) == (tag, commit, path)
        assert dep["license"] == "MIT"
        assert dep["ecosystem"] == ("npm" if name == "qmd" else "python")
        assert dep["repo"].startswith("https://github.com/")
        assert (ROOT / path / "LICENSE").is_file()
        assert not (ROOT / path / ".git").exists()
        assert not (ROOT / path / "node_modules").exists()
        assert "tree_sha256" in dep and len(dep["tree_sha256"]) == 64


def test_no_symlinks_in_vendor_tree():
    for path in (ROOT / "vendor").rglob("*"):
        assert not path.is_symlink(), f"symlink in vendor: {path}"


def test_verifier_passes_and_rejects_modification(tmp_path):
    ok = subprocess.run(
        [sys.executable, "scripts/vendor_dependencies.py", "verify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert ok.returncode == 0, ok.stderr
    target = ROOT / "vendor" / "lightrag" / "README.md"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\nlocal edit\n")
        bad = subprocess.run(
            [sys.executable, "scripts/vendor_dependencies.py", "verify"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert bad.returncode != 0
    finally:
        target.write_bytes(original)
