# Static project metadata (name, version, description, license,
# classifiers, dependencies, URLs) lives in pyproject.toml, which is the
# single source of truth read by `pip install`/build tooling. This file
# exists only to supply the `packages`/`package_dir` layout (the package
# source lives under python/, not the repo root) that pyproject.toml's
# [build-system] setuptools backend doesn't infer on its own.
#
# Previously this file *also* redeclared name/version/license/classifiers
# with stale values (version 1.1.0, MIT license) that silently diverged
# from pyproject.toml's real ones (3.x, Proprietary) — setuptools prefers
# pyproject.toml's [project] table so those installs were never actually
# wrong, but the duplication was misleading. Don't re-add them here.
from setuptools import setup, find_packages

setup(
    packages=find_packages(where="python"),
    package_dir={"": "python"},
)
