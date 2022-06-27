if(MSVC)
    # msvc has W3 warnings in both of these flags by default.  Just change them to W4 to avoid a warning
	string(REPLACE "/W3" "/W4" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}" )
endif(MSVC)
if(CMAKE_COMPILER_IS_GNUCXX)
    # could not use add_compile_options() as that adds incorrectly to CUDA, too.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")
endif(CMAKE_COMPILER_IS_GNUCXX)

find_package(OpenMP)

# proto C++
add_executable(c_tweetran_test_12 proto.cpp ../src/utils.cpp)
target_compile_definitions(c_tweetran_test_12 PUBLIC 
    GEN_CUDA_OUTPUT_FILE="${CMAKE_CURRENT_SOURCE_DIR}/../tests/test_12.cuh")
target_include_directories(c_tweetran_test_12 PUBLIC ../cuda)
target_compile_features(c_tweetran_test_12 PUBLIC cxx_std_11)
if(OpenMP_CXX_FOUND)
    target_link_libraries(c_tweetran_test_12 PUBLIC OpenMP::OpenMP_CXX)
endif()