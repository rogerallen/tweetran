#ifndef CODE_H
#define CODE_H

#include <algorithm>
#include <assert.h>
#include <cmath>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

#include "expression.h"

class Code {
    std::string mOriginalString;
    std::string mNormalizedString;
    std::vector<std::string> mTokenizedString;
    Expression *mRootExpression;
    void normalize();
    void tokenize();
    void parse();

    void debugTokens()
    {
        std::cout << "\n";
        for (auto t : mTokenizedString) {
            std::cout << "token: " << t << std::endl;
        }
    }

  public:
    Code(const std::string &s);
    // FIXME std::string getCudaCode() is better
    void cudaCodeGen(std::stringstream &out) { mRootExpression->cudaCodeGen(out); }
    void fragCodeGen(std::stringstream &out) { mRootExpression->fragCodeGen(out); }
    std::string source() { return mOriginalString; }
};

#endif