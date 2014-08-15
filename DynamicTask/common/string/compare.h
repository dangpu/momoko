
#ifndef COMMON_BASE_STRING_COMPARE_H
#define COMMON_BASE_STRING_COMPARE_H
#pragma once

#include <stddef.h>
#include <string>
//#include "common/base/compatible/string.h"
#include "common/static_assert.h"
#include "common/string/string_piece.h"
//#include "common/system/memory/unaligned.h"

template<typename T,size_t size>
struct UnalignedWrapper
{
    STATIC_ASSERT(size == 2 || size == 4 || size == 8);
    T value __attribute__((packed));
};

template <typename T>
struct UnalignedWrapper<T, 1>
{
    T value; // one byte needn't packed
};
 
template <typename T>
T GetUnaligned(const void* p)
{
    return static_cast<const UnalignedWrapper<T, sizeof(T)>*>(p)->value;
}

// namespace common {

// An optimized fast memory compare function, should be inlined
inline bool MemoryEqual(const void* a1, const void* a2, size_t size)
{
    return memcmp(a1, a2, size);
    //return memeql(a1, a2, size);
}

inline int CompareMemory(const void *b1, const void *b2, size_t len, size_t* prefix_length)
{
    STATIC_ASSERT(sizeof(size_t) == 8 || sizeof(size_t) == 4 || sizeof(size_t) == 2);

    const unsigned char * const a = (const unsigned char *)b1;
    const unsigned char * const b = (const unsigned char *)b2;

    // pos must bu signed type
    ptrdiff_t pos = 0;
    ptrdiff_t end_pos = len - sizeof(size_t);

    int result = 0;

#define COMPARE_MEMORY_ONE_BYTE() \
    result = a[pos] - b[pos]; \
    if (result) { \
        *prefix_length = pos;\
        return result;\
    } \
    ++pos

    while (pos <= end_pos) // compare by word size
    {
        if (GetUnaligned<size_t>(a + pos) != GetUnaligned<size_t>(b + pos))
        {
            switch (sizeof(size_t))
            {
            case 8:
                COMPARE_MEMORY_ONE_BYTE();
                COMPARE_MEMORY_ONE_BYTE();
                COMPARE_MEMORY_ONE_BYTE();
                COMPARE_MEMORY_ONE_BYTE();
                // fall through
            case 4:
                COMPARE_MEMORY_ONE_BYTE();
                COMPARE_MEMORY_ONE_BYTE();
                // fall through
            case 2:
                COMPARE_MEMORY_ONE_BYTE();
                COMPARE_MEMORY_ONE_BYTE();
            }
            assert(!"unreachable");
        }
        pos += sizeof(size_t);
    }

    switch (len - pos) // handle tail
    {
    case 7: COMPARE_MEMORY_ONE_BYTE();
    case 6: COMPARE_MEMORY_ONE_BYTE();
    case 5: COMPARE_MEMORY_ONE_BYTE();
    case 4: COMPARE_MEMORY_ONE_BYTE();
    case 3: COMPARE_MEMORY_ONE_BYTE();
    case 2: COMPARE_MEMORY_ONE_BYTE();
    case 1: COMPARE_MEMORY_ONE_BYTE();
    }

#undef COMPARE_MEMORY_ONE_BYTE

    *prefix_length = len;
    return result; // match
}

inline int CompareMemory(const void *b1, const void *b2, size_t len)
{
    size_t prefix_length;
    return CompareMemory(b1, b2, len, &prefix_length);
}

/// @brief  求两个串的最大公共前缀串
/// @param  lhs     lhs的buffer
/// @param  lhs_len lhs的长度
/// @param  rhs     rhs的buffer
/// @param  rhs_len rhs的长度
/// @return 最大公共前缀串的长度
inline size_t GetCommonPrefixLength(
    const void* lhs, size_t lhs_len,
    const void* rhs, size_t rhs_len
)
{
    size_t prefix_length;
    size_t common_length = lhs_len < rhs_len ? lhs_len : rhs_len;
    CompareMemory(lhs, rhs, common_length, &prefix_length);
    return prefix_length;
}

inline size_t GetCommonPrefixLength(const std::string& lhs, const std::string& rhs)
{
    return GetCommonPrefixLength(lhs.c_str(), lhs.length(),
            rhs.c_str(), rhs.length());
}

/// @brief  按字节大小比较字符串lhs 和 rhs
/// @param  lhs     lhs的buffer
/// @param  lhs_len lhs的长度
/// @param  rhs     rhs的buffer
/// @param  rhs_len rhs的长度
/// @param  inclusive 返回两个字符串是否存在包含关系
/// @retval <0 lhs < rhs
/// @retval 0  lhs = rhs;
/// @retval >0 lhs > rhs
/// @note 需要 inline
inline int CompareByteString(const void* lhs, size_t lhs_len,
        const void* rhs, size_t rhs_len, bool* inclusive,
        size_t* common_prefix_len = NULL)
{
    const unsigned char* p1 = reinterpret_cast<const unsigned char*>(lhs);
    const unsigned char* p2 = reinterpret_cast<const unsigned char*>(rhs);
    ptrdiff_t min_len = (lhs_len <= rhs_len) ? lhs_len : rhs_len;
    ptrdiff_t pos = 0;
    ptrdiff_t end_pos = min_len - sizeof(size_t) + 1;

    while (pos < end_pos)
    {
        if (GetUnaligned<size_t>(p1 + pos) == GetUnaligned<size_t>(p2 + pos))
            pos += sizeof(size_t); // 按机器字长剔除公共前缀串
        else
            break;
    }

    while ((pos < min_len) && (p1[pos] == p2[pos]))
        pos++;

    *inclusive = (pos == min_len);

    if (common_prefix_len != NULL)
        *common_prefix_len = pos;

    if (*inclusive)
    {
        if (lhs_len > rhs_len)
            return 1;
        else if (lhs_len == rhs_len)
            return 0;
        else
            return -1;
    }
    else
    {
        return p1[pos] - p2[pos];
    }
}

/// @brief  按字节大小比较字符串lhs 和 rhs
/// @param  lhs     lhs的buffer
/// @param  lhs_len lhs的长度
/// @param  rhs     rhs的buffer
/// @param  rhs_len rhs的长度
/// @retval <0 lhs < rhs
/// @retval 0  lhs = rhs;
/// @retval >0 lhs > rhs
inline int CompareByteString(
    const void* lhs, size_t lhs_len,
    const void* rhs, size_t rhs_len
)
{
    bool inclusive;
    return CompareByteString(lhs, lhs_len, rhs, rhs_len, &inclusive);
}

inline int CompareByteString(const std::string& lhs, const std::string& rhs)
{
    return CompareByteString(lhs.c_str(), lhs.length(), rhs.c_str(), rhs.length());
}

inline int CompareStringIgnoreCase(const StringPiece& lhs, const StringPiece& rhs)
{
    return lhs.ignore_case_compare(rhs);
}

inline bool StringEqualsIgnoreCase(const StringPiece& lhs, const StringPiece& rhs)
{
    return lhs.ignore_case_equal(rhs);
}

// } // namespace common

#endif // COMMON_BASE_STRING_COMPARE_H
