# tweetran - the tweegeemee Transpiler library

Code to transpile the [tweegeemee](https://twitter.com/tweegeemee) Clojure [Clisk library](https://github.com/mikera/clisk) code into other languages.  This will only work for functions that tweegeemee uses and in the format that tweegeemee generates.  The code is a work in progress, *alpha* quality.  And I am very far from a transpiler expert.  Failures happen quite often.  

The primary benefit of this code is that CUDA and WebGL both use the GPU and it can render tweegeemee images *much* faster than the CPU.  Interactive frame rates are possible.  A C++ CPU-only version is also available, but it isn't as fast.

While images often can be exactly as they are generated by the Clojure Clisk library, there are some exceptions and there is no guarantee of perfect matching.

## Usage

The programs in this directory are meant to be examples of how to use the library for use by programmers and are not expected to be used by non-technical end-users.  

At this point, my suggestion is to read the code to understand how to use it.  I'll add some instructions later.

This project was first developed on Linux and relies on Linux & Python to fully build, but there is a Windows Visual Studio 2022 solution file in the `win_vs22` directory that allows you to build & run executables on Windows.

## Tweegeemee code

Find images via [tweegeemee](https://twitter.com/tweegeemee) and https://tweegeemee.com 

Code for an image can be found in the image detail URL.  For example, the image for [this tweet](https://twitter.com/tweegeemee/status/1533259993029529600) can be retrieved like this: 

`curl https://tweegeemee.com/i/220605_013038_C/code > examples/220605_013038_C.clj`

That code happens to be: `(vsqrt (vsqrt (adjust-hue 0.2599296003519858 pos)))`

This library converts that code into programs the can run in CUDA, C++ and WebGL.

## Languages

### CUDA

The `render_cuda.sh` script puts download, transpile and png-creation all in one script.  For example:

`./render_cuda.sh 220605_013038_C`

#### gen_cuda

*gen_cuda* is a program to take the Clojure (clj) code that generates tweegeemee images and transpile it to CUDA.  This cuda code relies on the `cuda/clisk.cuh` library code.

Example:

`./build/src/gen_cuda examples/220605_013038_C.clj > examples/220605_013038_C.cuh`

#### cu_tweetran

*cu_tweetran* is an example program that uses CUDA to generate a PNG file.  It is a simple program
that you could modify for your own use cases.  See the code for various things you can control.

`./build/cuda/cu_tweetran examples/220605_013038_C.cuh examples/220605_013038_C.png`

Note: If you are not running from the root of this project, use JITIFY_OPTIONS to point to 
where the `cuda` directory is.

`JITIFY_OPTIONS="-I/path/to/this/tweegeemeetranspiler" cu_tweetran infile.cuh image.png`

### C++

See the CUDA/gen_cuda section above about how to output .cuda header (.cuh) files.

*c_tweetran_test_12* is packaged as an example.  In C++, the header file including the CUDA code is compiled along with the proto.cpp file to create an executable per tweegeemee image.  There is an example using the `tests/test_12.cuh` file.

`./build/cpp/c_tweetran_test_12`

The `render_cpp.sh` script puts download, compile & transpile and png-creation all in one script.  For example:

`./render_cpp.sh 220605_013038_C`

### WebGL

#### index.html & proto.js

`webgl/index.html` and `webgl/proto.js` are an example program that uses WebGL to generate an *interactive* tweegeemee image.  It is a simple prototype that you could modify for your own use cases.  See the web page & the source code for various things you can control.  You have to run your own web server to visit this web page.  Like:

```
$ cd webgl
$ python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Then open up http://0.0.0.0:8000/ on your web browser to see some test images that you can pan (click-drag), zoom (mousewheel) and animate (click the button)!

#### gen_frag

*gen_frag* is a program to take the Clojure (clj) code that generates tweegeemee images and transpile it to WebGL.  This WebGL code relies on the `webgl/clisk.frag` (and other files) library code.

Example:

`./build/src/gen_frag examples/220605_013038_C.clj > webgl/proto/220605_013038_C.frag`

At the top of `webgl/proto.js` is an array `frag_shaders` which lists the files you can view interactively in the browser.  Add `"proto/220605_013038_C.frag"` to that array in order to view this example.

## Testing

There are some parsing tests that run under ctest.

## License

Like the Clisk Library, code in this repository is LGPL 3.0.  http://www.gnu.org/licenses/lgpl-3.0.html
