#include "code.h"
#include "utils.h"

int main(int argc, char **argv)
{
    assert(argc = 1);
    std::string s = slurp(argv[1]);
    Code *g = new Code(s);
    // std::cout << g->debugString() << std::endl;
    std::stringstream out;
    g->cudaCodeGen(out);
    std::cout << out.str();
}
