#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path.cwd().resolve()
BUILD_DIR = Path(os.environ.get("BUILD_DIR", str(OUTPUT_DIR / "build"))).expanduser().resolve()
BUILD_TYPE = os.environ.get("BUILD_TYPE", "Debug")
LOCAL_VCPKG_ROOT = Path(os.environ.get("VCPKG_ROOT", str(OUTPUT_DIR / ".vcpkg"))).expanduser().resolve()

REQUIRED_PACKAGES = [
    "git",
    "curl",
    "cmake",
    "build-essential",
    "pkg-config",
    "tar",
    "zip",
    "unzip",
    "libx11-dev",
    "libxft-dev",
    "libxext-dev",
    "libwayland-dev",
    "libxkbcommon-dev",
    "libegl1-mesa-dev",
    "libibus-1.0-dev",
]

VCPKG_PACKAGES = [
    "sdl3",
    "sdl3-image[png]",
    "sdl3-ttf",
    "sdl3-mixer[libvorbis]",
    "sdl3-gfx",
]


def run(args, *, env=None):
    subprocess.run(args, check=True, env=env)


def log(message):
    print(message, flush=True)


def default_triplet():
    system = platform.system()
    if system == "Darwin":
        return "x64-osx"
    if system == "Windows" or system.startswith(("MINGW", "MSYS", "CYGWIN")):
        return "x64-windows-static"
    return "x64-linux"


def parse_args():
    parser = argparse.ArgumentParser(description="Fresh-build the SDL3 vcpkg test project.")
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install platform system dependencies before building.",
    )
    parser.add_argument(
        "--vcpkg-prefix",
        type=Path,
        help="Use the vcpkg installation at this prefix instead of bootstrapping a local one.",
    )
    return parser.parse_args()


def confirm_system_package_install(packages):
    package_list = " ".join(packages)
    try:
        answer = input(f"Install system packages system-wide: {package_list}. Confirm [y/N]: ")
    except EOFError:
        answer = ""

    if answer.strip().lower() not in ("y", "yes"):
        print("Aborted system package installation.", file=sys.stderr)
        sys.exit(1)


