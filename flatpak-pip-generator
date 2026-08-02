#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#    "requirements-parser<1.0.0,>=0.11.0",
#    "packaging>=23.0",
# ]
# ///

__license__ = "MIT"

import sys

if sys.version_info < (3, 10):
    sys.stderr.write("Error: This script requires Python 3.10 or higher.\n")
    sys.exit(1)

import textwrap
import platform
import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.request
from collections import OrderedDict
from collections.abc import Iterator
from contextlib import suppress
from typing import Any, TextIO, Callable, NoReturn
import operator
from packaging.version import Version
from packaging.tags import Tag
from typing import cast

try:
    import requirements
except ImportError:
    sys.exit("Please install the 'requirements-parser' module")

ALLOW_RESTR_MODULES = (
    os.environ.get("FLATPAK_PIP_GENERATOR_ALLOW_RESTRICTED_MODULES", "0") == "1"
)

ARTIFACT_POLICIES = ("universal", "platform", "sdist")


def parse_artifact_policy(s: str) -> tuple[str, str]:
    module, sep, policy = s.partition("=")
    module = module.strip()
    policy = policy.strip()

    if not (sep and module and policy in ARTIFACT_POLICIES):
        raise argparse.ArgumentTypeError(f"Invalid artifact policy {s!r}")

    return module, policy


def parse_comma_list(s: str) -> list[str]:
    return [x.strip().lower() for x in s.split(",") if x.strip()]


description = textwrap.dedent("""\
    flatpak-pip-generator

    Tool to generate flatpak-builder manifests for Python modules
""")
parser = argparse.ArgumentParser(
    description=description,
    formatter_class=argparse.RawTextHelpFormatter,
    usage=argparse.SUPPRESS,
    add_help=False,
)
parser.add_argument(
    "-h",
    "--help",
    action="help",
    help="Show this help message and exit",
)
parser.add_argument("packages", nargs="*")
parser.add_argument(
    "--python2", action="store_true", help="Look for a Python 2 package"
)
parser.add_argument(
    "--cleanup", choices=["scripts", "all"], help="Select what to clean up after build"
)
parser.add_argument(
    "--requirements-file",
    "-r",
    metavar="",
    help="Specify requirements.txt file. Cannot be used with pyproject file.",
)
parser.add_argument(
    "--pyproject-file",
    metavar="",
    help="Specify pyproject.toml file. Cannot be used with requirements file.",
)
parser.add_argument(
    "--optdep-groups",
    type=parse_comma_list,
    default=[],
    metavar="",
    help="Comma-separated optional dependency groups to include. Can only be used with pyproject file.",
)
parser.add_argument(
    "--build-only",
    action="store_const",
    dest="cleanup",
    const="all",
    help="Clean up all files after build",
)
parser.add_argument(
    "--build-isolation",
    action="store_true",
    default=False,
    help=(
        "Do not disable build isolation. "
        "Mostly useful on pip that doesn't "
        "support the feature."
    ),
)
parser.add_argument(
    "--ignore-installed",
    type=parse_comma_list,
    metavar="",
    default=[],
    help="Comma-separated list of package names for which pip "
    "should ignore already installed packages. Useful when "
    "the package is installed in the SDK but not in the "
    "runtime.",
)
parser.add_argument(
    "--checker-data",
    action="store_true",
    help='Include x-checker-data in output for the "Flatpak External Data Checker"',
)
parser.add_argument("--output", "-o", metavar="", help="Specify output file name")
parser.add_argument(
    "--runtime",
    metavar="",
    help=(
        "Specify a flatpak to run pip inside of a sandbox, "
        "ensures python version compatibility. Format: $RUNTIME_ID//$RUNTIME_BRANCH"
    ),
)
parser.add_argument(
    "--yaml", action="store_true", help="Use YAML as output format instead of JSON"
)
parser.add_argument(
    "--ignore-errors",
    action="store_true",
    help="Ignore errors when downloading packages",
)
parser.add_argument(
    "--ignore-pkg",
    type=parse_comma_list,
    default=[],
    metavar="",
    help=(
        "Comma-separated list of packages to ignore when generating the manifest. "
        "Include version constraints if present "
        "(e.g. --ignore-pkg 'foo>=3.0.0,baz>=21.0')."
    ),
)
parser.add_argument(
    "--prefer-wheels",
    metavar="",
    type=parse_comma_list,
    default=[],
    help="Comma-separated list of packages for which platform wheels should be preferred over sdists",
)

parser.add_argument(
    "--wheel-arches",
    metavar="",
    type=parse_comma_list,
    help="Comma-separated list of architectures for which platform wheels should be generated (default: x86_64,aarch64)",
)
parser.add_argument(
    "--artifact-policy",
    dest="artifact_policies",
    metavar="",
    action="append",
    default=[],
    type=parse_artifact_policy,
    help=argparse.SUPPRESS,
)

opts = parser.parse_args()


def normalize_name(name: str) -> str:
    return re.sub(r"[-_]+", "-", name.lower())


artifact_policy_map: dict[str, str] = {}

for raw_name, policy in opts.artifact_policies:
    norm = normalize_name(raw_name.lower())
    if norm in artifact_policy_map and artifact_policy_map[norm] != policy:
        sys.exit(f"Conflicting artifact policies for {raw_name!r}")
    artifact_policy_map[norm] = policy

policy_platform_pkgs = {n for n, p in artifact_policy_map.items() if p == "platform"}

