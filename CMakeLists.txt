# Testing on Ubuntu 20.04 which has cmake 3.16
cmake_minimum_required(VERSION 3.16)

# FIXME make CUDA optional

project(tweetran
    VERSION     0.1
    DESCRIPTION "tweetran"
    LANGUAGES   CUDA CXX
)

add_subdirectory(src)
add_subdirectory(cuda)
add_subdirectory(cpp)

enable_testing()
add_subdirectory(tests) 
