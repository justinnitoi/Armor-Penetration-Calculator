"""Loads the real stock gun_marker_ctrl.py, so tests run the mod against the
game's own shot-result code instead of an imitation of it.

The file comes from the decompiled client at izeberg/wot-src, pinned to
WOT_SRC_COMMIT, and is downloaded into tests/.cache/ (gitignored: Wargaming's
code is never committed here). After a client update, bump WOT_SRC_COMMIT to the
new wot-src commit and rerun the tests: failures in test_shot_analysis then show
where the mirrored logic in core/shot_analysis.py needs re-porting.

Run this file directly to (re)download: python tests/stock.py
"""

import imp
import os
import sys
import types

# wot-src NA branch, "v.2.4.1.0 #979"
WOT_SRC_COMMIT = "95c758ac0d7ddba41ab3a32b4f5b36cba2493583"
_PATH_IN_REPO = "sources/res/scripts/client/AvatarInputHandler/gun_marker_ctrl.py"
_URL = "https://raw.githubusercontent.com/izeberg/wot-src/{}/{}"

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "gun_marker_ctrl-{}.py".format(WOT_SRC_COMMIT[:12]))


def fetch():
    """Returns the path of the cached stock file, downloading it if needed.
    Returns None if it isn't cached and can't be downloaded."""
    if os.path.isfile(CACHE_FILE):
        return CACHE_FILE
    import urllib2

    try:
        data = urllib2.urlopen(_URL.format(WOT_SRC_COMMIT, _PATH_IN_REPO), timeout=30).read()
    except Exception as e:
        sys.stderr.write("Could not download stock gun_marker_ctrl.py: {}\n".format(e))
        return None
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(CACHE_FILE, "wb") as f:
        f.write(data)
    return CACHE_FILE


# --- auto-stubs ----------------------------------------------------------------


class _StubMeta(type):
    """Any missing attribute of a stub class is another stub class, so module
    level code like `aih_global_binding.BINDING_ID.CTRL_MODE_NAME` or
    `class X(CallbackDelayer)` just works."""

    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)
        stub = _stub_class(name)
        setattr(cls, name, stub)
        return stub


class _StubBase(object):
    __metaclass__ = _StubMeta

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _stub_class(name)()

    def __call__(self, *args, **kwargs):
        return _stub_class("result")()


def _stub_class(name):
    return _StubMeta(str(name), (_StubBase,), {})


class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        stub = _stub_class(name)
        setattr(self, name, stub)
        return stub


class _AutoStubFinder(object):
    """Serves a stub module for any import that neither a fake nor a real
    module on sys.path satisfies. Only active while load() runs."""

    def find_module(self, fullname, path=None):
        if fullname in sys.modules:
            return None
        if "." not in fullname:
            try:
                imp.find_module(fullname)
                return None  # a real (e.g. stdlib) module exists
            except ImportError:
                return self
        # Only submodules of fake/stub packages (whose __path__ is empty). A
        # real package's lookups -- including Python 2's implicit relative
        # imports like logging -> "logging.time" -- must fall through.
        parent = sys.modules.get(fullname.rpartition(".")[0])
        if parent is None or getattr(parent, "__path__", None):
            return None
        return self

    def load_module(self, fullname):
        module = _StubModule(fullname)
        module.__path__ = []
        module.__loader__ = self
        sys.modules[fullname] = module
        parent_name, _, child = fullname.rpartition(".")
        if parent_name and parent_name in sys.modules:
            setattr(sys.modules[parent_name], child, module)
        return module


def load():
    """Imports the stock file as AvatarInputHandler.gun_marker_ctrl (fakes must
    already be installed). Returns the module, or None if unavailable."""
    name = "AvatarInputHandler.gun_marker_ctrl"
    if name in sys.modules:
        return sys.modules[name]
    path = fetch()
    if path is None:
        return None
    finder = _AutoStubFinder()
    sys.meta_path.append(finder)
    try:
        module = imp.load_source(name, path)
    finally:
        sys.meta_path.remove(finder)
    sys.modules["AvatarInputHandler"].gun_marker_ctrl = module
    return module


def _download(commit):
    import urllib2

    return urllib2.urlopen(_URL.format(commit, _PATH_IN_REPO), timeout=30).read()


def _class_source(source, class_name="_CrosshairShotResults"):
    """The lines of one top-level class, up to the next top-level statement."""
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("class {}(".format(class_name)))
    end = start + 1
    while end < len(lines) and (not lines[end] or lines[end][0] in " \t"):
        end += 1
    return lines[start:end]


def diff(new_commit="NA"):
    """Prints how _CrosshairShotResults changed between WOT_SRC_COMMIT and
    new_commit (a sha, or a branch such as NA for the latest client)."""
    import difflib

    with open(fetch(), "rb") as f:
        old = _class_source(f.read())
    new = _class_source(_download(new_commit))
    changes = list(
        difflib.unified_diff(old, new, WOT_SRC_COMMIT[:12], new_commit, lineterm="")
    )
    print("\n".join(changes) if changes else "_CrosshairShotResults is unchanged.")


if __name__ == "__main__":
    # python tests/stock.py               download the pinned file
    # python tests/stock.py diff [sha]    diff the stock class against a newer commit
    if sys.argv[1:2] == ["diff"]:
        diff(*sys.argv[2:3])
    else:
        print(fetch() or "download failed")
