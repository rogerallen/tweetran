# tweegeemee Transpiler

Code to transpile the Clojure Clisk library code that creates the [tweegeemee](https://twitter.com/tweegeemee) images into other languages.  This will only work for functions that tweegeemee uses
and in the format that tweegeemee generates.  The code is a work in progress, *alpha* quality.  Failures happen quite often.  

CUDA and WebGL both use the GPU and it can render tweegeemee images *much* faster than the CPU.

## Tweegeemee code

Find images via [tweegeemee](https://twitter.com/tweegeemee) and https://tweegeemee.com 

Code for an image can be found in the image detail URL.  For example: 

`curl https://tweegeemee.com/i/220605_013038_C/code > examples/220605_013038_C.clj`

## Languages

### CUDA

#### gen_cuda

*gen_cuda* is a program to take the Clojure (clj) code that generates tweegeemee images and transpile it to CUDA.  This cuda code relies on the `cuda/clisk.cuh` library code.

Example:

`./build/src/gen_cuda examples/220605_013038_C.clj > examples/220605_013038_C.cuh`

#### proto 

*proto* is an example program that uses CUDA to generate a PNG file.  It is a simple program
that you could modify for your own use cases.  See the code for various things you can control.

`./build/cuda/proto examples/220605_013038_C.cuh examples/220605_013038_C.png`

Note: If you are not running from the root of this project, use JITIFY_OPTIONS to point to 
where the `cuda` directory is.

`JITIFY_OPTIONS="-I/path/to/this/tweegeemeetranspiler" proto infile.cuh image.png`

### WebGL

## Testing