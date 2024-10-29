# Set the minimum version of CMake required
cmake_minimum_required(VERSION 3.10)

# Set the project name
project(MyProject)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add the executable target
add_executable(MyExecutable main.cpp)

# Optionally, add include directories
target_include_directories(MyExecutable PRIVATE include)
