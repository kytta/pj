# pj

`pj` is a tiny project and dependency manager for Python. Think of it as a very opinionated and very lightweight alternative to tools like Hatch, PDM, and Poetry. So lightweight, actually, that it's intended to be included into your repository!

`pj` does everything for you:

- **Virtualenv** with the name `.venv` will be created in your root
- **Python version** gets choosen automatically based on pyenv, asdf, or pyproject.toml
- **Dependency management** with pyproject.toml
- **Lockfiles** (kind of) — `pj` relies on `pip-tools` and its `pip-compile`
- **Dependency groups** (dev, docs, test) via differen `requirements-*.txt` files
- **Build** your project with `python -m build`
- **Self-maintaining** — it will pull the dependencies it needs

## Why?

For small libraries, I really don't want to force tools like PDM, Hatch, or uv on the casual contributors. Install this, execute that... I'd do everything with setuptools and virtualenv, but the scripts get cumbersome to memorize and execute. `pj` is a shortcut for these tasks.

## Install

You don't need pip! Just run this inside your project directory:

```shell
wget -o pj https://codeberg.org/kytta/pj/src/branch/main/pj.py
chmod +x pj
```

If you're on Windows:

```powershell
Invoke-WebRequest https://codeberg.org/kytta/pj/src/branch/main/pj.py
```

> **IMPORTANT**
> `pj` should be at the same place where your pyproject.toml is, no exceptions!
