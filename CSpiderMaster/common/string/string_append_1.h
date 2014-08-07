// Copyright (c) 2013, Tencent Inc.
// All rights reserved.
//
// Author: CHEN Feng <phongchen@tencent.com>
// Created: 2013-01-28
// Description: StringAppend with 1 extra parameter

#ifndef COMMON_BASE_STRING_STRING_APPEND_1_H
#define COMMON_BASE_STRING_STRING_APPEND_1_H
#pragma once

#ifndef COMMON_BASE_STRING_CONCAT_H
#error "This file is an implemention detail of string concat, you should not include it directly"
#endif

#include <stdio.h>
#include <ostream>
#include <streambuf>
#include <string>

#include "common/base/static_assert.h"
#include "common/base/type_traits.h"

// GLOBAL_NOLINT(runtime/int)

inline void StringAppend(std::string* str, const std::string& value)
{
    str->append(value);
}

inline void StringAppend(std::string* str, const char* value)
{
    str->append(value);
}

inline void StringAppend(std::string* str, char value)
{
    str->push_back(value);
}

inline void StringAppend(std::string* str, bool value)
{
    if (value)
        str->append("true", 4);
    else
        str->append("false", 5);
}

void StringAppend(std::string* str, short value);
void StringAppend(std::string* str, unsigned short value);
void StringAppend(std::string* str, int value);
void StringAppend(std::string* str, unsigned int value);
void StringAppend(std::string* str, long value);
void StringAppend(std::string* str, unsigned long value);
void StringAppend(std::string* str, long long value);
void StringAppend(std::string* str, unsigned long long value);
void StringAppend(std::string* str, float value);
void StringAppend(std::string* str, double value);
void StringAppend(std::string* str, long double value);

namespace details {

class string_streambuf : public std::streambuf {
public:
    explicit string_streambuf(std::string* str) : m_str(str) {}
    virtual std::streamsize xsputn(const char * s, std::streamsize n) {
        m_str->append(s, n);
        return n;
    }
private:
    std::string* m_str;
};

template <bool is_enum>
struct StringAppendEnum
{
    template <typename T>
    static void Append(std::string* str, const T& value)
    {
        string_streambuf buf(str);
        std::ostream oss(&buf);
        oss.exceptions(std::ios_base::failbit | std::ios_base::badbit);
        oss << value;
    }
};

template <>
struct StringAppendEnum<true>
{
private:
    static void AppendEnum(std::string* str, int value)
    {
        StringAppend(str, value);
    }

    static void AppendEnum(std::string* str, unsigned int value)
    {
        StringAppend(str, value);
    }

    static void AppendEnum(std::string* str, long value)
    {
        StringAppend(str, value);
    }

    static void AppendEnum(std::string* str, unsigned long value)
    {
        StringAppend(str, value);
    }

    static void AppendEnum(std::string* str, long long value)
    {
        StringAppend(str, value);
    }

    static void AppendEnum(std::string* str, unsigned long long value)
    {
        StringAppend(str, value);
    }

public:
    template <typename T>
    static void Append(std::string* str, const T& value)
    {
        AppendEnum(str, value);
    }
};
} // namespace details

// default way to append
template <typename T>
void StringAppend(std::string* str, const T& value)
{
    // convert signed char or unsigned char to string is ambiguous
    // may be typedefed to int8_t or uint8_t
    // disable them
    STATIC_ASSERT((!std::is_same<T, signed char>::value),
        "signed char is not allowed");
    STATIC_ASSERT((!std::is_same<T, unsigned char>::value),
        "unsigned char is not allowed");
    details::StringAppendEnum<std::is_enum<T>::value>::Append(str, value);
}


#endif // COMMON_BASE_STRING_STRING_APPEND_1_H