def install_platform_dependencies(*, install_deps):
    if not install_deps:
        return
    if platform.system() != "Linux" or not shutil.which("apt") or not shutil.which("dpkg"):
        return

    missing = [
        package
        for package in REQUIRED_PACKAGES
        if subprocess.run(
            ["dpkg", "-s", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        != 0
    ]
    if not missing:
        return

    if getattr(os, "geteuid", lambda: -1)() == 0:
        confirm_system_package_install(missing)
        log(f"Installing system packages required by vcpkg/SDL3: {' '.join(missing)}")
        run(["apt", "update"])
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"
        run(["apt", "install", "-y", *missing], env=env)
    elif shutil.which("sudo"):
        confirm_system_package_install(missing)
        log(f"Installing system packages required by vcpkg/SDL3: {' '.join(missing)}")
        run(["sudo", "apt", "update"])
        run(
            [
                "sudo",
                "env",
                "DEBIAN_FRONTEND=noninteractive",
                "apt",
                "install",
                "-y",
                *missing,
            ]
        )
    else:
        print(f"Missing system packages: {' '.join(missing)}", file=sys.stderr)
        print("Install them manually.", file=sys.stderr)
        sys.exit(1)


def missing_tool_message(description, *, install_deps):
    if install_deps:
        return (
            f"Missing required tool after dependency installation: {description}. "
            "Install it manually."
        )
    return f"Missing required tool: {description}. Install it or rerun with --install-deps."


def need_tool(name, *, install_deps):
    if not shutil.which(name):
        print(missing_tool_message(name, install_deps=install_deps), file=sys.stderr)
        sys.exit(1)


def need_any_tool(names, description, *, install_deps):
    if not any(shutil.which(name) for name in names):
        print(missing_tool_message(description, install_deps=install_deps), file=sys.stderr)
        sys.exit(1)


def is_executable(path):
    return path.is_file() and os.access(path, os.X_OK)


def vcpkg_toolchain(vcpkg_root):
    return vcpkg_root / "scripts/buildsystems/vcpkg.cmake"


def validate_vcpkg(vcpkg, vcpkg_root, source):
    try:
        version_result = subprocess.run(
            [str(vcpkg), "version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError as error:
        print(f"Invalid {source} ({vcpkg}): {error}", file=sys.stderr)
        sys.exit(1)

    if version_result.returncode != 0:
        print(f"Invalid {source} ({vcpkg}): `vcpkg version` failed", file=sys.stderr)
        sys.exit(1)

    if vcpkg_toolchain(vcpkg_root).exists():
        return vcpkg, vcpkg_root

    print(f"Invalid {source} ({vcpkg_root}): missing {vcpkg_toolchain(vcpkg_root)}", file=sys.stderr)
    sys.exit(1)


def resolve_vcpkg_prefix(vcpkg_prefix):
    prefix = vcpkg_prefix.expanduser().resolve()
    if prefix.is_file():
        vcpkg = prefix
        vcpkg_root = prefix.parent
    else:
        vcpkg_root = prefix
        vcpkg = vcpkg_root / ("vcpkg.exe" if platform.system() == "Windows" else "vcpkg")
        if not is_executable(vcpkg):
            fallback = vcpkg_root / "vcpkg.exe"
            if is_executable(fallback):
                vcpkg = fallback

    if not is_executable(vcpkg):
        print(
            f"Invalid --vcpkg-prefix ({prefix}): no executable vcpkg was found there.",
            file=sys.stderr,
        )
        sys.exit(1)

    return validate_vcpkg(vcpkg, vcpkg_root, "--vcpkg-prefix")


def bootstrap_local_vcpkg():
    if not LOCAL_VCPKG_ROOT.exists():
        log(f"Installing vcpkg into {LOCAL_VCPKG_ROOT}")
        run(["git", "clone", "https://github.com/microsoft/vcpkg.git", str(LOCAL_VCPKG_ROOT)])

    vcpkg = LOCAL_VCPKG_ROOT / ("vcpkg.exe" if platform.system() == "Windows" else "vcpkg")
    if is_executable(vcpkg):
        return vcpkg, LOCAL_VCPKG_ROOT

    bootstrap_sh = LOCAL_VCPKG_ROOT / "bootstrap-vcpkg.sh"
    bootstrap_bat = LOCAL_VCPKG_ROOT / "bootstrap-vcpkg.bat"
    if bootstrap_sh.exists():
        run([str(bootstrap_sh), "-disableMetrics"])
    elif bootstrap_bat.exists():
        run(["cmd", "/c", str(bootstrap_bat), "-disableMetrics"])
    else:
        print(f"vcpkg is not ready and no bootstrap script was found in {LOCAL_VCPKG_ROOT}", file=sys.stderr)
        sys.exit(1)

    if is_executable(vcpkg):
        return vcpkg, LOCAL_VCPKG_ROOT

    fallback = LOCAL_VCPKG_ROOT / "vcpkg.exe"
    if is_executable(fallback):
        return fallback, LOCAL_VCPKG_ROOT

    print(f"vcpkg bootstrap finished, but no vcpkg executable was found in {LOCAL_VCPKG_ROOT}", file=sys.stderr)
    sys.exit(1)


def resolve_vcpkg(*, install_deps):
    if install_deps:
        vcpkg, vcpkg_root = bootstrap_local_vcpkg()
        return validate_vcpkg(vcpkg, vcpkg_root, "local vcpkg")

    print(
        "Missing required vcpkg. Provide --vcpkg-prefix /path/to/vcpkg "
        "or rerun with --install-deps to bootstrap a local vcpkg.",
        file=sys.stderr,
    )
    sys.exit(1)


def main():
    args = parse_args()
    vcpkg_triplet = os.environ.get("VCPKG_DEFAULT_TRIPLET", default_triplet())
    selected_vcpkg = resolve_vcpkg_prefix(args.vcpkg_prefix) if args.vcpkg_prefix else None

    install_platform_dependencies(install_deps=args.install_deps)
    need_tool("git", install_deps=args.install_deps)
    need_tool("curl", install_deps=args.install_deps)
    need_tool("cmake", install_deps=args.install_deps)
    need_any_tool(
        ["cc", "gcc", "clang", "cl"],
        "C compiler (cc, gcc, clang, or cl)",
        install_deps=args.install_deps,
    )
    need_any_tool(
        ["c++", "g++", "clang++", "cl"],
        "C++ compiler (c++, g++, clang++, or cl)",
        install_deps=args.install_deps,
    )

    if selected_vcpkg:
        vcpkg, vcpkg_root = selected_vcpkg
    else:
        vcpkg, vcpkg_root = resolve_vcpkg(install_deps=args.install_deps)

    log(f"Using vcpkg: {vcpkg}")
    log(f"Installing SDL3 packages for {vcpkg_triplet}")
    run(
        [
            str(vcpkg),
            "install",
            "--classic",
            "--recurse",
            "--triplet",
            vcpkg_triplet,
            f"--overlay-ports={SOURCE_DIR / 'ports'}",
            *VCPKG_PACKAGES,
        ]
    )

    log(f"Configuring a fresh build in {BUILD_DIR}")
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    run(
        [
            "cmake",
            "-S",
            str(SOURCE_DIR),
            "-B",
            str(BUILD_DIR),
            f"-DCMAKE_BUILD_TYPE={BUILD_TYPE}",
            f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_toolchain(vcpkg_root)}",
            f"-DVCPKG_TARGET_TRIPLET={vcpkg_triplet}",
            "-DVCPKG_MANIFEST_MODE=OFF",
        ]
    )

    log("Building")
    run(["cmake", "--build", str(BUILD_DIR), "--config", BUILD_TYPE, "--parallel"])
    log(f"Built: {BUILD_DIR / 'bin/sdl3_vcpkg_test'}")


if __name__ == "__main__":
    main()
