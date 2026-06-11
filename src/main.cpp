#include <SDL3/SDL_main.h>

#include "App.h"

#include <exception>
#include <iostream>

int main(int, char**) {
  try {
    App app;
    app.run();
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }

  return 0;
}

