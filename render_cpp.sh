# download code, transpile and render via C++
# example: 
#   render_cpp.sh 220605_043024_D
if [ -z "$1" ]
then
    echo "No tweegeemee name supplied, exiting"
    exit
fi
TGM=$1
if [[ ! -f examples/${TGM}.clj ]]
then
    curl https://tweegeemee.com/i/${TGM}/code > examples/${TGM}.clj
fi
if [[ ! -f examples/${TGM}.cuh ]]
then
    ./build/src/gen_cuda examples/${TGM}.clj > examples/${TGM}.cuh
fi
# always compile
g++ -DGEN_CUDA_OUTPUT_FILE=\"../examples/${TGM}.cuh\" -I./cuda -fopenmp cpp/proto.cpp -o examples/c_tweetran_${TGM} -lgomp
examples/c_tweetran_${TGM} examples/${TGM}_cpp.png
echo see result in examples/${TGM}_cpp.png