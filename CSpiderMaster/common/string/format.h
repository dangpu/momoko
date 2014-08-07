// Copyright (c) 2011, Tencent Inc.
// All rights reserved.
//
// Author: CHEN Feng <phongchen@tencent.com>
// Created: 04/30/11
// Description: string format, C++ version of sprintf

#ifndef COMMON_BASE_STRING_FORMAT_H
#define COMMON_BASE_STRING_FORMAT_H
#pragma once

#include <stdarg.h>
#include <stddef.h>
#include <string>
#include "common/base/platform_features.h"

// namespace common {

/// format argument va_list and append to string.
size_t StringFormatAppendVA(std::string* dst, const char* format, va_list ap)
    __attribute__((format(printf, 2, 0)));

/// format arguments and append to string.
size_t StringFormatAppend(std::string* dst, const char* format, ...)
    __attribute__((format(printf, 2, 3)));

/// format arguments and write to string.
size_t StringFormatTo(std::string* dst, const char* format, ...)
    __attribute__((format(printf, 2, 3)));

/// format arguments return the result as string.
std::string StringFormat(const char* format, ...)
    __attribute__((format(printf, 1, 2)));

// } // namespace common

#endif // COMMON_BASE_STRING_FORMAT_H
