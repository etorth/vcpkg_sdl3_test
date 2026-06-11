#pragma once

#include <SDL3/SDL.h>
#include <SDL3_mixer/SDL_mixer.h>
#include <SDL3_ttf/SDL_ttf.h>

#include <filesystem>
#include <string>
#include <vector>

class App {
public:
  App();
  ~App();

  App(const App&) = delete;
  App& operator=(const App&) = delete;

  void run();

private:
  void init();
  void loadResources();
  void handleEvent(const SDL_Event& event);
  void render();
  void renderApng(Uint64 ticks) const;
  void renderTtfText(float x, float y) const;
  void playMusicLoop() const;
  void playSound() const;

  [[nodiscard]] std::filesystem::path resourcePath(const std::string& name) const;
  [[nodiscard]] std::filesystem::path findFont() const;

  SDL_Window* window_ = nullptr;
  SDL_Renderer* renderer_ = nullptr;
  SDL_Texture* imageTexture_ = nullptr;
  SDL_Texture* textTexture_ = nullptr;
  std::vector<SDL_Texture*> apngFrames_;
  std::vector<int> apngFrameDelays_;
  MIX_Mixer* mixer_ = nullptr;
  MIX_Audio* beep_ = nullptr;
  MIX_Track* beepTrack_ = nullptr;
  MIX_Audio* music_ = nullptr;
  MIX_Track* musicTrack_ = nullptr;
  TTF_Font* font_ = nullptr;

  std::filesystem::path basePath_;
  bool running_ = true;
  bool mixerInitialized_ = false;
  float imageWidth_ = 0.0f;
  float imageHeight_ = 0.0f;
  float textWidth_ = 0.0f;
  float textHeight_ = 0.0f;
  int apngWidth_ = 0;
  int apngHeight_ = 0;
  int apngTotalDelayMs_ = 0;
};
