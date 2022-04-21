add_executable(parse parse.cpp ../src/code.cpp ../src/utils.cpp)
add_test(NAME parse WORKING_DIRECTORY .. COMMAND parse)
target_compile_features(parse PUBLIC cxx_std_11)