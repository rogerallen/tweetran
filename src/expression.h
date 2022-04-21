#ifndef EXPRESSION_H
#define EXPRESSION_H

#include <cmath>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "expressions.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Expression can be either functions or atoms.
// Expressions are gathered into collections called blocks.
// Blocks are output as separate functions.
class Expression {
    bool mIsFunction;              // true if function, false if atom
    bool mIsTerminalFunction;      // true if terminal function.  will be atom
    std::string mLabel;            // name of function or atom value
    std::vector<Expression> mArgs; // if function, the arguments for it

    int mId;         // unique, ordered ID to use for either functions and atoms
    int mFunctionId; // unique, ordered ID to use only for functions
    int mBlockId;    // unique, ordered ID to use for blocks
    int mMaxId;
    int mMaxFunctionId;
    int mMaxBlockId;
    std::vector<float> mAtomValues;

    // internal helper function to add pos as an input to functions
    // that affect position
    void fixPosFunctions()
    {
        if (mIsFunction) {
            if (gAddPos.find(mLabel) != gAddPos.end()) {
                mArgs.insert(mArgs.begin(), Expression("pos"));
            }
        }
        for (unsigned i = 0; i < mArgs.size(); i++) {
            mArgs[i].fixPosFunctions();
        }
    }

    // internal helper function to assign ids to functions & atoms
    void assignIds(int *id, int *functionId, int *blockId, int curBlockId)
    {
        mId = (*id)++;
        mFunctionId = (mIsFunction) ? (*functionId)++ : -1;
        mBlockId = curBlockId;
        // printf("aid %s %d\n", mLabel.c_str(), mBlockId);
        bool modPos = false;
        if (mIsFunction) {
            if (gModPos.find(mLabel) != gModPos.end()) {
                // modify for pos means add a new BlockId
                modPos = true;
            }
        }
        for (unsigned i = 0; i < mArgs.size(); i++) {
            if (modPos && (i == mArgs.size() - 1)) {
                if ((mArgs[i].mIsFunction || mArgs[i].mIsTerminalFunction)) {
                    // the last arg in a modPos fn args is part of the next function
                    (*blockId) += 1;
                    // printf("ai1 %s %d %d\n", mArgs[i].mLabel.c_str(), *blockId, *blockId);
                    mArgs[i].assignIds(id, functionId, blockId, *blockId);
                }
                else {
                    // the last arg *should* be a fn, but it isn't.
                    if (mArgs[i].mLabel == "pos") {
                        // change this to the "unity" function
                        mArgs[i].mLabel = "unity";
                        mArgs[i].assignIds(id, functionId, blockId, curBlockId);
                    }
                    else {
                        // okay this function  is bogus
                        std::cerr << "WARNING: Last argument to " << mLabel << "was" << mLabel << ".  Changing to unity.\n";
                        // change this whole function to just return this value
                        mLabel = "unity";
                        // okay you wasted work on those earlier args
                        mArgs.erase(mArgs.begin(), mArgs.begin() + 2);
                    }
                }
            }
            else {
                // other fn & atom args are part of this function
                // printf("ai2 %s %d %d\n", mArgs[i].mLabel.c_str(), *blockId, curBlockId);
                mArgs[i].assignIds(id, functionId, blockId, curBlockId);
            }
        }
    }

    // internal helper to assign mAtomValues
    void assignValues()
    {
        if (mIsFunction) {
            for (unsigned i = 0; i < mArgs.size(); i++) {
                mArgs[i].assignValues();
            }
        }
        else {
            std::istringstream iss(mLabel);
            std::vector<std::string> results((std::istream_iterator<std::string>(iss)),
                                             std::istream_iterator<std::string>());
            for (auto r : results) {
                if (r == "pos") {
                    // leave pos alone
                    continue;
                }
                else if (r == "PI") {
                    mAtomValues.push_back(M_PI);
                }
                else if (r == "TAU") {
                    mAtomValues.push_back(2 * M_PI);
                }
                else if (mIsTerminalFunction) {
                    // printf("assignValues termfn %s\n", r.c_str());
                    continue;
                }
                else if ((r != "[") && (r != "]")) {
                    mAtomValues.push_back((float)atof(r.c_str()));
                }
            }
        }
    }

