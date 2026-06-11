#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${BUILD_DIR:-"${ROOT_DIR}/build"}"
BUILD_TYPE="${BUILD_TYPE:-Debug}"
VCPKG_ROOT="${VCPKG_ROOT:-"${ROOT_DIR}/.vcpkg"}"

case "$(uname -s)" in
  Darwin*) DEFAULT_TRIPLET="x64-osx" ;;
  MINGW*|MSYS*|CYGWIN*) DEFAULT_TRIPLET="x64-windows" ;;
  *) DEFAULT_TRIPLET="x64-linux" ;;
esac
VCPKG_TRIPLET="${VCPKG_DEFAULT_TRIPLET:-${DEFAULT_TRIPLET}}"

install_apt_packages() {
  if [[ "${SKIP_APT_INSTALL:-0}" == "1" ]]; then
    return
  fi
  if [[ "$(uname -s)" != "Linux" ]] || ! command -v apt >/dev/null 2>&1 || ! command -v dpkg >/dev/null 2>&1; then
    return
  fi

  local missing=()
  local package
  for package in "$@"; do
    if ! dpkg -s "${package}" >/dev/null 2>&1; then
      missing+=("${package}")
    fi
  done

  if ((${#missing[@]} == 0)); then
    return
  fi

  echo "Installing system packages required by vcpkg/SDL3: ${missing[*]}"
  if [[ "${EUID}" -eq 0 ]]; then
    apt update
    DEBIAN_FRONTEND=noninteractive apt install -y "${missing[@]}"
  elif command -v sudo >/dev/null 2>&1; then
    sudo apt update
    sudo env DEBIAN_FRONTEND=noninteractive apt install -y "${missing[@]}"
  else
    echo "Missing system packages: ${missing[*]}" >&2
    echo "Install them manually, or set SKIP_APT_INSTALL=1 to skip this check." >&2
    exit 1
  fi
}

need_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required tool: $1" >&2
    exit 1
  fi
}

install_apt_packages \
  git \
  curl \
  cmake \
  build-essential \
  pkg-config \
  tar \
  zip \
  unzip \
  libx11-dev \
  libxft-dev \
  libxext-dev \
  libwayland-dev \
  libxkbcommon-dev \
  libegl1-mesa-dev \
  libibus-1.0-dev

need_tool git
need_tool curl
need_tool cmake

if [[ ! -x "${VCPKG_ROOT}/vcpkg" && ! -x "${VCPKG_ROOT}/vcpkg.exe" ]]; then
  echo "Installing vcpkg into ${VCPKG_ROOT}"
  git clone https://github.com/microsoft/vcpkg.git "${VCPKG_ROOT}"
  "${VCPKG_ROOT}/bootstrap-vcpkg.sh" -disableMetrics
fi

if [[ -x "${VCPKG_ROOT}/vcpkg.exe" ]]; then
  VCPKG_EXE="${VCPKG_ROOT}/vcpkg.exe"
else
  VCPKG_EXE="${VCPKG_ROOT}/vcpkg"
fi

PACKAGES=(
  sdl3
  "sdl3-image[png]"
  sdl3-ttf
  "sdl3-mixer[libvorbis]"
  sdl3-gfx
)

echo "Installing SDL3 packages for ${VCPKG_TRIPLET}"
"${VCPKG_EXE}" install \
  --classic \
  --recurse \
  --triplet "${VCPKG_TRIPLET}" \
  --overlay-ports="${ROOT_DIR}/ports" \
  "${PACKAGES[@]}"

echo "Configuring a fresh build in ${BUILD_DIR}"
rm -rf "${BUILD_DIR}"
cmake -S "${ROOT_DIR}" -B "${BUILD_DIR}" \
  -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
  -DCMAKE_TOOLCHAIN_FILE="${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_TARGET_TRIPLET="${VCPKG_TRIPLET}" \
  -DVCPKG_MANIFEST_MODE=OFF

echo "Building"
cmake --build "${BUILD_DIR}" --config "${BUILD_TYPE}" --parallel

echo "Built: ${BUILD_DIR}/bin/sdl3_vcpkg_test"
