#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from typing import NoReturn
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

__version__ = "0.1.0"

VENV_NAME = ".venv"


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

    return parser


def _run(
        project_venv: str | bytes | os.PathLike,
        program: str,
        rest: Sequence[str],
) -> int:
    command = (
        program,
        *rest,
    )

    activator = os.path.join(project_venv, "bin", "activate_this.py")
    with open(activator) as f:
        exec(f.read(), {"__file__": activator})

    import shutil
    executable = shutil.which(program)
    if executable is None:
        err(f"{program}: could not find executable")
        return 1

    import subprocess

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


def main(_argv: Sequence[str] | None = None) -> int:
    argv: Sequence[str] = _argv if _argv is not None else sys.argv[1:]
    args, rest = _make_parser().parse_known_args(argv)

    project_root, project_venv = _get_locations()

    if args.command == "run":
        return _run(project_venv, args.program, rest)

    abort("You... shouldn't be here", 42)


if __name__ == "__main__":
    raise SystemExit(main())