  public:
    // given a string and starting token index parse the tokens for your expression tree,
    // modifying the token index.
    Expression(std::vector<std::string> &tokens, int *tokenIndex)
    {
        int i = *tokenIndex;
        int bug23count = 0;
        if (tokens[i++] == "(") {
            mLabel = tokens[i++];
            while (mLabel == "(") {
                // tweegeemee bug 23 - exta parens, sometimes
                mLabel = tokens[i++];
                bug23count++;
            }
            if (mLabel.substr(0, 11) == "clisk.live/") {
                mLabel.erase(0, 11);
            }
            if (gFunctionRename[mLabel] == "") {
                std::cerr << "ERROR: Unknown Function: " << mLabel << std::endl;
            }
            mIsFunction = true;
            while (tokens[i] != ")") {
                mArgs.push_back(Expression(tokens, &i));
            }
            i++;
            while (bug23count > 0) {
                i++;
                bug23count--;
            }
        }
        else {
            i--;
            mLabel = tokens[i++];
            if (mLabel.substr(0, 11) == "clisk.live/") {
                mLabel.erase(0, 11);
            }
            mIsFunction = false;
            mIsTerminalFunction = (gTermFns.find(mLabel) != gTermFns.end());
        }
        *tokenIndex = i;
        mId = -1;
        mFunctionId = -1;
        mBlockId = -1;
        mMaxId = -1;
        mMaxFunctionId = -1;
        mMaxBlockId = -1;
    }
    // this variant is used to insert "pos" as an argument in fixPosFunctions
    Expression(std::string token)
    {
        mLabel = token;
        mIsFunction = false;
        mId = -1;
        mFunctionId = -1;
        mBlockId = -1;
        mMaxId = -1;
        mMaxFunctionId = -1;
        mMaxBlockId = -1;
    }

    void printDebugInfo(int level)
    {
        if (level == 0)
            printf("\n");
        for (int i = 0; i < level; ++i) {
            printf("  ");
        }
        printf("%s id=%d fid=%d bid=%d\n", mLabel.c_str(), mId, mFunctionId, mBlockId);
        for (unsigned i = 0; i < mArgs.size(); i++) {
            mArgs[i].printDebugInfo(level + 1);
        }
    }

    // FIXME private fn
    // assign ids to functions
    void postProcess()
    {
        fixPosFunctions();
        // printDebugInfo(0);
        int i = 0, fi = 0, bi = 0;
        assignIds(&i, &fi, &bi, bi);
        // printDebugInfo(0);
        mMaxId = i;
        mMaxFunctionId = fi;
        mMaxBlockId = bi;
        assignValues();
    }

    // return cuda variable name for this function or the value of the atom
    std::string cudaVariableName()
    {
        if (mLabel == "pos") {
            return "pos";
        }
        else if (mIsFunction || mIsTerminalFunction) {
            return "var" + std::to_string(mId);
        }
        else {
            return "atom" + std::to_string(mId);
        }
    }

    void
    cudaCodeGen1(std::stringstream &out, int level, int blockNumber, std::string &lastVarName)
    {
        for (unsigned i = 0; i < mArgs.size(); i++) {
            mArgs[i].cudaCodeGen1(out, level + 1, blockNumber, lastVarName);
        }
        if (mBlockId == blockNumber) {
            if (mIsFunction) {
                lastVarName = cudaVariableName();
                out << "    vfloat " << cudaVariableName() << " = " << gFunctionRename[mLabel] + "(";
                if (mArgs.size() > 0) {
                    unsigned i = 0;
                    out << mArgs[i++].cudaVariableName();
                    for (; i < mArgs.size(); i++) {
                        if (gModPos.find(mLabel) != gModPos.end()) {
                            if (i == mArgs.size() - 1) {
                                if (mArgs[i].mIsFunction) {
                                    // last argument is a function
                                    out << ", pixel_fn" << mArgs[i].mBlockId;
                                }
                                else {
                                    // last argument is NOT a function.  I hope we fixed the label.
                                    out << ", " << mArgs[i].mLabel;
                                }
                            }
                            else {
                                out << ", " << mArgs[i].cudaVariableName();
                            }
                        }
                        else {
                            out << ", " << mArgs[i].cudaVariableName();
                        }
                    }
                }
                out << ");\n";
            }
            else { // Atom
                if (cudaVariableName() == "pos") {
                    return;
                }
                lastVarName = cudaVariableName();
                out << "    vfloat " << cudaVariableName() << " = ";
                if (mIsTerminalFunction) {
                    out << gFunctionRename[mLabel] << "(pos);\n";
                }
                else {
                    out << "vfloat( ";
                    unsigned int i = 0;
                    for (auto a : mAtomValues) {
                        out << a;
                        if (++i != mAtomValues.size()) {
                            out << ", ";
                        }
                    }
                    out << " );\n";
                }
            }
        }
    }

