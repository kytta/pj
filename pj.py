#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from typing import Sequence


def _warn(msg: str) -> None:
    sys.stderr.write(f"[WARNING] {msg}\n")
    sys.stderr.flush()


def _err(msg: str) -> None:
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()


if "NO_COLOR" in os.environ and "FORCE_COLOR" not in os.environ:
    warn = _warn
    err = _err
else:
    def warn(msg) -> None:
        return _warn(f"\033[33m{msg}\033[0m")

    def err(msg) -> None:
        return _err(f"\033[31m{msg}\033[0m")


def _get_cache_dir() -> str | None:
    if sys.platform == "win32":
        import ctypes

        if hasattr(ctypes, "windll"):
            buf = ctypes.create_unicode_buffer(1024)
            # 28 = CSIDL_LOCAL_APPDATA
            ctypes.windll.shell32.SHGetFolderPathW(None, 28, None, 0, buf)

            # Downgrade to short path name if it has high-bit chars.
            if any(ord(c) > 255 for c in buf):  # noqa: PLR2004
                buf2 = ctypes.create_unicode_buffer(1024)
                if ctypes.windll.kernel32.GetShortPathNameW(
                        buf.value, buf2, 1024,
                ):
                    buf = buf2

            return buf.value

        try:
            import winreg
        except ImportError:
            return os.environ.get("LOCALAPPDATA")
        else:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            directory, _ = winreg.QueryValueEx(key, "Local AppData")
            return str(directory)
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    else:
        path = os.environ.get("XDG_CACHE_HOME", "")
        if not path.strip():
            path = os.path.expanduser("~/.cache")
        return path


def _get_own_venv_path(fallback_root: str | bytes | os.PathLike) -> str:
    cache_dir = _get_cache_dir()
    if cache_dir is None:
        warn(
            "Could not find a proper cache directory. "
            "pj's own venv will live at .pj-venv",
        )
        return os.path.join(fallback_root, ".pj-venv")

    return os.path.join(_get_cache_dir(), "pj", "virtualenv")


def _find_root() -> str:
    we = os.path.dirname(__file__)

    root = os.getcwd()

    if os.path.commonpath([we, root]) == we:
        return we

    sysroot = os.path.abspath("/")

    while True:
        if "pyproject.toml" in os.listdir(root):
            return root
        root = os.path.dirname(root)
        if root == sysroot:
            m = "Cannot find project root"
            raise LookupError(m)


def _make_venv(path: str | bytes | os.PathLike):
    try:
        from virtualenv import cli_run

        cli_run([str(path)])
    except ImportError:
        import venv

        venv.create(path, symlinks=True, with_pip=True)


def _ensure_venv(venv_path: str | bytes | os.PathLike) -> None:
    if os.path.isdir(venv_path) and os.path.exists(
            os.path.join(venv_path, "pyvenv.cfg"),
    ):
        return

    _make_venv(venv_path)


def _run_in_venv(
        venv_path: str | bytes | os.PathLike,
        executable: str,
        *args: str,
) -> None:
    import subprocess

    subprocess.check_call(
        [
            executable,
            *args,
        ],
        executable=os.path.join(venv_path, "bin", executable),
    )


def _ensure_own_requirements(venv_path: str | bytes | os.PathLike) -> None:
    _run_in_venv(
        venv_path,
        "pip",
        "install",
        "--upgrade",
        "pip",
        "pip-tools",
        "shellingham",
        "virtualenv",
    )


def main(argv: Sequence[str] | None = None) -> None:
    try:
        project_root = _find_root()
    except LookupError:
        err(
            "Cannot find project root. "
            "Make sure pj.py is in the same directory with pyproject.toml",
        )
        exit(1)

    project_venv = os.path.join(project_root, ".venv")

    venv_path = _get_own_venv_path(project_root)

    def launch_in_own_venv():
        try:
            _ensure_venv(venv_path)
        except Exception as exc:
            err(f"Could not create virtual environment: {exc!s}")

        _ensure_own_requirements(venv_path)

        os.execv(  # noqa: S606
            os.path.join(venv_path, "bin", "python"), [
                "pj",
                __file__,
                *(argv or []),
            ],
        )

    if sys.prefix != sys.base_prefix:
        project_venv = os.path.join(project_root, ".venv")

        if sys.prefix != venv_path:
            if sys.prefix == project_venv:
                print("we are in project venv")
                launch_in_own_venv()
            else:
                err("You are in a different virtualenv. Deactivate it first")
                sys.exit(1)
        else:
            print("we are in OUR OWN venv")

            import argparse
            parser = argparse.ArgumentParser(
                description="A tiny project & dependency manager to take with you", )
            subparsers = parser.add_subparsers(dest="command")
            add_cmd = subparsers.add_parser("add", help="Add a dependency")
            add_cmd.add_argument(
                "--group", "-G", action="store", const="dev", dest="group",
                help="Specify the target dependency group to add into", )
            add_cmd.add_argument(
                "--dev",
                "-D",
                action="store",
                const="dev",
                dest="group",
                help="Add packages into dev dependencies. Equivalent to `--group dev`",
            )

            subparsers.add_parser(
                "shell", help="Spawns a shell within the virtual environment.",
            )

            args = parser.parse_args(argv)

            try:
                project_root = _find_root()
            except LookupError:
                err("Cannot find project root. Make sure pj.py is in the same directory with pyproject.toml")
                sys.exit(1)

            if args.command == "add":
                if args.group is None:
                    raise NotImplementedError
                raise NotImplementedError

            project_venv = os.path.join(project_root, ".venv")

            if args.command == "shell":
                if getattr(sys, "real_prefix", sys.prefix) == project_venv:
                    sys.exit(0)

                raise NotImplementedError

        sys.exit(0)
    else:
        print("we are NOT in virtualenv")

        launch_in_own_venv()


if __name__ == "__main__":
    main()
