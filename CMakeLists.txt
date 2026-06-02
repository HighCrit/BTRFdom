cmake_minimum_required(VERSION 3.16)

project(BTRFdom VERSION 1.0 LANGUAGES CXX)

enable_testing()

set(CMAKE_VERBOSE_MAKEFILE ON)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

# C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Shared libraries without "lib" prefix
set(CMAKE_SHARED_LIBRARY_PREFIX "")

# Optional build type
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

if(MSVC)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)

    add_link_options(
        /MANIFEST:NO
        /INCREMENTAL:NO
    )
else()
    add_compile_options(
        -Wall
        -Wextra
    )

    if(MINGW)
        add_link_options(
            -static-libgcc
            -static-libstdc++
            -Wl,--add-stdcall-alias
        )
    endif()

    # Legacy compatibility define used by old Qt Creator projects
    add_compile_definitions(__GXX_EXPERIMENTAL_CXX0X__)
endif()

# Runtime library search path on Unix-like systems
if(UNIX AND NOT APPLE)
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
    set(CMAKE_BUILD_RPATH "$ORIGIN")
endif()

# Dependencies
# Disabled test since original git sub-module has been deleted.
# add_subdirectory(gtest)
add_subdirectory(shared-lib)
add_subdirectory(dll-client-cpp)
# add_subdirectory(dll-test-cpp)