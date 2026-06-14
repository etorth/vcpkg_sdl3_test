# vcpkg_sdl3_test

A small SDL3 test project built with CMake and vcpkg.

It exercises:

- SDL3 window/render/audio initialization
- SDL3_gfx drawing primitives
- SDL3_image image loading
- SDL3_image APNG animation loading
- SDL3_ttf text rendering
- SDL3_mixer WAV playback and looping OGG playback

Build from a fresh checkout:

```sh
./build.py
```

Or build with an existing vcpkg checkout:

```sh
./build.py --vcpkg-prefix /path/to/vcpkg
```

`build.py` uses the current working directory as the output root by default, or the directory passed to `--build-dir`. It creates `vcpkg/` and `build/` under that root, even when the script is launched by absolute path from another directory. Use `--vcpkg-prefix` to point at an existing vcpkg installation. The script does not install or pre-check system packages; missing tools fail at the command that needs them. CMake uses the repo's `vcpkg.json` manifest to install SDL3 dependencies with static linkage where vcpkg supports it. MSYS2/MinGW shells default both target and host packages to a `*-mingw-static` triplet; other Windows shells default target packages to `x64-windows-static`. Set `VCPKG_DEFAULT_TRIPLET` or `VCPKG_DEFAULT_HOST_TRIPLET` to override those defaults.

Use `--c-compiler`, `--cxx-compiler`, `--build-type`, `--build-dir`, and `--install-prefix` to set `CMAKE_C_COMPILER`, `CMAKE_CXX_COMPILER`, the output root, `CMAKE_BUILD_TYPE`, and `CMAKE_INSTALL_PREFIX`. If `--install-prefix` is omitted, it defaults to `<build-dir>/install`.

Out-of-source build example:

```sh
mkdir -p ~/build/vcpkg_sdl3_test
cd ~/build/vcpkg_sdl3_test
/home/anhong/vcpkg_sdl3_test/build.py
```

After vcpkg is ready, CMake can also configure and build directly by pointing at that vcpkg toolchain file:

```sh
cmake -S /home/anhong/vcpkg_sdl3_test -B build \
  -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --parallel
```

Run the demo from the install output:

```sh
./install/bin/sdl3_vcpkg_test
```

Press Space to replay the sound and Esc to quit.