if opts.runtime:
    parts = opts.runtime.split("//", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        sys.exit("Runtime argument must be in the format: $RUNTIME_ID//$RUNTIME_BRANCH")

DEFAULT_WHEEL_ARCHES = ["x86_64", "aarch64"]

if opts.prefer_wheels:
    if not opts.runtime:
        sys.exit(
            "--prefer-wheels requires --runtime to ensure correct platform wheel selection"
        )

if opts.wheel_arches:
    DEFAULT_WHEEL_ARCHES = opts.wheel_arches

if opts.requirements_file and opts.pyproject_file:
    sys.exit("Can't use both requirements and pyproject files at the same time")

if opts.requirements_file and opts.optdep_groups:
    sys.exit("Can only use optional dependency groups with pyproject file")

if opts.pyproject_file:
    try:
        from tomllib import load as toml_load
    except ModuleNotFoundError:
        try:
            from tomli import load as toml_load  # type: ignore
        except ModuleNotFoundError:
            sys.exit("Please install the 'tomli' module")

if opts.ignore_pkg and not (opts.requirements_file or opts.pyproject_file):
    sys.exit("--ignore-pkg can only be used with requirements or pyproject file")

if opts.yaml:
    try:
        import yaml
    except ImportError:
        sys.exit("Please install the 'PyYAML' module")

_PYPI_CACHE: dict[tuple[str, str], list[dict]] = {}


def get_flatpak_runtime_scope(runtime: str) -> str:
    for scope in ("--user", "--system"):
        try:
            subprocess.run(
                ["flatpak", "info", scope, runtime],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return scope
        except subprocess.CalledProcessError:
            continue
    sys.exit(f"Runtime {runtime} not found for user or system")


runtime_scope = get_flatpak_runtime_scope(opts.runtime) if opts.runtime else None


def get_runtime_arch() -> str:
    cmd = [
        "flatpak",
        "info",
        runtime_scope,
        "-r",
        opts.runtime,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        if line.startswith("runtime/"):
            parts = line.split("/")
            if len(parts) >= 3:
                return parts[2]
    raise RuntimeError(f"Failed to determine architecture for runtime {opts.runtime}")


runtime_tags_cache: dict[str, set[Tag] | None] = {}


def get_platform_tags_from_runtime(arch: str) -> set[Tag] | None:
    if arch in runtime_tags_cache:
        return runtime_tags_cache[arch]
    cmd = [
        "flatpak",
        f"--arch={arch}",
        runtime_scope,
        "--devel",
        "--command=python3",
        "run",
        opts.runtime,
        "-c",
        (
            "import json; "
            "from packaging import tags; "
            "print(json.dumps([str(t) for t in tags.sys_tags()]))"
        ),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        tags_list = [Tag(*t.split("-")) for t in json.loads(result.stdout)]
        runtime_tags_cache[arch] = set(tags_list)
        return runtime_tags_cache[arch]
    except subprocess.CalledProcessError:
        runtime_tags_cache[arch] = None
        return None


SUPPORTED_TAG_SET: set[Tag] | None = None

effective_prefer_wheels = set(opts.prefer_wheels) | policy_platform_pkgs

if effective_prefer_wheels:
    if not opts.runtime:
        sys.exit(
            "--prefer-wheels or --artifact-policy with 'platform' policy"
            + " requires --runtime to ensure correct platform wheel"
            + " selection"
        )
    runtime_arch = get_runtime_arch()
    platform_tags = get_platform_tags_from_runtime(runtime_arch)

    if not platform_tags:
        sys.exit(
            "Failed to obtain platform tags from runtime. Cannot select platform wheels."
        )

    for arch in DEFAULT_WHEEL_ARCHES:
        if arch == runtime_arch:
            continue

        if get_platform_tags_from_runtime(arch) is None:
            print(
                f"\nWarning: Runtime for arch '{arch}' is not installed",
                f"Platform tags will be extrapolated from the '{runtime_arch}' runtime.\n",
                file=sys.stderr,
            )

    SUPPORTED_TAG_SET = set(platform_tags)

    assert SUPPORTED_TAG_SET is not None


def make_source(
    file_info: dict[str, str | dict[str, str]], only_arches: list[str] | None = None
) -> dict[str, str | list[str] | dict[str, str]]:
    url = file_info["url"]
    digests = file_info["digests"]
    filename = file_info["filename"]

    if not isinstance(url, str):
        raise TypeError("file_info['url'] must be str")
    if not isinstance(digests, dict):
        raise TypeError("file_info['digests'] must be dict")
    if not isinstance(filename, str):
        raise TypeError("file_info['filename'] must be str")

    source: dict[str, str | list[str] | dict[str, str]] = {}

    source["type"] = "file"
    source["url"] = url
    source["sha256"] = digests["sha256"]

    if only_arches:
        source["only-arches"] = only_arches

    if opts.checker_data:
        pkg_name = normalize_name(get_package_name(filename))
        checker: dict[str, str] = {"type": "pypi", "name": pkg_name}
        if filename.endswith(".whl"):
            checker["packagetype"] = "bdist_wheel"
        source["x-checker-data"] = checker

    return source


def parse_req_hashes(raw_lines: list[str]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for line in raw_lines:
        hashes = set(re.findall(r"--hash=sha256:([a-f0-9]+)", line))
        if not hashes:
            continue
        name_part = re.split(r"[=\s;]", line.split("--hash")[0].strip())[0]
        if not name_part:
            continue
        normalized = normalize_name(name_part)
        result.setdefault(normalized, set()).update(hashes)
    return result


def get_req_name(s: str) -> str:
    return re.split(r"[<>=!~\[\s]", s, maxsplit=1)[0].strip().casefold()


def resolve_package_sources(
    name: str,
    version: str,
    candidates: list[str],
    is_preferred: bool,
    known_hashes: set[str] | None = None,
    policy: str | None = None,
) -> tuple[list[dict], list[str]]:
    sources_out: list[dict] = []
    pypi_files: list[dict] | None = None

    def fetch_pypi_files(name: str, version: str) -> list[dict]:
        key = (name, version)
        if key in _PYPI_CACHE:
            return _PYPI_CACHE[key]
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        print(f"Fetching PyPI metadata for {name}=={version}")
        with urllib.request.urlopen(url) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))["urls"]
        _PYPI_CACHE[key] = data
        return data

    def get_py_tags(filename: str) -> list[str]:
        return filename[:-4].split("-")[-3].split(".")

    def is_py2_only_wheel(filename: str) -> bool:
        if not filename.endswith(".whl"):
            return False
        py_tags = get_py_tags(filename)
        return any(t.startswith(("py2", "cp2")) for t in py_tags) and not any(
            t.startswith(("py3", "cp3")) for t in py_tags
        )

    def is_py3_only_wheel(filename: str) -> bool:
        if not filename.endswith(".whl"):
            return False
        py_tags = get_py_tags(filename)
        return any(t.startswith(("py3", "cp3")) for t in py_tags) and not any(
            t.startswith(("py2", "cp2")) for t in py_tags
        )

    def get_pypi_files() -> list[dict]:
        nonlocal pypi_files
        if pypi_files is None:
            all_files = fetch_pypi_files(name, version)
            pypi_hashes = {f["digests"]["sha256"] for f in all_files}
            if known_hashes:
                if known_hashes != pypi_hashes:
                    print(
                        f"\nWARNING: Requirements file does not include hashes for all "
                        f"artifacts for {name}=={version}. Resolution may be"
                        "restricted.\n"
                    )
                missing = known_hashes - pypi_hashes
                if missing:
                    sys.exit(
                        f"ERROR: Hash(es) {missing} for {name}=={version} "
                        "not found on PyPI. Aborting."
                    )
                pypi_files = [
                    f for f in all_files if f["digests"]["sha256"] in known_hashes
                ]
            else:
                pypi_files = all_files
        return pypi_files

    files = get_pypi_files()

    if opts.python2:
        files = [f for f in files if not is_py3_only_wheel(f["filename"])]
    else:
        files = [f for f in files if not is_py2_only_wheel(f["filename"])]

    def is_universal(filename: str) -> bool:
        return filename.endswith(".whl") and filename[:-4].split("-")[-1] == "any"

    def is_platform_wheel(filename: str) -> bool:
        return filename.endswith(".whl") and filename[:-4].split("-")[-1] != "any"

    def adapt_tags_for_arch(tag_set: set[Tag], arch: str) -> set[Tag]:
        out = set()
        for t in tag_set:
            plat = t.platform
            for known_arch in DEFAULT_WHEEL_ARCHES:
                if plat.endswith(f"_{known_arch}"):
                    plat = plat[: -len(known_arch)] + arch
                    break
            out.add(Tag(t.interpreter, t.abi, plat))
        return out

    def get_tags_for_arch(arch: str) -> set[Tag]:
        assert SUPPORTED_TAG_SET is not None
        runtime_tags = get_platform_tags_from_runtime(arch)
        if runtime_tags is not None:
            return runtime_tags
        return adapt_tags_for_arch(SUPPORTED_TAG_SET, arch)

    def runtime_python_ver(tag_set: set[Tag]) -> int | None:
        for t in tag_set:
            if (
                t.interpreter.startswith("cp")
                and t.abi.startswith("cp")
                and t.interpreter == t.abi
            ):
                with suppress(ValueError):
                    return int(t.interpreter[2:])
        return None

    def wheel_priority(filename: str, arch_tag_set: set[Tag]) -> int:
        parts = filename[:-4].split("-")
        pytags = parts[-3].split(".")
        abitags = parts[-2].split(".")
        platformtags = parts[-1].split(".")
        wheel_tags = {
            Tag(py, abi, plat)
            for py in pytags
            for abi in abitags
            for plat in platformtags
        }
        return len(wheel_tags & arch_tag_set)

    def arch_platform_candidates(arch: str, py_ver: int) -> list[dict]:
        def is_arch_match(platform_tag: str) -> bool:
            return platform_tag != "any" and arch in platform_tag

        def parse_wheel_ver(py: str) -> int | None:
            if not py.startswith("cp"):
                return None
            with suppress(ValueError):
                return int(py[2:])
            return None

        def is_abi_free(abitags: list[str]) -> bool:
            return all(abi == "none" for abi in abitags)

        def strict_compat(pytags: list[str], abitags: list[str], py_ver: int) -> bool:
            if is_abi_free(abitags):
                return True
            for py, abi in zip(pytags, abitags):
                ver = parse_wheel_ver(py)
                if ver is None:
                    continue
                if ver == py_ver:
                    return True
                if abi == "abi3" and ver <= py_ver:
                    return True
            return False

        def relaxed_compat(pytags: list[str], abitags: list[str], py_ver: int) -> bool:
            if is_abi_free(abitags):
                return True
            for py in pytags:
                ver = parse_wheel_ver(py)
                if ver is not None and ver <= py_ver:
                    return True
            return False

        def collect(compat_fn) -> list[dict]:
            result = []
            for f in files:
                fn = f["filename"]
                if not fn.endswith(".whl"):
                    continue
                parts = fn[:-4].split("-")
                if not is_arch_match(parts[-1]):
                    continue
                if py_ver is None or compat_fn(
                    parts[-3].split("."), parts[-2].split(".")
                ):
                    result.append(f)
            return result

        found = collect(lambda pytags, abitags: strict_compat(pytags, abitags, py_ver))
        if not found and py_ver is not None:
            found = collect(
                lambda pytags, abitags: relaxed_compat(pytags, abitags, py_ver)
            )
        return found

    def format_error(msg: str) -> str:
        if known_hashes:
            return f"{msg} (constrained by hashes in requirements file)"
        return msg

    def pkg_error(msg: str) -> str:
        return f"{name}: {format_error(msg)}"

    def policy_error(msg: str) -> NoReturn:
        sys.exit(f"ERROR: artifact-policy '{policy}' for {name!r}: {format_error(msg)}")

    def find_universal() -> dict[str, str | dict[str, str]] | None:
        return next((f for f in files if is_universal(f["filename"])), None)

    def find_sdist() -> dict[str, str | dict[str, str]] | None:
        return next((f for f in files if not f["filename"].endswith(".whl")), None)

    def resolve_platform_wheels(
        platform_policy: bool,
    ) -> tuple[
        list[dict[str, str | list[str] | dict[str, str]]],
        list[str],
    ]:
        assert SUPPORTED_TAG_SET is not None
        native_py_ver = runtime_python_ver(SUPPORTED_TAG_SET)

        out = []
        errs = []

        for arch in DEFAULT_WHEEL_ARCHES:
            arch_tags = get_tags_for_arch(arch)
            py_ver = runtime_python_ver(arch_tags) or native_py_ver

            if py_ver is None:
                msg = f"Unable to determine Python version for arch '{arch}'"
                if platform_policy:
                    policy_error(msg)
                errs.append(pkg_error(msg))
                continue

            arch_candidates = arch_platform_candidates(arch, cast(int, py_ver))

            if not arch_candidates:
                msg = f"No compatible platform wheel found for arch '{arch}'"
                if platform_policy:
                    policy_error(msg)
                errs.append(pkg_error(msg))
                continue

            wheel = max(
                arch_candidates,
                key=lambda f: wheel_priority(f["filename"], arch_tags),
            )
            out.append(make_source(wheel, only_arches=[arch]))

        return out, errs

    pypi_universal = find_universal()
    pypi_sdist = find_sdist()

    if policy == "universal":
        if not pypi_universal:
            policy_error("No universal wheel found on PyPI")
        return [make_source(pypi_universal)], []

    if policy == "sdist":
        if not pypi_sdist:
            policy_error("No sdist found on PyPI")
        return [make_source(pypi_sdist)], []

    if policy == "platform":
        sources_out, _ = resolve_platform_wheels(platform_policy=True)
        return sources_out, []

    if pypi_universal:
        return [make_source(pypi_universal)], []

    if not is_preferred:
        if pypi_sdist:
            return [make_source(pypi_sdist)], []

        if any(is_platform_wheel(f["filename"]) for f in files):
            return [], [f"__PLATFORM_ONLY__:{name}"]

        if known_hashes:
            return [], [pkg_error("No suitable source found on PyPI")]
        else:
            return [], [f"{name}: No suitable source found on PyPI"]

    sources_out, errors = resolve_platform_wheels(platform_policy=False)
    return sources_out, errors


def get_poetry_deps(pyproject_data: dict[str, Any]) -> list[str]:
    poetry_deps = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies")

    if not poetry_deps:
        return []

    def format_dependency_version(name: str, value: Any) -> str:
        sep, suffix = "@", ""
        dep_name = name

        if isinstance(value, dict):
            if version := value.get("version"):
                sep, val = "==", version
            elif git_url := value.get("git"):
                val = f"git+{git_url}" if not git_url.startswith("git@") else git_url
                if rev := value.get("branch") or value.get("rev") or value.get("tag"):
                    val += f"@{rev}"
                if subdir := value.get("subdirectory"):
                    val += f"#subdirectory={subdir}"
            elif path := value.get("path"):
                dep_name, sep, val = "", "", path
            elif url := value.get("url"):
                dep_name, sep, val = "", "", url
            else:
                dep_name, sep, val = name, "", ""

            if markers := value.get("markers"):
                suffix = f";{markers}"
        else:
            sep, val = "==", value

        if val.startswith("^"):
            sep, val = ">=", val[1:]
        elif val.startswith("~"):
            sep, val = "~=", val[1:]
        elif "<" in val or ">" in val:
            sep, val = "", val.replace(" ", "")

        return f"{dep_name}{sep}{val}{suffix}"

    return sorted(
        format_dependency_version(dep, val)
        for dep, val in poetry_deps.items()
        if dep != "python"
    )


def get_package_name(filename: str) -> str:
    if filename.endswith(("bz2", "gz", "xz", "zip")):
        segments = filename.split("-")
        if len(segments) == 2:
            return segments[0]
        return "-".join(segments[: len(segments) - 1])
    if filename.endswith("whl"):
        segments = filename.split("-")
        if len(segments) == 5:
            return segments[0]
        candidate = segments[: len(segments) - 4]
        # Some packages list the version number twice
        # e.g. PyQt5-5.15.0-5.15.0-cp35.cp36.cp37.cp38-abi3-manylinux2014_x86_64.whl
        if candidate[-1] == segments[len(segments) - 4]:
            return "-".join(candidate[:-1])
        return "-".join(candidate)
    raise Exception(
        f"Downloaded filename: {filename} does not end with bz2, gz, xz, zip, or whl"
    )


def get_file_version(filename: str) -> str:
    name = get_package_name(filename)
    segments = filename.split(name + "-")
    version = segments[1].split("-")[0]
    for ext in ["tar.gz", "whl", "tar.xz", "tar.gz", "tar.bz2", "zip"]:
        version = version.replace("." + ext, "")
    return version


def parse_continuation_lines(fin: TextIO) -> Iterator[str]:
    for raw_line in fin:
        line = raw_line.rstrip("\n")
        while line.endswith("\\"):
            try:
                line = line[:-1] + next(fin).rstrip("\n")
            except StopIteration:
                sys.exit(
                    "Requirements have a wrong number of line "
                    'continuation characters "\\"'
                )
        yield line


def fprint(string: str) -> None:
    separator = "=" * 72  # Same as `flatpak-builder`
    print(separator)
    print(string)
    print(separator)


def handle_req_env_markers(requirements_text: str) -> str:
    def handle_sys_platform(marker: str) -> bool:
        pattern = r'sys_platform\s*(==|!=)\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, marker, re.IGNORECASE):
            op, platform = match.group(1), match.group(2).lower()
            if (op == "==" and not platform.startswith("linux")) or (
                op == "!=" and platform.startswith("linux")
            ):
                return False
        return True

    def handle_platform_system(marker: str) -> bool:
        pattern = r'platform_system\s*(==|!=)\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, marker, re.IGNORECASE):
            op, system = match.group(1), match.group(2).lower()
            if (op == "==" and system != "linux") or (op == "!=" and system == "linux"):
                return False
        return True

    def handle_os_name(marker: str) -> bool:
        pattern = r'os_name\s*(==|!=)\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, marker, re.IGNORECASE):
            op, name = match.group(1), match.group(2).lower()
            if (op == "==" and name != "posix") or (op == "!=" and name == "posix"):
                return False
        return True

    def handle_implementation_name(marker: str) -> bool:
        pattern_impl_name = r'implementation_name\s*(==|!=)\s*["\']([^"\']+)["\']'
        pattern_platform_impl = (
            r'platform_python_implementation\s*(==|!=)\s*["\']([^"\']+)["\']'
        )

        current_impl_name = sys.implementation.name.lower()
        current_platform_impl = platform.python_implementation().lower()

        if current_impl_name != "cpython":
            print(
                f"WARNING: sys.implementation.name '{current_impl_name}' does not match fdsdk runtime",
                file=sys.stderr,
            )
        if current_platform_impl != "cpython":
            print(
                f"WARNING: platform.python_implementation() '{current_platform_impl}' "
                f"does not match fdsdk runtime",
                file=sys.stderr,
            )

        for match in re.finditer(pattern_impl_name, marker, re.IGNORECASE):
            op, expected = match.group(1), match.group(2).lower()
            if (op == "==" and expected != current_impl_name) or (
                op == "!=" and expected == current_impl_name
            ):
                return False

        for match in re.finditer(pattern_platform_impl, marker, re.IGNORECASE):
            op, expected = match.group(1), match.group(2).lower()
            if (op == "==" and expected != current_platform_impl) or (
                op == "!=" and expected == current_platform_impl
            ):
                return False

        return True

    def handle_platform_machine(marker: str) -> bool:
        pattern = r'platform_machine\s*(==|!=)\s*["\']([^"\']+)["\']'

        if re.search(pattern, marker, re.IGNORECASE):
            print(
                f"WARNING: Ignoring platform_machine marker: '{marker}'",
                file=sys.stderr,
            )

        return True

    def handle_version_markers(marker: str) -> bool:
        # https://peps.python.org/pep-0496/#version-numbers
        def format_full_version(info) -> str:
            version = f"{info.major}.{info.minor}.{info.micro}"
            if info.releaselevel != "final":
                version += info.releaselevel[0] + str(info.serial)
            return version

        MARKERS: dict[str, str] = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",  # MAJOR.MINOR, :3 breaks comparison
            "python_full_version": format_full_version(sys.version_info),
            "platform_version": platform.version(),
            "implementation_version": format_full_version(sys.implementation.version),
        }

        OPS: dict[str, Callable[[Version, Version], bool]] = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }

        PAT = (
            r"(python_version|python_full_version|platform_version|implementation_version)"
            r'\s*(==|!=|<=|>=|<|>)\s*["\']([^"\']+)["\']'
        )

        def to_ver(v: str) -> Version | None:
            for s in (v, v.split("-", 1)[0]):
                try:
                    return Version(s)
                except Exception:
                    pass
            print(f"WARNING: unable to parse version '{v}'", file=sys.stderr)
            return None

        for name, op, rhs in re.findall(PAT, marker):
            lhs = to_ver(MARKERS[name])
            rhs = to_ver(rhs)
            if lhs and rhs and not OPS[op](lhs, rhs):
                return False

        return True

    marker_handlers = (
        handle_sys_platform,
        handle_platform_system,
        handle_os_name,
        handle_implementation_name,
        handle_platform_machine,
    )

    filtered_lines = []
    ignored_lines = []

    for line in requirements_text.split("\n"):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            filtered_lines.append(line)
            continue

        if ";" in line:
            marker = line.split(";", 1)[1].strip()
            should_include = all(handler(marker) for handler in marker_handlers)
        else:
            should_include = True

        if should_include:
            filtered_lines.append(line)
        else:
            ignored_lines.append(line)

    if ignored_lines:
        print(f"Ignored packages: {ignored_lines}")

    return "\n".join(filtered_lines)


packages = []
req_hashes_by_pkg: dict[str, set[str]] = {}
ignore_pkg = {pkg.casefold() for pkg in opts.ignore_pkg}

if opts.requirements_file:
    requirements_file_input = os.path.expanduser(opts.requirements_file)
    try:
        with open(requirements_file_input) as in_req_file:
            raw_lines = list(parse_continuation_lines(in_req_file))
            req_hashes_by_pkg = parse_req_hashes(raw_lines)
            reqs_as_str = handle_req_env_markers(
                "\n".join(r.split("--hash")[0] for r in raw_lines)
            )
            py_version_regex = re.compile(r";.*python_version .+$")
            reqs_list = [
                py_version_regex.sub("", line) for line in reqs_as_str.splitlines()
            ]

            if ignore_pkg:
                reqs_list = [
                    line for line in reqs_list if get_req_name(line) not in ignore_pkg
                ]
                raw_lines = [
                    line for line in raw_lines if get_req_name(line) not in ignore_pkg
                ]
            packages = list(requirements.parse("\n".join(reqs_list)))
            with tempfile.NamedTemporaryFile(
                "w", delete=False, prefix="requirements."
            ) as temp_req_file:
                temp_req_file.write("\n".join(raw_lines))
                requirements_file_output = temp_req_file.name
    except FileNotFoundError as err:
        print(err)
        sys.exit(1)

elif opts.pyproject_file:
    pyproject_file = os.path.expanduser(opts.pyproject_file)
    with open(pyproject_file, "rb") as f:
        pyproject_data = toml_load(f)
    is_poetry = pyproject_data.get("tool", {}).get("poetry") is not None
    if is_poetry:
        dependencies = get_poetry_deps(pyproject_data)
    else:
        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        if opts.optdep_groups:
            pyproject_optdep_groups = {
                k.lower(): v
                for k, v in pyproject_data.get("project", {})
                .get("optional-dependencies", {})
                .items()
            }
            for group in opts.optdep_groups:
                if group not in pyproject_optdep_groups:
                    sys.exit(
                        f"Optional dependency group {group} not found in pyproject file"
                    )
                dependencies += pyproject_optdep_groups[group]

    if not dependencies:
        sys.exit("Pyproject file was specified but no dependencies were collected")

    build_system_requires = pyproject_data.get("build-system", {}).get("requires", [])
    if build_system_requires:
        dependencies.extend(build_system_requires)

    if ignore_pkg:
        dependencies = [
            dep for dep in dependencies if get_req_name(dep) not in ignore_pkg
        ]

    packages = list(requirements.parse(handle_req_env_markers("\n".join(dependencies))))

    with tempfile.NamedTemporaryFile(
        "w", delete=False, prefix="requirements."
    ) as req_file:
        req_file.write("\n".join(dependencies))
        requirements_file_output = req_file.name

elif opts.packages:
    filtered_packages_str = handle_req_env_markers("\n".join(opts.packages))
    packages = list(requirements.parse(filtered_packages_str))
    with tempfile.NamedTemporaryFile(
        "w", delete=False, prefix="requirements."
    ) as req_file:
        req_file.write(filtered_packages_str)
        requirements_file_output = req_file.name
elif not len(sys.argv) > 1:
    sys.exit("Please specify either packages or requirements file argument")
else:
    sys.exit("This option can only be used with requirements file")

PYQT_PACKAGES = {
    "pyqt-builder",
    "pyqt6-sip",
    "pyqt5-sip",
    "pyqt6-webengine",
    "pyqt5-webengine",
    "pyqt6",
    "pyqt5",
}

PYSIDE6_PACKAGES = {
    "pyside6",
    "pyside6-addons",
    "pyside6-essentials",
    "shiboken6",
}

if not ALLOW_RESTR_MODULES:
    for i in packages:
        name = i["name"].lower()
        if name in PYQT_PACKAGES:
            print(
                "Please use the baseapp https://github.com/flathub/com.riverbankcomputing.PyQt.BaseApp"
            )
            sys.exit(0)
        elif name in PYSIDE6_PACKAGES:
            print(
                "Please use the baseapp https://github.com/flathub/io.qt.PySide.BaseApp"
            )
            sys.exit(0)

with open(requirements_file_output) as in_req_file:
    use_hash = "--hash=" in in_req_file.read()

python_version = "2" if opts.python2 else "3"
pip_executable = "pip2" if opts.python2 else "pip3"
pip_base_args = [
    "--no-input",
    "--disable-pip-version-check",
]

if opts.runtime:
    flatpak_cmd = [
        "flatpak",
        runtime_scope,
        "--devel",
        "--share=network",
        f"--filesystem={tempfile.gettempdir()}",
        f"--command={pip_executable}",
        "run",
        opts.runtime,
    ]
    if opts.requirements_file and os.path.exists(requirements_file_output):
        prefix = os.path.realpath(requirements_file_output)
        flag = f"--filesystem={prefix}"
        flatpak_cmd.insert(1, flag)
else:
    flatpak_cmd = [pip_executable]

flatpak_cmd += pip_base_args

output_path = ""
output_package = ""

if opts.output:
    if os.path.isdir(opts.output):
        output_path = opts.output
    else:
        output_path = os.path.dirname(opts.output)
        output_package = os.path.basename(opts.output)

if not output_package:
    if opts.requirements_file:
        output_package = "python{}-{}".format(
            python_version,
            os.path.basename(opts.requirements_file).replace(".txt", ""),
        )
    elif len(packages) == 1:
        output_package = f"python{python_version}-{packages[0].name}"
    else:
        output_package = f"python{python_version}-modules"

output_filename = os.path.join(output_path, output_package)
suffix = ".yaml" if opts.yaml else ".json"
if not output_filename.endswith(suffix):
    output_filename += suffix

modules: list[dict[str, str | list[str] | list[dict[str, Any]]]] = []
vcs_modules: list[dict[str, str | list[str] | list[dict[str, Any]]]] = []
sources: dict[str, Any] = {}
unresolved_dependencies_errors = []
prefer_wheels_missing: list[str] = []
prefer_set = {normalize_name(p) for p in effective_prefer_wheels}

tempdir_prefix = f"pip-generator-{output_package}"
with tempfile.TemporaryDirectory(prefix=tempdir_prefix) as tempdir:
    pip_download = [
        *flatpak_cmd,
        "download",
        "--exists-action=i",
        "--dest",
        tempdir,
        "-r",
        requirements_file_output,
    ]
    if use_hash:
        pip_download.append("--require-hashes")

    fprint("Downloading sources")
    cmd = " ".join(pip_download)
    print(f'Running: "{cmd}"')
    try:
        subprocess.run(pip_download, check=True)
        os.remove(requirements_file_output)
    except subprocess.CalledProcessError:
        os.remove(requirements_file_output)
        print("Failed to download")
        print("Please fix the module manually in the generated file")
        if not opts.ignore_errors:
            print("Ignore the error by passing --ignore-errors")
            raise

        with suppress(FileNotFoundError):
            os.remove(requirements_file_output)

    grouped: dict[str, list[str]] = {}

    for filename in os.listdir(tempdir):
        name = get_package_name(filename)
        grouped.setdefault(name, []).append(filename)

    # Delete redundant sources, for vcs sources keeping zip
    for name, files_list in grouped.items():
        if len(files_list) > 1 and any(f.endswith(".zip") for f in files_list):
            for fname in files_list:
                if not fname.endswith(".zip"):
                    with suppress(FileNotFoundError):
                        os.remove(os.path.join(tempdir, fname))

    vcs_packages: dict[str, dict[str, str | None]] = {
        str(x.name): {"vcs": x.vcs, "revision": x.revision, "uri": x.uri}
        for x in packages
        if x.vcs and x.name
    }

    fprint("Obtaining hashes and urls")

    grouped = {}
    for filename in os.listdir(tempdir):
        name = get_package_name(filename)
        grouped.setdefault(name, []).append(filename)

    for name, candidates in grouped.items():
        if name in vcs_packages:
            uri = vcs_packages[name]["uri"]
            if not uri:
                raise ValueError(f"Missing URI for VCS package: {name}")
            revision = vcs_packages[name]["revision"]
            vcs = vcs_packages[name]["vcs"]
            if not vcs:
                raise ValueError(
                    f"Unable to determine VCS type for VCS package: {name}"
                )
            url = "https://" + uri.split("://", 1)[1]
            vcs_source: dict[str, Any] = {"type": vcs, "url": url}
            if revision:
                vcs_source["commit" if vcs != "svn" else "revision"] = revision
            sources[name] = {"source": [vcs_source], "vcs": True, "pypi": False}
        else:
            name_cf = normalize_name(name)
            version = get_file_version(candidates[0])
            is_preferred = name_cf in prefer_set
            pkg_policy = artifact_policy_map.get(name_cf)

            known_hashes = req_hashes_by_pkg.get(name_cf) if use_hash else None
            resolved, errors = resolve_package_sources(
                name_cf,
                version,
                candidates,
                is_preferred,
                known_hashes,
                policy=pkg_policy,
            )

            for error in errors:
                if error.startswith("__PLATFORM_ONLY__:"):
                    pkg = error.removeprefix("__PLATFORM_ONLY__:")
                    prefer_wheels_missing.append(pkg)
                    unresolved_dependencies_errors.append(
                        f"Only platform wheels are available for: {pkg}"
                    )
                else:
                    unresolved_dependencies_errors.append(error)

            if resolved:
                sources[name_cf] = {
                    "source": resolved,
                    "vcs": False,
                    "pypi": True,
                }

if ALLOW_RESTR_MODULES:
    system_packages = []
else:
    # Python3 packages that come as part of org.freedesktop.Sdk.
    system_packages = [
        "cython",
        "mako",
        "markdown",
        "meson",
        "packaging",
        "pip",
        "setuptools",
        "wheel",
    ]

ignore_installed = {pkg.casefold() for pkg in opts.ignore_installed}

fprint("Generating dependencies")
for package in packages:
    if package.name is None:
        print(
            f"Warning: skipping invalid requirement specification {package.line} "
            "because it is missing a name",
            file=sys.stderr,
        )
        print(
            "Append #egg=<pkgname> to the end of the requirement line to fix",
            file=sys.stderr,
        )
        continue
    elif (
        not opts.python2
        and package.name.casefold() in system_packages
        and package.name.casefold() not in ignore_installed
    ):
        print(f"{package.name} is in system_packages. Skipping.")
        continue

    if len(package.extras) > 0:
        extras = "[" + ",".join(extra for extra in package.extras) + "]"
    else:
        extras = ""

    version_list = [x[0] + x[1] for x in package.specs]
    version = ",".join(version_list)

    if package.vcs:
        revision = ""
        if package.revision:
            revision = "@" + package.revision
        pkg = package.uri + revision + "#egg=" + package.name
    else:
        pkg = package.name + extras + version

    dependencies = []
    # Downloads the package again to list dependencies

    tempdir_prefix = f"pip-generator-{package.name}"
    with tempfile.TemporaryDirectory(
        prefix=f"{tempdir_prefix}-{package.name}"
    ) as tempdir:
        pip_download = [
            *flatpak_cmd,
            "download",
            "--exists-action=i",
            "--dest",
            tempdir,
        ]
        try:
            print(f"Generating dependencies for {package.name}")
            subprocess.run([*pip_download, pkg], check=True, stdout=subprocess.DEVNULL)
            for filename in sorted(os.listdir(tempdir)):
                dep_name = get_package_name(filename)
                if (
                    dep_name.casefold() in system_packages
                    and dep_name.casefold() not in ignore_installed
                ):
                    continue
                dependencies.append(dep_name)

        except subprocess.CalledProcessError:
            print(f"Failed to download {package.name}")

    is_vcs = bool(package.vcs)
    package_sources = []
    for dependency in dependencies:
        casefolded = normalize_name(dependency)
        if casefolded in sources and sources[casefolded].get("pypi") is True:
            source = sources[casefolded]
        elif dependency in sources and sources[dependency].get("pypi") is False:
            source = sources[dependency]
        elif (
            casefolded.replace("_", "-") in sources
            and sources[casefolded.replace("_", "-")].get("pypi") is True
        ):
            source = sources[casefolded.replace("_", "-")]
        elif (
            dependency.replace("_", "-") in sources
            and sources[dependency.replace("_", "-")].get("pypi") is False
        ):
            source = sources[dependency.replace("_", "-")]
        else:
            continue

        if source["vcs"] and not is_vcs:
            continue

        package_sources.extend(source["source"])

    name_for_pip = "." if package.vcs else pkg

    module_name = f"python{python_version}-{package.name}"

    pip_command = [
        pip_executable,
        "install",
        "--verbose",
        "--exists-action=i",
        "--no-index",
        '--find-links="file://${PWD}"',
        "--prefix=${FLATPAK_DEST}",
        f'"{name_for_pip}"',
    ]
    if package.name in ignore_installed:
        pip_command.append("--ignore-installed")
    if not opts.build_isolation:
        pip_command.append("--no-build-isolation")

    module = OrderedDict(
        [
            ("name", module_name),
            ("buildsystem", "simple"),
            ("build-commands", [" ".join(pip_command)]),
            ("sources", package_sources),
        ]
    )
    if opts.cleanup == "all":
        module["cleanup"] = ["*"]
    elif opts.cleanup == "scripts":
        module["cleanup"] = ["/bin", "/share/man/man1"]

    if package.vcs:
        vcs_modules.append(module)
    else:
        modules.append(module)

modules = vcs_modules + modules

if not modules:
    sys.exit("No modules were generated. Nothing to write.")

if len(modules) == 1:
    pypi_module = modules[0]
else:
    pypi_module = {
        "name": output_package,
        "buildsystem": "simple",
        "build-commands": [],
        "modules": modules,
    }

print()
with open(output_filename, "w") as output:
    if opts.yaml:

        class OrderedDumper(yaml.Dumper):
            def increase_indent(self, flow: bool = False, indentless: bool = False):
                return super().increase_indent(flow, False)

        def dict_representer(
            dumper: yaml.Dumper, data: OrderedDict[str, Any]
        ) -> yaml.nodes.MappingNode:
            return dumper.represent_dict(data.items())

        OrderedDumper.add_representer(OrderedDict, dict_representer)

        output.write(
            "# Generated with flatpak-pip-generator " + " ".join(sys.argv[1:]) + "\n"
        )
        yaml.dump(
            pypi_module,
            output,
            Dumper=OrderedDumper,
            sort_keys=False,
        )
    else:
        output.write(json.dumps(pypi_module, indent=4) + "\n")

    print(f"Output saved to {output_filename}")

if len(unresolved_dependencies_errors) != 0:
    for e in unresolved_dependencies_errors:
        print(f"- ERROR: {e}")

    if prefer_wheels_missing:
        pkgs = ",".join(sorted(set(prefer_wheels_missing)))
        print(
            f"\nOnly platform wheels are available for: {pkgs}. "
            f"Use '--runtime $RUNTIME_ID//$RUNTIME_BRANCH --prefer-wheels={pkgs}'\n",
            file=sys.stderr,
        )

    raise Exception("Unresolved dependencies. Handle them manually")
