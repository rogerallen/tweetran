#include "utils.h"
#include <fstream>
#include <iostream>
#include <vector>

std::string slurp(const std::string &fileName)
{
    std::ifstream ifs(fileName.c_str(), std::ios::in | std::ios::binary | std::ios::ate);
    if (!ifs.is_open()) {
        std::cerr << "ERROR: " << fileName << " does not exist." << std::endl;
        return "";
    }

    std::ifstream::pos_type fileSize = ifs.tellg();
    ifs.seekg(0, std::ios::beg);

    std::vector<char> bytes(fileSize);
    ifs.read(bytes.data(), fileSize);

    return std::string(bytes.data(), fileSize);
}
