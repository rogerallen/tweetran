/*

Originally based on https://github.com/Pseudomanifold/Aleph/blob/master/tests/Base.hh.in
found via this blog post http://bastian.rieck.me/blog/posts/2017/simple_unit_tests/
that file is licensed as:

Copyright (c) 2016 Bastian Rieck

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/
#ifndef TESTS_BASE_HH__
#define TESTS_BASE_HH__

#include <iostream>
#include <stdexcept>
#include <string>

#define ASSERT_EQUAL(x, y)                                                                                                                                                                                                                         \
    {                                                                                                                                                                                                                                              \
        if ((x) != (y)) {                                                                                                                                                                                                                          \
            throw std::runtime_error(std::string(__FILE__) + std::string(":") + std::to_string(__LINE__) + std::string(" in ") + std::string(__FUNCTION__) + std::string(": ") + std::to_string((x)) + std::string(" != ") + std::to_string((y))); \
        }                                                                                                                                                                                                                                          \
    }

#define ASSERT_STRING_EQUAL(x, y)                                                                                                                                                                                  \
    {                                                                                                                                                                                                              \
        if ((x) != (y)) {                                                                                                                                                                                          \
            throw std::runtime_error(std::string(__FILE__) + std::string(":") + std::to_string(__LINE__) + std::string(" in ") + std::string(__FUNCTION__) + std::string(": ") + (x) + std::string(" != ") + (y)); \
        }                                                                                                                                                                                                          \
    }

#define ASSERT_THROW(condition)                                                                                                                              \
    {                                                                                                                                                        \
        if (!(condition)) {                                                                                                                                  \
            throw std::runtime_error(std::string(__FILE__) + std::string(":") + std::to_string(__LINE__) + std::string(" in ") + std::string(__FUNCTION__)); \
        }                                                                                                                                                    \
    }

#define EXPECT_EXCEPTION(expression, exception)                                                                                                              \
    {                                                                                                                                                        \
        try {                                                                                                                                                \
            (expression);                                                                                                                                    \
        }                                                                                                                                                    \
        catch (exception & e) {                                                                                                                              \
        }                                                                                                                                                    \
        catch (...) {                                                                                                                                        \
            throw std::runtime_error(std::string(__FILE__) + std::string(":") + std::to_string(__LINE__) + std::string(" in ") + std::string(__FUNCTION__)); \
        }                                                                                                                                                    \
    }

#define TEST_BEGIN(name)                                      \
    {                                                         \
        std::cerr << "-- Running test \"" << name << "\"..."; \
    }

#define TEST_END()                 \
    {                              \
        std::cerr << "finished\n"; \
    }

#endif