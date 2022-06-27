# download code, transpile and render via cuda
# example: 
#   render_cuda.sh 220605_043024_D
TGM=$1
if [[ ! -f examples/${TGM}.clj ]]
then
    curl https://tweegeemee.com/i/${TGM}/code > examples/${TGM}.clj
fi
if [[ ! -f examples/${TGM}.cuh ]]
then
    ./build/src/gen_cuda examples/${TGM}.clj > examples/${TGM}.cuh
fi
./build/cuda/cu_retwee examples/${TGM}.cuh examples/${TGM}_cu.png