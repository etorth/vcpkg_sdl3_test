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
./build.sh
```

`build.sh` installs a local vcpkg checkout in `.vcpkg`, installs SDL3 dependencies, and installs SDL3 Linux system prerequisites with `apt install` when needed. Set `SKIP_APT_INSTALL=1` to skip the apt step.

After vcpkg is ready, CMake can also configure and build directly:

```sh
cmake -S . -B build
cmake --build build --parallel
```

Run the demo from the build output:

```sh
./build/bin/sdl3_vcpkg_test
```

Press Space to replay the sound and Esc to quit.
