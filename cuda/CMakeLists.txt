# Testing on Ubuntu 20.04 which has cmake 3.16
cmake_minimum_required(VERSION 3.16)

include(CheckLanguage)
check_language(CUDA)

if(MSVC)
    # msvc has W3 warnings in both of these flags by default.  Just change them to W4 to avoid a warning
	string(REPLACE "/W3" "/W4" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}" )
	string(REPLACE "/W3" "/W4" CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS}" )
endif(MSVC)
if(CMAKE_COMPILER_IS_GNUCXX)
    # could not use add_compile_options() as that adds incorrectly to CUDA, too.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")
    # adding -pedantic to CUDA made for way too much spew.
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -Xcompiler -Wall,-Wextra")
endif(CMAKE_COMPILER_IS_GNUCXX)

# add gencode targets
# FIXME--how to manage this properly?
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch sm_61 -gencode=arch=compute_61,code=sm_61 -gencode=arch=compute_75,code=sm_75 -gencode=arch=compute_86,code=sm_86")
# CUDA wants C++11
if(NOT DEFINED CMAKE_CUDA_STANDARD)
    set(CMAKE_CUDA_STANDARD 11)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)
endif()

# proto CUDA
add_executable(proto proto.cu ../src/utils.cpp)
target_compile_features(proto PUBLIC cxx_std_11)
target_include_directories(proto PUBLIC "${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}")
if(CMAKE_COMPILER_IS_GNUCXX)
target_link_libraries(proto PRIVATE cuda cudart nvrtc)
endif(CMAKE_COMPILER_IS_GNUCXX)
if(MSVC)
target_link_libraries(proto PRIVATE cuda cudart nvrtc Dbghelp)
endif(MSVC)
