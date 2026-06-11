Resources used by the SDL3 test app.

- checker.ppm is loaded through SDL3_image.
- elephant.png is loaded through SDL3_image's APNG animation API.
- beep.wav is loaded through SDL3_mixer.
- sound.ogg is loaded through SDL3_mixer and played in a loop.
- SDL3_ttf uses SDL3_TEST_FONT, res/DejaVuSans.ttf if present, or a common system font.
