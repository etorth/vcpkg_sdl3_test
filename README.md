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

`build.py` uses the current working directory as the output root: it creates `.vcpkg/` and `build/` there, even when the script is launched by absolute path from another directory. It installs SDL3 dependencies and Linux system prerequisites with `apt install` when needed. Pass `--skip-apt-install` to skip the apt step.

Out-of-source build example:

```sh
mkdir -p ~/build/vcpkg_sdl3_test
cd ~/build/vcpkg_sdl3_test
/home/anhong/vcpkg_sdl3_test/build.py
```

`build.sh` remains available as a shell equivalent with the original source-local layout.

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
