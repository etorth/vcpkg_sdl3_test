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

`build.py` uses the current working directory as the output root: it creates `.vcpkg/` and `build/` there, even when the script is launched by absolute path from another directory. It installs SDL3 dependencies with static linkage where vcpkg supports it. Pass `--install-deps` to also install platform system dependencies before building.

Out-of-source build example:

```sh
mkdir -p ~/build/vcpkg_sdl3_test
cd ~/build/vcpkg_sdl3_test
/home/anhong/vcpkg_sdl3_test/build.py
```

After vcpkg is ready, CMake can also configure and build directly:

```sh
cmake -S /home/anhong/vcpkg_sdl3_test -B build \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/.vcpkg/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_MANIFEST_MODE=OFF
cmake --build build --parallel
```

Run the demo from the build output:

```sh
./build/bin/sdl3_vcpkg_test
```

Press Space to replay the sound and Esc to quit.
