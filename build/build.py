#!/usr/bin/env python3
"""Build tool for pademinune's Armor Penetration Calculator 2.

Runs on Python 3.6+ on any OS. The mod's own sources are compiled by a separate
Python 2.7 interpreter (--python27): the WoT client runs Python 2.7 and cannot
load bytecode from any other version.

Subcommands:

  deploy     Compile and copy everything into <wot-root>/res_mods/<version>/ as
             loose override files, for fast local iteration. Close the client
             first -- a running client locks files under its install dir.
  package    Compile and stage into bin/package/, then zip (ZIP_STORED) into
             bin/wotmods/pademinune-AP_Calculator-<version>.wotmod. The version
             is VERSION in ap_calculator/debug.py (the single source of truth);
             src/meta.xml's <version> is rewritten to match before staging.
             Does not touch a WoT install.
  uninstall  Remove whatever `deploy` put into res_mods/<version>/, derived from
             the same source tree so the file list never goes stale.

Examples:

  python build/build.py deploy --wot-root "C:/Games/World_of_Tanks_NA"
  python build/build.py deploy --version 2.4.1.0 --python27 "C:/Python27/python.exe"
  python build/build.py package
  python build/build.py uninstall --wot-root "C:/Games/World_of_Tanks_NA"

Paths are resolved relative to this file, so it can be run from anywhere.
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
SRC_RES_DIR = os.path.join(SRC_DIR, "res")
META_SRC = os.path.join(SRC_DIR, "meta.xml")
VERSION_SRC = os.path.join(
    SRC_RES_DIR, "scripts", "client", "ap_calculator", "debug.py"
)
BIN_DIR = os.path.join(REPO_ROOT, "bin")
STAGE_DIR = os.path.join(BIN_DIR, "package")
OUT_DIR = os.path.join(BIN_DIR, "wotmods")

DEFAULT_CLIENT_VERSION = "2.4.1.0"
DEFAULT_WOT_ROOT = r"C:\Program Files\World_of_Tanks_NA" if os.name == "nt" else None
PYTHON27_CANDIDATES = ("python27", "python2.7", "python2")
DEFAULT_PYTHON27 = r"C:\Program Files\Python27\python.exe" if os.name == "nt" else None

# --- what ships ------------------------------------------------------------------
# Every entry is relative to src/res/ and lands at the same relative path under
# res_mods/<version>/ (deploy) or res/ inside the .wotmod (package) -- the one
# table all three subcommands read, so they can't drift apart.

# Directories whose *.py files are compiled (recursively) to .pyc.
PY_ROOTS = (
    "scripts/client/gui/mods",
    "scripts/client/ap_calculator",
)

# Files, or directories copied recursively, shipped as-is.
ASSETS = (
    "gui/AP_Calculator_2/gameface",
    "gui/AP_Calculator_2/tooltips",
    "gui/AP_Calculator_2/translations",
    "gui/gen_resources/ap_calculator_2.json",
)

# Left behind in a WoT install by releases before 2.2.0, which registered the
# view through OpenWG's res_map instead of gen_resources. Relative to wot-root
# (not version-scoped); removed by deploy and uninstall.
LEGACY_FILES = ("mods/configs/res_map/APBattleView.json",)

# Runs under the Python 2.7 interpreter: reads [[src, cfile, dfile], ...] as
# JSON from stdin and compiles each one, refusing to run on any other version.
_COMPILE_SCRIPT = """
import json, py_compile, sys
if sys.version_info[:2] != (2, 7):
    sys.stderr.write('expected Python 2.7, got %s\\n' % sys.version.split()[0])
    sys.exit(3)
for src, cfile, dfile in json.load(sys.stdin):
    try:
        py_compile.compile(src, cfile, dfile, True)
    except py_compile.PyCompileError as e:
        sys.stderr.write(e.msg + '\\n')
        sys.exit(1)
