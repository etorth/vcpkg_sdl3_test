# vcpkg_sdl3_test

A small SDL3 test project built with CMake and vcpkg.

It exercises:

- SDL3 window/render/audio initialization
- SDL3_gfx drawing primitives
- SDL3_image image loading
- SDL3_image APNG animation loading
- SDL3_ttf text rendering
- SDL3_mixer WAV playback and looping OGG playback

Build with an existing vcpkg checkout:

```sh
./build.py --vcpkg-prefix /path/to/vcpkg
```

Or bootstrap a local vcpkg checkout in the current directory:

```sh
./build.py --install-deps
```

`build.py` uses the current working directory as the output root: it creates `build/` there, even when the script is launched by absolute path from another directory. Use `--vcpkg-prefix` to point at an existing vcpkg installation. Without `--vcpkg-prefix`, vcpkg is controlled by `--install-deps`, which bootstraps a local `.vcpkg/` in the current directory. If `--install-deps` needs to install system-wide packages, it asks for confirmation before changing the system. CMake uses the repo's `vcpkg.json` manifest to install SDL3 dependencies with static linkage where vcpkg supports it. MSYS2/MinGW shells default both target and host packages to a `*-mingw-static` triplet; other Windows shells default target packages to `x64-windows-static`. Set `VCPKG_DEFAULT_TRIPLET` or `VCPKG_DEFAULT_HOST_TRIPLET` to override those defaults.

Out-of-source build example:

```sh
mkdir -p ~/build/vcpkg_sdl3_test
cd ~/build/vcpkg_sdl3_test
/home/anhong/vcpkg_sdl3_test/build.py --install-deps
```

After vcpkg is ready, CMake can also configure and build directly by pointing at that vcpkg toolchain file:

```sh
cmake -S /home/anhong/vcpkg_sdl3_test -B build \
  -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --parallel
```

Run the demo from the build output:

```sh
./build/bin/sdl3_vcpkg_test
```

Press Space to replay the sound and Esc to quit.
