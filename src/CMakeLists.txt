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

# pre-make expressions.h file
add_custom_command(
    OUTPUT  ${CMAKE_CURRENT_SOURCE_DIR}/expressions.h
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/gen_expressions.py > expressions.h
    DEPENDS
        ${CMAKE_CURRENT_SOURCE_DIR}/gen_expressions.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
add_custom_target(expressions_header
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/expressions.h
)

# generate CUDA
add_executable(gen_cuda gen_cuda.cpp code.cpp utils.cpp)
add_dependencies(gen_cuda expressions_header)
target_compile_features(gen_cuda PUBLIC cxx_std_11)

# generate Fragment Shader
add_executable(gen_frag gen_frag.cpp code.cpp utils.cpp)
add_dependencies(gen_frag expressions_header)
target_compile_features(gen_frag PUBLIC cxx_std_11)
