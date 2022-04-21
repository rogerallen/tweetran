#include "code.h"
#include <cctype>

bool nilOrBlank(std::string &s)
{
    return s == "" || s == " ";
}

Code::Code(const std::string &s)
{
    mOriginalString = s;
    // std::cout << "\noriginal input: " << mOriginalString << "\n";
    mNormalizedString = "";
    normalize();
    // std::cout << "\nnormalized input: " << mNormalizedString << "\n";
    tokenize();
    // debugTokens();
    parse();
}

// Update mNormalizedString.  Adjust whitespace to be single-space and
// remove comments
void Code::normalize()
{
    bool commentMode = false;
    bool whitespaceMode = false;
    for (unsigned i = 0; i < mOriginalString.size(); i++) {
        char curChar;
        curChar = mOriginalString[i];

        // remove ;; comments
        if (commentMode) {
            // windows uses '\r\n', so this still works
            if (curChar == '\n') {
                commentMode = false;
            }
        }
        // order allows for both comment && whitespace mode
        else if (curChar == ';') {
            commentMode = true;
            i++;
        }
        else if (whitespaceMode) {
            if (!std::isspace(curChar)) {
                whitespaceMode = false;
                i--; // go back and re-try (comment issue)
            }
        }
        else if (std::isspace(curChar)) {
            // We don't have to worry about strings, so just take out all whitespace
            // and make into a single space.
            mNormalizedString += " ";
            whitespaceMode = true;
        }
        else {
            mNormalizedString += curChar;
        }
    }
}

// convert mNormalizedString into a vector of string tokens in mTokenizedString
void Code::tokenize()
{
    std::string cur = "";
    bool ignoreSpaces = false;
    for (unsigned i = 0; i < mNormalizedString.length(); i++) {
        if (mNormalizedString[i] == '(') {
            mTokenizedString.push_back("(");
        }
        else if (mNormalizedString[i] == ')') {
            if (!nilOrBlank(cur)) {
                mTokenizedString.push_back(cur);
                cur = "";
            }
            mTokenizedString.push_back(")");
        }
        else if (mNormalizedString[i] == '[') {
            ignoreSpaces = true;
            cur += std::string(1, mNormalizedString[i]) + " ";
        }
        else if (mNormalizedString[i] == ']') {
            ignoreSpaces = false;
            cur += " " + std::string(1, mNormalizedString[i]);
            if (!nilOrBlank(cur)) {
                mTokenizedString.push_back(cur);
                cur = "";
            }
        }
        else if (!ignoreSpaces && mNormalizedString[i] == ' ') {
            if (!nilOrBlank(cur)) {
                mTokenizedString.push_back(cur);
                cur = "";
            }
        }
        else {
            cur += mNormalizedString[i];
        }
    }
}

// parse mTokenizedString into an Expression Tree
void Code::parse()
{
    int curToken = 0;
    mRootExpression = new Expression(mTokenizedString, &curToken);
    mRootExpression->postProcess(); // FIXME?
    // mRootExpression->debugCodeGen();
}
