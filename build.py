#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent
DEFAULT_LOCAL_BUILD_DIR = Path.cwd().resolve()

def run(args, *, env=None):
    subprocess.run(args, check=True, env=env)


def run_batch_file(batch_file, *args):
    run([os.environ.get("COMSPEC") or "cmd", "/c", str(batch_file), *args])


def log(message):
    print(message, flush=True)


def is_windows_like(system=None):
    system = system or platform.system()
    return system == "Windows" or system.startswith(("MINGW", "MSYS", "CYGWIN"))


def default_mingw_triplet():
    msystem = os.environ.get("MSYSTEM", "").upper()
    msystem_chost = os.environ.get("MSYSTEM_CHOST", "").lower()
    has_msys2_environment = bool(
        msystem
        or msystem_chost
        or os.environ.get("MINGW_PREFIX")
        or os.environ.get("MSYSTEM_PREFIX")
    )

    if not has_msys2_environment and not platform.system().startswith(("MINGW", "MSYS")):
        return None

    if "aarch64" in msystem_chost or "arm64" in msystem:
        return "arm64-mingw-static"
    if msystem_chost.startswith("i686") or msystem.endswith("32"):
        return "x86-mingw-static"

    machine = platform.machine().lower()
    if machine in ("aarch64", "arm64"):
        return "arm64-mingw-static"
    if machine in ("i386", "i686", "x86"):
        return "x86-mingw-static"

    return "x64-mingw-static"


def default_triplet():
    system = platform.system()
    if system == "Darwin":
        return "x64-osx"
    mingw_triplet = default_mingw_triplet()
    if mingw_triplet:
        return mingw_triplet
    if is_windows_like(system):
        return "x64-windows-static"
    return "x64-linux"


def default_host_triplet(target_triplet):
    mingw_triplet = default_mingw_triplet()
    if mingw_triplet:
        return mingw_triplet
    if "mingw" in target_triplet:
        return target_triplet
    return None


def parse_args():
    parser = argparse.ArgumentParser(description="Fresh-build the SDL3 vcpkg test project.")
    parser.add_argument(
        "--vcpkg-prefix",
        type=Path,
        help="Use the vcpkg installation at this prefix instead of bootstrapping a local one.",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        help="Use this directory as the local build root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--c-compiler",
        help="CMAKE_C_COMPILER.",
    )
    parser.add_argument(
        "--cxx-compiler",
        help="CMAKE_CXX_COMPILER.",
    )
    parser.add_argument(
        "--build-type",
        default="Release",
        help="CMAKE_BUILD_TYPE",
    )
    parser.add_argument(
        "--install-prefix",
        type=Path,
        help="CMAKE_INSTALL_PREFIX. Defaults to <build-dir>/install.",
    )
    return parser.parse_args()


def is_executable(path):
    return path.is_file() and os.access(path, os.X_OK)


def vcpkg_toolchain(vcpkg_root):
    return vcpkg_root / "scripts/buildsystems/vcpkg.cmake"


def resolve_vcpkg_prefix(vcpkg_prefix):
    prefix = vcpkg_prefix.expanduser().resolve()
    if prefix.is_file():
        vcpkg = prefix
        vcpkg_root = prefix.parent
    else:
        vcpkg_root = prefix
        vcpkg = vcpkg_root / ("vcpkg.exe" if is_windows_like() else "vcpkg")
        if not is_executable(vcpkg):
            fallback = vcpkg_root / "vcpkg.exe"
            if is_executable(fallback):
                vcpkg = fallback

    return vcpkg, vcpkg_root


