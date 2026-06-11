#include "App.h"

#include <SDL3_image/SDL_image.h>
#include <SDL3_gfx/SDL3_gfxPrimitives.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <string>

namespace {
std::runtime_error sdlError(const std::string& what) {
  return std::runtime_error(what + ": " + SDL_GetError());
}
} // namespace

App::App() {
  init();
  loadResources();
}

App::~App() {
  if (beepTrack_) {
    MIX_DestroyTrack(beepTrack_);
  }
  if (beep_) {
    MIX_DestroyAudio(beep_);
  }
  if (textTexture_) {
    SDL_DestroyTexture(textTexture_);
  }
  if (font_) {
    TTF_CloseFont(font_);
  }
  if (imageTexture_) {
    SDL_DestroyTexture(imageTexture_);
  }
  if (mixer_) {
    MIX_DestroyMixer(mixer_);
  }
  if (renderer_) {
    SDL_DestroyRenderer(renderer_);
  }
  if (window_) {
    SDL_DestroyWindow(window_);
  }
  TTF_Quit();
  if (mixerInitialized_) {
    MIX_Quit();
  }
  SDL_Quit();
}

void App::init() {
  if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO)) {
    throw sdlError("SDL_Init failed");
  }

  if (!TTF_Init()) {
    throw sdlError("TTF_Init failed");
  }

  if (MIX_Init()) {
    mixerInitialized_ = true;
  } else {
    SDL_Log("SDL3_mixer initialization unavailable: %s", SDL_GetError());
  }

  window_ = SDL_CreateWindow("SDL3 + vcpkg test", 960, 540, SDL_WINDOW_RESIZABLE);
  if (!window_) {
    throw sdlError("SDL_CreateWindow failed");
  }

  renderer_ = SDL_CreateRenderer(window_, nullptr);
  if (!renderer_) {
    throw sdlError("SDL_CreateRenderer failed");
  }
  SDL_SetRenderVSync(renderer_, 1);

  SDL_AudioSpec audioSpec{};
  audioSpec.freq = 44100;
  audioSpec.format = SDL_AUDIO_S16;
  audioSpec.channels = 1;
  if (mixerInitialized_) {
    mixer_ = MIX_CreateMixerDevice(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &audioSpec);
  }
  if (!mixer_) {
    SDL_Log("Audio output unavailable: %s", SDL_GetError());
  }

  const char* base = SDL_GetBasePath();
  basePath_ = base ? std::filesystem::path(base) : std::filesystem::current_path();
}

void App::loadResources() {
  const auto imagePath = resourcePath("checker.ppm");
  SDL_Surface* imageSurface = IMG_Load(imagePath.string().c_str());
  if (!imageSurface) {
    throw sdlError("IMG_Load failed for " + imagePath.string());
  }
  imageWidth_ = static_cast<float>(imageSurface->w);
  imageHeight_ = static_cast<float>(imageSurface->h);
  imageTexture_ = SDL_CreateTextureFromSurface(renderer_, imageSurface);
  SDL_DestroySurface(imageSurface);
  if (!imageTexture_) {
    throw sdlError("SDL_CreateTextureFromSurface failed for image");
  }

  if (mixer_) {
    const auto soundPath = resourcePath("beep.wav");
    beep_ = MIX_LoadAudio(mixer_, soundPath.string().c_str(), true);
    if (!beep_) {
      throw sdlError("MIX_LoadAudio failed for " + soundPath.string());
    }

    beepTrack_ = MIX_CreateTrack(mixer_);
    if (!beepTrack_) {
      throw sdlError("MIX_CreateTrack failed");
    }
    if (!MIX_SetTrackAudio(beepTrack_, beep_)) {
      throw sdlError("MIX_SetTrackAudio failed");
    }
  }

  const auto fontPath = findFont();
  if (!fontPath.empty()) {
    font_ = TTF_OpenFont(fontPath.string().c_str(), 26.0f);
    if (!font_) {
      throw sdlError("TTF_OpenFont failed for " + fontPath.string());
    }

    SDL_Color color{230, 240, 255, 255};
    SDL_Surface* textSurface =
        TTF_RenderText_Blended(font_, "SDL3_ttf rendered text", 0, color);
    if (!textSurface) {
      throw sdlError("TTF_RenderText_Blended failed");
    }
    textWidth_ = static_cast<float>(textSurface->w);
    textHeight_ = static_cast<float>(textSurface->h);
    textTexture_ = SDL_CreateTextureFromSurface(renderer_, textSurface);
    SDL_DestroySurface(textSurface);
    if (!textTexture_) {
      throw sdlError("SDL_CreateTextureFromSurface failed for text");
    }
  } else {
    SDL_Log("No TrueType font found; set SDL3_TEST_FONT or add res/DejaVuSans.ttf to enable SDL3_ttf text.");
  }

  playSound();
}

