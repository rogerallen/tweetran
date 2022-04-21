#include "../src/code.h"
#include "../src/utils.h"
#include "tests.h"

// a is value from test, b_str is the expected value
void test_compare(std::stringstream &a, std::string &b_str)
{
    if (a.str() == b_str) {
        // early return
        return;
    }
    // else find out where they differ
    std::stringstream b;
    std::string a_line, b_line;
    b << b_str;
    int line = 1;
    std::getline(b, b_line);
    if ((b_line.length() > 0) && (b_line[b_line.length() - 1] == '\r')) {
        b_line.pop_back();
    }
    std::getline(a, a_line);
    while (!b.eof()) { // b is assumed to be "good"
        if (a.eof()) {
            throw std::runtime_error("ERROR: line:" + std::to_string(line) + b_line + " != EOF\n");
        }
        else if (a_line != b_line) {
            throw std::runtime_error("ERROR on line:" + std::to_string(line) + "\nexpect: '" + b_line + "'\nactual: '" + a_line + "'\n");
        }
        std::getline(b, b_line);
        if ((b_line.length() > 0) && (b_line[b_line.length() - 1] == '\r')) {
            b_line.pop_back();
        }
        std::getline(a, a_line);
        line++;
    }
    if (line == 1) {
        throw std::runtime_error("ERROR: no lines in expected string!\n");
    }
}

void test_cuh(int i)
{
    std::stringstream iss;
    iss.fill('0');
    iss.width(2);
    iss << i;

    TEST_BEGIN(iss.str());

    std::string s = slurp("tests/test_" + iss.str() + ".clj");
    std::string r = slurp("tests/test_" + iss.str() + ".cuh"); // "golden"  files
    Code *g = new Code(s);
    std::stringstream out;
    g->cudaCodeGen(out);
    test_compare(out, r);
    TEST_END();
}

void test_frag(int i)
{
    std::stringstream iss;
    iss.fill('0');
    iss.width(2);
    iss << i;

    TEST_BEGIN(iss.str());

    std::string s = slurp("tests/test_" + iss.str() + ".clj");
    std::string r = slurp("tests/test_" + iss.str() + ".frag"); // "golden"  files
    Code *g = new Code(s);
    std::stringstream out;
    g->fragCodeGen(out);
    test_compare(out, r);
    TEST_END();
}

int main(int argc, char **argv)
{
    try {
        std::cout << "CUDA ===================\n";
        for (int i = 0; i <= 12; i++) {
            test_cuh(i);
        }

        std::cout << "FRAG ===================\n";
        for (int i = 0; i <= 12; i++) {
            test_frag(i);
        }

        std::cout << "========================\n";
        std::cout << "= = = TESTS PASSED = = =\n";
        std::cout << "========================" << std::endl;
        return (0);
    }
    catch (const std::exception &e) {
        std::cerr << "\n"
                  << e.what() << std::endl;
        return (1);
    }
}