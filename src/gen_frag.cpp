#include "code.h"
#include "utils.h"

#include <string>

int main(int argc, char **argv)
{
    bool print_everything = true;
    std::string root = "";
    int i = 1;
    for (; i < argc; i++) {
        std::string arg = std::string(argv[i]);
        if (arg == "-1") {
            print_everything = false;
        }
        else if (arg == "-r") {
            root = std::string(argv[++i]) + "/";
        }
        else if (arg[0] == '-') {
            std::cerr << "ERROR: usage: gen_frag [-1] [-r ceegeemee_root] filename.clj" << std::endl;
            std::exit(1);
        }
    }
    std::string s = slurp(argv[i - 1]);

    std::string uniforms = slurp(root + "webgl/uniforms.frag");
    std::string prefix = slurp(root + "webgl/prefix.frag");
    std::string noise = slurp(root + "webgl/noise.frag");
    std::string clisk = slurp(root + "webgl/clisk.frag");
    std::string suffix = slurp(root + "webgl/suffix.frag");

    Code *g = new Code(s);
    std::stringstream out;
    g->fragCodeGen(out);

    if (print_everything) {
        std::cout << uniforms << prefix << noise << clisk;
    }
    std::cout << out.str();
    if (print_everything) {
        std::cout << suffix;
    }
}