"""


class BuildError(Exception):
    pass


def log(message):
    print(message, flush=True)


# --- helpers -----------------------------------------------------------------------


def rel_files(root, suffix=None):
    """Yield paths relative to src/res/ of every file under the src/res/-relative
    `root` (a file or a directory), sorted, optionally filtered by suffix."""
    full = os.path.join(SRC_RES_DIR, root)
    if os.path.isfile(full):
        yield root
        return
    if not os.path.isdir(full):
        raise BuildError("Missing source: " + full)
    for dirpath, dirnames, filenames in os.walk(full):
        dirnames.sort()
        for name in sorted(filenames):
            if suffix is None or name.endswith(suffix):
                rel = os.path.relpath(os.path.join(dirpath, name), SRC_RES_DIR)
                yield rel.replace(os.sep, "/")


def py_sources():
    sources = [rel for root in PY_ROOTS for rel in rel_files(root, ".py")]
    if not sources:
        raise BuildError("No .py files found under " + ", ".join(PY_ROOTS))
    return sources


def asset_files():
    return [rel for root in ASSETS for rel in rel_files(root)]


def to_pyc(rel):
    return rel[: -len(".py")] + ".pyc"


def find_python27(explicit):
    if explicit:
        return explicit
    for name in PYTHON27_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    if DEFAULT_PYTHON27 and os.path.isfile(DEFAULT_PYTHON27):
        return DEFAULT_PYTHON27
    raise BuildError(
        "No Python 2.7 found on PATH (tried {}) or at {}. Pass --python27 /path/to/python2.7.".format(
            ", ".join(PYTHON27_CANDIDATES), DEFAULT_PYTHON27
        )
    )


def compile_all(python27, dest_root):
    """Compile every shipped .py with Python 2.7 into dest_root at the same
    relative path. Compiles into a temp dir first, so a syntax error anywhere
    leaves dest_root untouched. Returns the .pyc paths relative to dest_root."""
    sources = py_sources()
    tmp = tempfile.mkdtemp(prefix="ap_calc_build_")
    try:
        # dfile is the in-client path, so tracebacks name the file as the game
        # sees it rather than a path on this machine.
        jobs = [
            [os.path.join(SRC_RES_DIR, rel), os.path.join(tmp, to_pyc(rel)), rel]
            for rel in sources
        ]
        for _src, cfile, _dfile in jobs:
            os.makedirs(os.path.dirname(cfile), exist_ok=True)
        log("Compiling {} modules with {} ...".format(len(jobs), python27))
        try:
            result = subprocess.run(
                [python27, "-c", _COMPILE_SCRIPT],
                input=json.dumps(jobs).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError as e:
            raise BuildError("Could not run '{}': {}".format(python27, e))
        if result.returncode != 0:
            raise BuildError(
                "Compile failed (exit {}):\n{}".format(
                    result.returncode, result.stderr.decode("utf-8", "replace").strip()
                )
            )

        pycs = [to_pyc(rel) for rel in sources]
        for pyc in pycs:
            dest = os.path.join(dest_root, pyc)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            # A stale .py (or old .pyc) next to the fresh file can shadow it and
            # silently run old code.
            stale_py = dest[: -len(".pyc")] + ".py"
            if os.path.exists(stale_py):
                os.remove(stale_py)
                log("  removed stale: " + os.path.relpath(stale_py, dest_root))
            shutil.copyfile(os.path.join(tmp, pyc), dest)
            log("  " + pyc)
        return pycs
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def copy_assets(dest_root):
    log("Copying assets ...")
    for rel in asset_files():
        dest = os.path.join(dest_root, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(SRC_RES_DIR, rel), dest)
        log("  " + rel)


def remove_file(path, label):
    if os.path.isfile(path):
        os.remove(path)
        log("  removed: " + label)
        return True
    return False


def prune_empty_dirs(path, stop):
    """Remove `path` and then each parent while empty, never removing `stop`
    or anything above it."""
    stop = os.path.abspath(stop)
    path = os.path.abspath(path)
    while path != stop and path.startswith(stop + os.sep):
        if not os.path.isdir(path) or os.listdir(path):
            return
        os.rmdir(path)
        log("  removed empty directory: " + path)
        path = os.path.dirname(path)


def remove_legacy_files(wot_root):
    for rel in LEGACY_FILES:
        path = os.path.join(wot_root, rel)
        if remove_file(path, rel + " (pre-2.2.0 res_map registration)"):
            prune_empty_dirs(os.path.dirname(path), wot_root)


def mod_version():
    """VERSION from debug.py -- the single source of truth for the mod version.
    Read as text rather than imported: debug.py is Python 2.7 client code."""
    with io.open(VERSION_SRC, encoding="utf-8") as fh:
        match = re.search(r"""^VERSION\s*=\s*["']([^"']+)["']""", fh.read(), re.M)
    if not match or not match.group(1).strip():
        raise BuildError('No VERSION = "<version>" line in ' + VERSION_SRC)
    return match.group(1).strip()


def sync_meta_version(version):
    """Rewrite <version> in src/meta.xml to `version` if it differs. Edits the
    text in place rather than round-tripping through an XML parser, so the
    comments and line endings survive."""
    with io.open(META_SRC, encoding="utf-8", newline="") as fh:
        text = fh.read()
    match = re.search(r"<version>(.*?)</version>", text, re.S)
    if not match:
        raise BuildError("No <version> in " + META_SRC)
    old = match.group(1).strip()
    if old == version:
        return
    text = text[: match.start(1)] + version + text[match.end(1) :]
    with io.open(META_SRC, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    log("Updated meta.xml <version>: {} -> {}".format(old, version))


def resolve_wot_root(args):
    if not args.wot_root:
        raise BuildError("Pass --wot-root (the World of Tanks install directory).")
    if not os.path.isdir(args.wot_root):
        raise BuildError(
            "WoT install not found: {} (pass --wot-root)".format(args.wot_root)
        )
    return args.wot_root


def zip_dir(source, destination):
    """ZIP_STORED archive of `source`'s contents: explicit directory entries,
    forward-slash names and fixed permissions (same shape OpenWG's own packager
    writes), plus a fixed timestamp and sorted order so identical inputs give
    byte-identical archives."""
    stamp = (2020, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_STORED) as zf:
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames.sort()
            rel_dir = os.path.relpath(dirpath, source).replace(os.sep, "/")
            if rel_dir != ".":
                info = zipfile.ZipInfo(rel_dir + "/", stamp)
                info.external_attr = 0o40775 << 16 | 0x10
                zf.writestr(info, b"")
            for name in sorted(filenames):
                arcname = name if rel_dir == "." else rel_dir + "/" + name
                info = zipfile.ZipInfo(arcname, stamp)
                info.external_attr = 0o100666 << 16
                with open(os.path.join(dirpath, name), "rb") as fh:
                    zf.writestr(info, fh.read())


# --- subcommands -----------------------------------------------------------------


def cmd_deploy(args):
    wot_root = resolve_wot_root(args)
    python27 = find_python27(args.python27)
    dest_root = os.path.join(wot_root, "res_mods", args.version)
    log("Deploying into " + dest_root)
    compile_all(python27, dest_root)
    copy_assets(dest_root)
    remove_legacy_files(wot_root)
    log("")
    log("Done. Start a new battle to pick up the changes (restart the client if")
    log("a change doesn't seem to take effect).")


def cmd_package(args):
    python27 = find_python27(args.python27)
    version = mod_version()
    sync_meta_version(version)
    out_file = os.path.join(
        OUT_DIR, "pademinune-AP_Calculator-{}.wotmod".format(version)
    )

    # Wiped every run so a package never mixes fresh output with leftovers from
    # a previous src layout.
    if os.path.isdir(STAGE_DIR):
        shutil.rmtree(STAGE_DIR)
    res_dir = os.path.join(STAGE_DIR, "res")
    os.makedirs(res_dir)
    os.makedirs(OUT_DIR, exist_ok=True)

    compile_all(python27, res_dir)
    copy_assets(res_dir)
    # meta.xml sits at the archive root, next to res/, not inside it.
    shutil.copyfile(META_SRC, os.path.join(STAGE_DIR, "meta.xml"))

    if os.path.exists(out_file):
        os.remove(out_file)
    zip_dir(STAGE_DIR, out_file)
    log("Packaged: " + out_file)


def cmd_uninstall(args):
    wot_root = resolve_wot_root(args)
    dest_root = os.path.join(wot_root, "res_mods", args.version)
    log("Removing from " + dest_root)
    shipped = [to_pyc(rel) for rel in py_sources()] + asset_files()
    for rel in shipped:
        path = os.path.join(dest_root, rel)
        if remove_file(path, rel):
            prune_empty_dirs(os.path.dirname(path), dest_root)
    remove_legacy_files(wot_root)
    log("")
    log("Done.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Run `%(prog)s <subcommand> -h` for that subcommand's options.",
    )
    sub = parser.add_subparsers(dest="command", metavar="{deploy,package,uninstall}")
    sub.required = True

    def add_wot_args(p):
        p.add_argument(
            "--wot-root",
            default=DEFAULT_WOT_ROOT,
            help="World of Tanks install directory"
            + (" (default: %(default)s)" if DEFAULT_WOT_ROOT else " (required)"),
        )
        p.add_argument(
            "--version",
            default=DEFAULT_CLIENT_VERSION,
            help="client version folder under res_mods/ (default: %(default)s)",
        )

    def add_python27_arg(p):
        p.add_argument(
            "--python27",
            help="Python 2.7 interpreter used to compile (default: first of {} on PATH, "
            "else {})".format(", ".join(PYTHON27_CANDIDATES), DEFAULT_PYTHON27),
        )

    p = sub.add_parser("deploy", help="compile + copy loose files into a WoT install")
    add_wot_args(p)
    add_python27_arg(p)
    p.set_defaults(func=cmd_deploy)

    p = sub.add_parser("package", help="build bin/wotmods/<name>.wotmod")
    add_python27_arg(p)
    p.set_defaults(func=cmd_package)

    p = sub.add_parser("uninstall", help="remove what deploy put into a WoT install")
    add_wot_args(p)
    p.set_defaults(func=cmd_uninstall)

    args = parser.parse_args(argv)
    try:
        args.func(args)
    except BuildError as e:
        sys.exit("error: {}".format(e))
    except PermissionError as e:
        sys.exit(
            "error: {}\nIs the WoT client still running (it locks its files), or does "
            "this location need administrator rights?".format(e)
        )


if __name__ == "__main__":
    main()
