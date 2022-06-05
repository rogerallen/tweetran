# download code, transpile and render via cuda
# example: 
#   render_cuda.sh 220605_043024_D
TGM=$1
curl https://tweegeemee.com/i/${TGM}/code > examples/${TGM}.clj
./build/src/gen_cuda examples/${TGM}.clj > examples/${TGM}.cuh
./build/cuda/proto examples/${TGM}.cuh examples/${TGM}.png