#!/bin/bash
set -e

# Setup Emscripten environment
echo "Sourcing emsdk_env.sh..."
source /home/rallen/Documents/Devel/emscripten/emsdk/emsdk_env.sh

# Compile
echo "Compiling WebAssembly..."
emcc -O3 -std=c++11 \
  -I../src \
  transpiler_wasm.cpp ../src/code.cpp ../src/utils.cpp \
  -s WASM=1 \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="createTranspilerModule" \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap", "UTF8ToString", "stringToUTF8"]' \
  -s EXPORTED_FUNCTIONS='["_transpile_to_glsl", "_transpile_to_cpp_cuda", "_free_string", "_malloc", "_free"]' \
  --embed-file ../webgl@/webgl \
  -o transpiler.js

echo "Build complete! Generated transpiler.js and transpiler.wasm"
