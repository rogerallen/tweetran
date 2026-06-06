#include <emscripten.h>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include "code.h"
#include "utils.h"

extern "C" {

EMSCRIPTEN_KEEPALIVE
const char* transpile_to_glsl(const char* clj_code, const char* root_path) {
    try {
        std::string s(clj_code);
        std::string root(root_path);
        if (!root.empty() && root.back() != '/') {
            root += "/";
        }
        
        std::string uniforms = slurp(root + "webgl/uniforms.frag");
        std::string prefix = slurp(root + "webgl/prefix.frag");
        std::string noise = slurp(root + "webgl/noise.frag");
        std::string clisk = slurp(root + "webgl/clisk.frag");
        std::string suffix = slurp(root + "webgl/suffix.frag");
        
        Code g(s);
        std::stringstream out;
        g.fragCodeGen(out);
        
        std::string full_shader = uniforms + prefix + noise + clisk + out.str() + suffix;
        
        char* res = (char*)malloc(full_shader.size() + 1);
        strcpy(res, full_shader.c_str());
        return res;
    } catch (const std::exception& e) {
        std::string err = std::string("ERROR: ") + e.what();
        char* res = (char*)malloc(err.size() + 1);
        strcpy(res, err.c_str());
        return res;
    } catch (...) {
        const char* err = "ERROR: Unknown transpilation exception";
        char* res = (char*)malloc(strlen(err) + 1);
        strcpy(res, err);
        return res;
    }
}

EMSCRIPTEN_KEEPALIVE
const char* transpile_to_cpp_cuda(const char* clj_code) {
    try {
        std::string s(clj_code);
        Code g(s);
        std::stringstream out;
        g.cudaCodeGen(out);
        
        std::string code_str = out.str();
        char* res = (char*)malloc(code_str.size() + 1);
        strcpy(res, code_str.c_str());
        return res;
    } catch (const std::exception& e) {
        std::string err = std::string("ERROR: ") + e.what();
        char* res = (char*)malloc(err.size() + 1);
        strcpy(res, err.c_str());
        return res;
    } catch (...) {
        const char* err = "ERROR: Unknown transpilation exception";
        char* res = (char*)malloc(strlen(err) + 1);
        strcpy(res, err);
        return res;
    }
}

EMSCRIPTEN_KEEPALIVE
void free_string(char* ptr) {
    free(ptr);
}

}
