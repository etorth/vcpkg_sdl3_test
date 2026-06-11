cmake_minimum_required(VERSION 3.21)

if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
  if(DEFINED ENV{VCPKG_ROOT} AND EXISTS "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
        CACHE FILEPATH "vcpkg toolchain file")
  elseif(EXISTS "${CMAKE_CURRENT_LIST_DIR}/.vcpkg/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/.vcpkg/scripts/buildsystems/vcpkg.cmake"
        CACHE FILEPATH "vcpkg toolchain file")
  elseif(EXISTS "${CMAKE_CURRENT_LIST_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake"
        CACHE FILEPATH "vcpkg toolchain file")
  endif()
endif()

project(sdl3_vcpkg_test VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(SDL3 CONFIG REQUIRED)
find_package(SDL3_image CONFIG REQUIRED)
find_package(SDL3_ttf CONFIG REQUIRED)
find_package(SDL3_mixer CONFIG REQUIRED)

find_path(SDL3_GFX_INCLUDE_DIR
  NAMES SDL3_gfx/SDL3_gfxPrimitives.h
)
find_library(SDL3_GFX_LIBRARY
  NAMES SDL3_gfx sdl3_gfx sdl3-gfx
)

if(NOT SDL3_GFX_INCLUDE_DIR OR NOT SDL3_GFX_LIBRARY)
  message(FATAL_ERROR
    "SDL3_gfx was not found. Run ./build.sh or install the sdl3-gfx overlay port from ./ports.")
endif()

add_library(SDL3_gfx::SDL3_gfx UNKNOWN IMPORTED)
set_target_properties(SDL3_gfx::SDL3_gfx PROPERTIES
  IMPORTED_LOCATION "${SDL3_GFX_LIBRARY}"
  INTERFACE_INCLUDE_DIRECTORIES "${SDL3_GFX_INCLUDE_DIR}"
)

add_executable(sdl3_vcpkg_test
  src/App.cpp
  src/App.h
  src/main.cpp
)

set_target_properties(sdl3_vcpkg_test PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

target_link_libraries(sdl3_vcpkg_test PRIVATE
  SDL3::SDL3
  $<IF:$<TARGET_EXISTS:SDL3_image::SDL3_image-shared>,SDL3_image::SDL3_image-shared,SDL3_image::SDL3_image-static>
  SDL3_ttf::SDL3_ttf
  $<IF:$<TARGET_EXISTS:SDL3_mixer::SDL3_mixer>,SDL3_mixer::SDL3_mixer,SDL3_mixer::SDL3_mixer-static>
  SDL3_gfx::SDL3_gfx
)

add_custom_command(TARGET sdl3_vcpkg_test POST_BUILD
  COMMAND "${CMAKE_COMMAND}" -E copy_directory
          "${CMAKE_CURRENT_SOURCE_DIR}/res"
          "$<TARGET_FILE_DIR:sdl3_vcpkg_test>/res"
  VERBATIM
)