    // FIXME call this at construction time & store it in a string
    void cudaCodeGen(std::stringstream &out)
    {
        for (int i = mMaxBlockId; i >= 0; i--) {
            out << "__device__ vfloat pixel_fn" << i << "(vfloat pos)\n{\n";
            std::string lastVar;
            cudaCodeGen1(out, 0, i, lastVar);
            out << "    return " << lastVar << ";\n";
            out << "}\n";
        }
    }

    static void fragOffsetFnGen(std::stringstream &out, std::string fn_name)
    {
        out << "vfloat offset_" << fn_name << "(vfloat pos, vfloat offset)\n";
        out << "{\n";
        out << "    vec4 o = get_vec4(offset);\n";
        out << "    vfloat pos1 = make_vfloat(pos.v + o);\n";
        out << "    vfloat var0 = " << fn_name << "(pos1);\n";
        out << "    return var0;\n";
        out << "}\n";
    }

    static void fragScaleFnGen(std::stringstream &out, std::string fn_name)
    {
        out << "vfloat scale_" << fn_name << "(vfloat pos, vfloat scale)\n";
        out << "{\n";
        out << "    vec4 s = smear_vec4(scale);\n";
        out << "    vec4 oos = 1.0 / s;\n";
        out << "    vfloat pos1 = make_vfloat(pos.v * oos);\n";
        out << "    vfloat var0 = " << fn_name << "(pos1);\n";
        out << "    return var0;\n";
        out << "}\n";
    }

    static void fragRotateFnGen(std::stringstream &out, std::string fn_name)
    {
        out << "vfloat rotate_" << fn_name << "(vfloat pos, vfloat angle)\n";
        out << "{\n";
        out << "    float a = angle.v.x;\n";
        out << "    float x = pos.v.x;\n";
        out << "    float y = pos.v.y;\n";
        out << "    float z = pos.v.z;\n";
        out << "    float t = pos.v.w;\n";
        out << "    vfloat pos1 = make_vfloat(x * cos(a) - y * sin(a), y * cos(a) + x * sin(a), z, t);\n";
        out << "    vfloat var0 = " << fn_name << "(pos1);\n";
        out << "    return var0;\n";
        out << "}\n";
    }

    static void fragGradientFnGen(std::stringstream &out, std::string fn_name)
    {
        out << "vfloat gradient_" << fn_name << "(vfloat pos)\n";
        out << "{\n";
        out << "    float epsilon = 0.0001;\n";
        out << "    float oo_epsilon = 1.0 / epsilon;\n";
        out << "    vfloat pos_dx = make_vfloat(pos.v.x + epsilon, pos.v.y, pos.v.z, pos.v.w);\n";
        out << "    vfloat pos_dy = make_vfloat(pos.v.x, pos.v.y + epsilon, pos.v.z, pos.v.w);\n";
        out << "    vfloat pos_dz = make_vfloat(pos.v.x, pos.v.y, pos.v.z + epsilon, pos.v.w);\n";
        out << "    vfloat pos_dw = make_vfloat(pos.v.x, pos.v.y, pos.v.z, pos.v.w + epsilon);\n";
        out << "    vfloat var1 = " << fn_name << "(pos);\n";
        out << "    vfloat var1_dx = " << fn_name << "(pos_dx);\n";
        out << "    vfloat var1_dy = " << fn_name << "(pos_dy);\n";
        out << "    vfloat var1_dz = " << fn_name << "(pos_dz);\n";
        out << "    vfloat var1_dw = " << fn_name << "(pos_dw);\n";
        out << "    float var0_dx = (var1_dx.v.x - var1.v.x) * oo_epsilon;\n";
        out << "    float var0_dy = (var1_dy.v.y - var1.v.y) * oo_epsilon;\n";
        out << "    float var0_dz = (var1_dz.v.z - var1.v.z) * oo_epsilon;\n";
        out << "    float var0_dw = (var1_dw.v.w - var1.v.w) * oo_epsilon;\n";
        out << "    vfloat var0 = make_vfloat(var0_dx, var0_dy, var0_dz, var0_dw);\n";
        out << "    return var0;\n";
        out << "}\n";
    }