def bootstrap_local_vcpkg(local_vcpkg_dir):
    if not local_vcpkg_dir.exists():
        log(f"Installing vcpkg into {local_vcpkg_dir}")
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "https://github.com/microsoft/vcpkg.git",
                str(local_vcpkg_dir),
            ]
        )

    vcpkg = local_vcpkg_dir / ("vcpkg.exe" if is_windows_like() else "vcpkg")
    if is_executable(vcpkg):
        return vcpkg, local_vcpkg_dir

    bootstrap_sh = local_vcpkg_dir / "bootstrap-vcpkg.sh"
    bootstrap_bat = local_vcpkg_dir / "bootstrap-vcpkg.bat"
    if is_windows_like() and bootstrap_bat.exists():
        run_batch_file(bootstrap_bat, "-disableMetrics")
    elif bootstrap_sh.exists():
        run([str(bootstrap_sh), "-disableMetrics"])
    elif bootstrap_bat.exists():
        run_batch_file(bootstrap_bat, "-disableMetrics")
    else:
        print(f"vcpkg is not ready and no bootstrap script was found in {local_vcpkg_dir}", file=sys.stderr)
        sys.exit(1)

    if is_executable(vcpkg):
        return vcpkg, local_vcpkg_dir

    fallback = local_vcpkg_dir / "vcpkg.exe"
    if is_executable(fallback):
        return fallback, local_vcpkg_dir

    print(f"vcpkg bootstrap finished, but no vcpkg executable was found in {local_vcpkg_dir}", file=sys.stderr)
    sys.exit(1)


def resolve_vcpkg(local_vcpkg_dir):
    return bootstrap_local_vcpkg(local_vcpkg_dir)


def main():
    args = parse_args()
    vcpkg_triplet = os.environ.get("VCPKG_DEFAULT_TRIPLET", default_triplet())
    vcpkg_host_triplet = os.environ.get(
        "VCPKG_DEFAULT_HOST_TRIPLET",
        default_host_triplet(vcpkg_triplet),
    )
    local_build_dir = args.build_dir.expanduser().resolve() if args.build_dir else DEFAULT_LOCAL_BUILD_DIR
    local_vcpkg_dir = local_build_dir / "vcpkg"
    cmake_build_dir = local_build_dir / "build"
    selected_vcpkg = resolve_vcpkg_prefix(args.vcpkg_prefix) if args.vcpkg_prefix else None
    install_prefix = (
        args.install_prefix.expanduser().resolve()
        if args.install_prefix
        else local_build_dir / "install"
    )
    local_build_dir.mkdir(parents=True, exist_ok=True)

    if selected_vcpkg:
        vcpkg, vcpkg_root = selected_vcpkg
    else:
        vcpkg, vcpkg_root = resolve_vcpkg(local_vcpkg_dir)

    log(f"Using vcpkg: {vcpkg}")
    if vcpkg_host_triplet:
        log(f"Configuring SDL3 manifest for {vcpkg_triplet} with host triplet {vcpkg_host_triplet}")
    else:
        log(f"Configuring SDL3 manifest for {vcpkg_triplet}")

    log(f"Configuring a fresh build in {cmake_build_dir}")
    shutil.rmtree(cmake_build_dir, ignore_errors=True)
    cmake_configure_args = [
        "cmake",
        "-S",
        str(SOURCE_DIR),
        "-B",
        str(cmake_build_dir),
        f"-DCMAKE_BUILD_TYPE={args.build_type}",
        f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_toolchain(vcpkg_root)}",
        f"-DVCPKG_TARGET_TRIPLET={vcpkg_triplet}",
    ]
    if vcpkg_host_triplet:
        cmake_configure_args.append(f"-DVCPKG_HOST_TRIPLET={vcpkg_host_triplet}")
    if args.c_compiler:
        cmake_configure_args.append(f"-DCMAKE_C_COMPILER={args.c_compiler}")
    if args.cxx_compiler:
        cmake_configure_args.append(f"-DCMAKE_CXX_COMPILER={args.cxx_compiler}")
    cmake_configure_args.append(f"-DCMAKE_INSTALL_PREFIX={install_prefix}")
    run(cmake_configure_args)

    log("Building")
    run(["cmake", "--build", str(cmake_build_dir), "--config", args.build_type, "--parallel"])
    log(f"Built: {cmake_build_dir / 'bin/sdl3_vcpkg_test'}")

    log(f"Installing into {install_prefix}")
    run(["cmake", "--install", str(cmake_build_dir), "--config", args.build_type])


if __name__ == "__main__":
    main()
