#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
from typing import NoReturn
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

__version__ = "0.1.0"

VENV_NAME = ".venv"


def doing(msg: str) -> None:
    sys.stderr.write(msg + "...")
    sys.stderr.flush()


def done() -> None:
    sys.stderr.write("done" + "\n")
    sys.stderr.flush()


def log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


if "NO_COLOR" in os.environ and "FORCE_COLOR" not in os.environ:
    _warn_tag = "[WARNING] "
    _err_tag = "[ERROR] "
else:
    _warn_tag = "\033[97;43m WARNING \033[0m "
    _err_tag = "\033[97;41m ERROR \033[0m "


def warn(msg: str) -> None:
    log(_warn_tag + msg)


def err(msg: str) -> None:
    log(_err_tag + msg)


def abort(msg: str, code: int = 1) -> NoReturn:
    err(msg)
    raise SystemExit(code)


def execute(
        program: str, args: Sequence[str],
        executable: str | None = None,
) -> int:
    import subprocess

    command = (program, *args)

    if executable is None:
        executable = shutil.which(program)

    if executable is None:
        abort(f"{program}: could not find executable")

    try:
        completed = subprocess.run(
            command,
            executable=executable,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        err(f"'{program}' exited with code {exc.returncode}")
        return exc.returncode

    return completed.returncode


# Adapted from `platformdirs`
# Copyright (c) 2010-202x The platformdirs developers
# Licensed under the MIT License
def _get_cache_dir_location() -> str | None:
    path = os.environ.get("XDG_CACHE_HOME", "")
    if path.strip():
        return path

    if sys.platform == "win32":
        import ctypes

        if not hasattr(ctypes, "windll"):
            return os.environ.get("LOCALAPPDATA")

        buf = ctypes.create_unicode_buffer(1024)
        # 28 = CSIDL_LOCAL_APPDATA
        ctypes.windll.shell32.SHGetFolderPathW(None, 28, None, 0, buf)

        # Downgrade to short path name if it has high-bit chars.
        if any(ord(c) > 255 for c in buf) or buf.value == "":
            return os.environ.get("LOCALAPPDATA")

        return buf.value

    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")

    return os.path.expanduser("~/.cache")


def ensure_pj_venv() -> str:
    cache_dir_location = _get_cache_dir_location()
    if cache_dir_location is None:
        venv_path = os.path.join(os.getcwd(), ".pjvenv")
    else:
        venv_path = os.path.join(
            os.path.realpath(cache_dir_location),
            "pj",
            "virtualenv",
        )

    if os.path.exists(os.path.join(venv_path, "pyvenv.cfg")):
        return venv_path

    doing("Initializing environment")
    try:
        import virtualenv
    except ImportError:
        import venv
        venv.create(venv_path, symlinks=True, with_pip=True)
    else:
        virtualenv.cli_run(["--python", sys.executable, venv_path])
    done()

    return venv_path


def ensure_module(name: str, project: str | None = None) -> None:
    if name in sys.modules:
        return

    from importlib.util import find_spec
    from importlib.util import module_from_spec
    if (spec := find_spec(name)) is not None:
        module = module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return

    doing(f"Installing '{project or name}'")
    from importlib import invalidate_caches
    from importlib import import_module
    from subprocess import check_output as exe
    exe([sys.executable, "-m", "pip", "install", project or name])
    invalidate_caches()
    import_module(name)
    done()


def _get_locations() -> tuple[str, str]:
    root = os.path.dirname(__file__)

    if os.path.commonpath([root, os.getcwd()]) == root:
        # cwd is with us or deeper
        return root, os.path.join(root, VENV_NAME)

    root = os.getcwd()
    sysroot = os.path.abspath("/")
    while True:
        if "pyproject.toml" in os.listdir(root):
            return root, os.path.join(root, VENV_NAME)
        root = os.path.dirname(root)
        if root == sysroot:
            abort(
                "Cannot find project root. "
                "Make sure pj.py is in the same directory with "
                "pyproject.toml",
                1,
            )


def _make_parser() -> argparse.ArgumentParser:
    import argparse

    parser = argparse.ArgumentParser(
        description="A tiny project & dependency manager to take with you",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=__version__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Run an executable inside a virtual environment",
    )
    run_parser.add_argument(
        "program",
        type=str,
        help="program to run",
    )

    subparsers.add_parser(
        "build",
        help="Run an executable inside a virtual environment",
    )

    return parser


def main(_argv: Sequence[str] | None = None) -> int:
    argv: Sequence[str] = _argv if _argv is not None else sys.argv[1:]

    pj_venv_path = ensure_pj_venv()

    if sys.prefix != pj_venv_path:
        # rerun in venv
        os.execv(
            shutil.which(os.path.join(pj_venv_path, "bin", "python3")),
            ("python3", *sys.argv),
        )

    args, rest = _make_parser().parse_known_args(argv)

    project_root, project_venv = _get_locations()

    if args.command == "build":
        ensure_module("build")
        return execute(
            "python3",
            ("-m", "build", *rest),
            executable=sys.executable,
        )

    if args.command == "run":
        os.environ["PATH"] = os.pathsep.join([
            os.path.join(project_venv, 'bin'),
            *os.environ.get("PATH", "").split(os.pathsep)
        ])
        return execute(args.program, rest)

    abort("You... shouldn't be here", 42)


if __name__ == "__main__":
    raise SystemExit(main())