    static void fragMakeMultiFractalFnGen(std::stringstream &out, std::string fn_name)
    {
        out << "vfloat make_multi_fractal_" << fn_name << "(vfloat pos)\n";
        out << "{\n";
        out << "    float octaves = 8.0;\n";
        out << "    float lacunarity = 2.0;\n";
        out << "    float gain = 0.5;\n";
        out << "    float scale = 0.5;\n";
        out << "    vfloat sum = make_vfloat(0.0, 0.0, 0.0, 0.0);\n";
        out << "    for (float octave = 0.0; octave < octaves; octave += 1.0) {\n";
        out << "        float pos_scale = pow(lacunarity, octave);\n";
        out << "        vfloat pos1 = make_vfloat(pos.v * pos_scale);\n";
        out << "        vfloat val = " << fn_name << "(pos1);\n";
        out << "        float val_scale = scale * pow(gain, octave);\n";
        out << "        val = make_vfloat(val.v * val_scale);\n";
        out << "        sum = make_vfloat(sum.v + val.v);\n";
        out << "    }\n";
        out << "    return sum;\n";
        out << "}\n";
    }

    // FIXME turbulate

    // generate scale/offset type functions (only) prior to the current blockNumber
    void fragCodeGen0(std::stringstream &out, int level, int blockNumber)
    {
        for (unsigned i = 0; i < mArgs.size(); i++) {
            mArgs[i].fragCodeGen0(out, level + 1, blockNumber);
        }
        if (mBlockId == blockNumber) {
            if (mIsFunction) {
                if (gModPos.find(mLabel) != gModPos.end()) {
                    std::string fn_name = "pixel_fn" + std::to_string(mArgs[mArgs.size() - 1].mBlockId);
                    if (mLabel == "offset") {
                        fragOffsetFnGen(out, fn_name);
                    }
                    else if (mLabel == "scale") {
                        fragScaleFnGen(out, fn_name);
                    }
                    else if (mLabel == "rotate") {
                        fragRotateFnGen(out, fn_name);
                    }
                    else if (mLabel == "gradient") {
                        fragGradientFnGen(out, fn_name);
                    }
                    // FIXME more types
                }
            }
        }
    }

    void
    fragCodeGen1(std::stringstream &out, int level, int blockNumber, std::string &lastVarName)
    {
        for (unsigned i = 0; i < mArgs.size(); i++) {
            mArgs[i].fragCodeGen1(out, level + 1, blockNumber, lastVarName);
        }
        if (mBlockId == blockNumber) {
            if (mIsFunction) {
                lastVarName = cudaVariableName();
                out << "    vfloat " << cudaVariableName() << " = ";
                if (gModPos.find(mLabel) != gModPos.end()) {
                    out << gFunctionRename[mLabel] + "_pixel_fn" << mArgs[mArgs.size() - 1].mBlockId << "(";
                }
                else {
                    out << gFunctionRename[mLabel] << "(";
                }
                if (mArgs.size() > 0) {
                    unsigned i = 0;
                    out << mArgs[i++].cudaVariableName();
                    for (; i < mArgs.size(); i++) {
                        if (gModPos.find(mLabel) != gModPos.end()) {
                            if (i == mArgs.size() - 1) {
                                // last argument is a function in CUDA, but not in frag shader
                                // out << ", pixel_fn" << mArgs[i].mBlockId;
                                ;
                            }
                            else {
                                out << ", " << mArgs[i].cudaVariableName();
                            }
                        }
                        else {
                            out << ", " << mArgs[i].cudaVariableName();
                        }
                    }
                }
                out << ");\n";
            }
            else { // Atom
                if (cudaVariableName() == "pos") {
                    return;
                }
                lastVarName = cudaVariableName();
                out << "    vfloat " << cudaVariableName() << " = ";
                if (mIsTerminalFunction) {
                    out << gFunctionRename[mLabel] << "(pos);\n";
                }
                else {
                    out << "make_vfloat( ";
                    unsigned int i = 0;
                    for (auto a : mAtomValues) {
                        out << a;
                        if (++i != mAtomValues.size()) {
                            out << ", ";
                        }
                    }
                    out << " );\n";
                }
            }
        }
    }

    // what do we call this block of code?
    std::string fragFunctionSignature(int i)
    {
        std::string v = "vfloat pixel_fn" + std::to_string(i) + "(vfloat pos)";
        return v;
    }

    // FIXME call this at construction time & store it in a string
    void fragCodeGen(std::stringstream &out)
    {
        // No confusing GLSL with integers instead of floats
        out.setf(std::ios::showpoint);
        out.setf(std::ios::fixed, std::ios::floatfield);
        out.precision(5);

        out << "// --------------------------------------------------------------------------------\n";

        for (int i = mMaxBlockId; i >= 0; i--) {
            fragCodeGen0(out, 0, i);
            out << fragFunctionSignature(i) << "\n{\n";
            std::string lastVar;
            fragCodeGen1(out, 0, i, lastVar);
            out << "    return " << lastVar << ";\n";
            out << "}\n";
        }
    }
};

#endif