# pj

`pj` is a tiny project and dependency manager for Python. Think of it as a very opinionated and very lightweight
alternative to tools like Hatch, PDM, and Poetry. So lightweight, actually, that it's intended to be included into your
repository!

`pj` does everything for you:

- **Virtualenv** with the name `.venv` will be created in your root
- **Python version** gets choosen automatically based on pyenv, asdf, or pyproject.toml
- **Dependency management** with pyproject.toml
- **Lockfiles** (kind of) — `pj` relies on `pip-tools` and its `pip-compile`
- **Dependency groups** (dev, docs, test) via differen `requirements-*.txt` files
- **Build** your project with `python -m build`
- **Self-maintaining** — it will pull the dependencies it needs

## Why?

For small libraries, I really don't want to force tools like PDM, Hatch, or uv on the casual contributors. Install this,
execute that... I'd do everything with setuptools and virtualenv, but the scripts get cumbersome to memorize and
execute. `pj` is a shortcut for these tasks.

## Install & use

1. Put `pj` in your project root:

   ```shell
   wget https://codeberg.org/kytta/pj/raw/branch/main/pj.py
   ```

   If `wget` for some reason does not work in PowerShell:

   ```powershell
   Invoke-WebRequest https://codeberg.org/kytta/pj/raw/branch/main/pj.py
   ```

1. That's it!

   ```shell
   ./pj.py --help
   ```

1. **Pro tip:** Use aliases to type it faster!

   ```shell
   alias pj=./pj.py
   ```

   ```powershell
   Set-Alias pj .\pj.py
   ```

1. **Pro tip:** Add it to your repo so that everyone can use it

   ```shell
   git add pj.py && git commit -m "🎉 added pj"
   ```

## CLI Reference

Every command ensures that a virtual environment exists and that the packages are up-to-date.

### `pj run`

Runs a command inside virtual environment. For example:

```shell
pj run ruff check
```