void App::run() {
  while (running_) {
    SDL_Event event{};
    while (SDL_PollEvent(&event)) {
      handleEvent(event);
    }

    render();
    SDL_Delay(16);
  }
}

void App::handleEvent(const SDL_Event& event) {
  if (event.type == SDL_EVENT_QUIT) {
    running_ = false;
  } else if (event.type == SDL_EVENT_KEY_DOWN) {
    if (event.key.key == SDLK_ESCAPE) {
      running_ = false;
    } else if (event.key.key == SDLK_SPACE) {
      playSound();
    }
  }
}

void App::render() {
  const Uint64 ticks = SDL_GetTicks();
  const float time = static_cast<float>(ticks) / 1000.0f;
  const float pulse = (std::sin(time * 2.5f) + 1.0f) * 0.5f;

  SDL_SetRenderDrawColor(renderer_, 18, 22, 32, 255);
  SDL_RenderClear(renderer_);

  roundedBoxRGBA(renderer_, 32, 32, 928, 508, 22, 36, 45, 66, 255);
  roundedRectangleRGBA(renderer_, 32, 32, 928, 508, 22, 86, 109, 160, 255);
  thickLineRGBA(renderer_, 64, 112, 896, 112, 4, 75, 192, 255, 255);

  const float radius = 54.0f + pulse * 18.0f;
  filledCircleRGBA(renderer_, 188, 268, radius, 250, 175, 65, 220);
  aacircleRGBA(renderer_, 188, 268, radius + 8.0f, 255, 232, 148, 255);

  const std::array<float, 5> px{394, 472, 548, 520, 420};
  const std::array<float, 5> py{202, 174, 238, 334, 324};
  filledPolygonRGBA(renderer_, px.data(), py.data(), static_cast<int>(px.size()), 128, 219, 144, 220);
  aapolygonRGBA(renderer_, px.data(), py.data(), static_cast<int>(px.size()), 210, 255, 218, 255);

  SDL_FRect imageDst{666.0f, 190.0f, imageWidth_ * 8.0f, imageHeight_ * 8.0f};
  SDL_RenderTexture(renderer_, imageTexture_, nullptr, &imageDst);
  rectangleRGBA(renderer_, imageDst.x - 1.0f, imageDst.y - 1.0f,
                imageDst.x + imageDst.w + 1.0f, imageDst.y + imageDst.h + 1.0f,
                255, 255, 255, 255);

  stringRGBA(renderer_, 72, 72, "SDL3_gfx primitives", 255, 255, 255, 255);
  stringRGBA(renderer_, 72, 476, "Space: play SDL3_mixer sound   Esc: quit", 196, 210, 232, 255);

  renderTtfText(72.0f, 136.0f);

  SDL_RenderPresent(renderer_);
}

void App::renderTtfText(float x, float y) const {
  if (!textTexture_) {
    stringRGBA(renderer_, x, y, "SDL3_ttf font not found", 255, 180, 180, 255);
    return;
  }

  SDL_FRect dst{x, y, textWidth_, textHeight_};
  SDL_RenderTexture(renderer_, textTexture_, nullptr, &dst);
}

void App::playSound() const {
  if (beepTrack_) {
    MIX_PlayTrack(beepTrack_, 0);
  }
}

std::filesystem::path App::resourcePath(const std::string& name) const {
  return basePath_ / "res" / name;
}

std::filesystem::path App::findFont() const {
  if (const char* envFont = SDL_getenv("SDL3_TEST_FONT")) {
    std::filesystem::path path(envFont);
    if (std::filesystem::exists(path)) {
      return path;
    }
  }

  const std::array<std::filesystem::path, 9> candidates{
      resourcePath("DejaVuSans.ttf"),
      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
      "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
      "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
      "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
      "/usr/share/fonts/TTF/DejaVuSans.ttf",
      "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
      "/System/Library/Fonts/Supplemental/Arial.ttf",
      "C:/Windows/Fonts/arial.ttf",
  };

  const auto found = std::find_if(candidates.begin(), candidates.end(),
                                  [](const auto& path) { return std::filesystem::exists(path); });
  return found != candidates.end() ? *found : std::filesystem::path{};
}
