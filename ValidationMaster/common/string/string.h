
#ifndef COMMON_BASE_COMPATIBLE_STRING_H
#define COMMON_BASE_COMPATIBLE_STRING_H

#include <ctype.h>
#include <limits.h>
#include <string.h>

//#include "common/base/compatible/internal.h"
//#include "common/base/compatible/stdbool.h"
//#include "common/base/platform_features.h"
//#include "common/base/stdint.h"
#include <stdint.h>

# define COMPATIBLE_INLINE inline
# define STATIC_CAST(type, value) static_cast<type>(value)


inline bool memeql_2(const char* p1, const char* p2)
{
    return *(uint16_t*)&p1[0] == *(uint16_t*)&p2[0];
}

inline bool memeql_3(const char* p1, const char* p2)
{
    return
        *(uint16_t*)&p1[0] == *(uint16_t*)&p2[0] &&
        p1[2] == p2[2];
}

inline bool memeql_4(const char* p1, const char* p2)
{
    return
        *(uint32_t*)&p1[0] == *(uint32_t*)&p2[0];
}

inline bool memeql_5(const char* p1, const char* p2)
{
    return
        *(uint32_t*)&p1[0] == *(uint32_t*)&p2[0] &&
        p1[4] == p2[4];
}

inline bool memeql_6(const char* p1, const char* p2)
{
    return
        *(uint32_t*)&p1[0] == *(uint32_t*)&p2[0] &&
        *(uint16_t*)&p1[4] == *(uint16_t*)&p2[4];
}

inline bool memeql_7(const char* p1, const char* p2)
{
    return
        *(uint32_t*)&p1[0] == *(uint32_t*)&p2[0] &&
        *(uint16_t*)&p1[4] == *(uint16_t*)&p2[4] &&
        p1[6] == p2[6];
}

inline bool memeql_8(const char* p1, const char* p2)
{
    return *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0];
}

inline bool memeql_9(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        p1[8] == p2[8];
}

inline bool memeql_10(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint16_t*)&p1[8] == *(uint16_t*)&p2[8];
}

inline bool memeql_11(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint16_t*)&p1[8] == *(uint16_t*)&p2[8] &&
        p1[10] == p2[10];
}

inline bool memeql_12(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint32_t*)&p1[8] == *(uint32_t*)&p2[8];
}

inline bool memeql_13(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint32_t*)&p1[8] == *(uint32_t*)&p2[8] &&
        p1[12] == p2[12];
}

inline bool memeql_14(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint32_t*)&p1[8] == *(uint32_t*)&p2[8] &&
        *(uint16_t*)&p1[12] == *(uint16_t*)&p2[12];
}

inline bool memeql_15(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint32_t*)&p1[8] == *(uint32_t*)&p2[8] &&
        *(uint16_t*)&p1[12] == *(uint16_t*)&p2[12] &&
        p1[14] == p2[14];
}

inline bool memeql_16(const char* p1, const char* p2)
{
    return
        *(uint64_t*)&p1[0] == *(uint64_t*)&p2[0] &&
        *(uint64_t*)&p1[8] == *(uint64_t*)&p2[8];
}

// An optimized fast memory compare function, should be inlined
inline
bool memeql(const void* a1, const void* a2, size_t size)
{
#if ALIGNMENT_INSENSITIVE_PLATFORM
    // optimize for alignment insensitive architectures
    const char* p1 = (const char*)a1;
    const char* p2 = (const char*)a2;

    switch (size)
    {
    case 0:
        return true;
    case 1:
        return p1[0] == p2[0];
    case 2:
        return memeql_2(p1, p2);
    case 3:
        return memeql_3(p1, p2);
    case 4:
        return memeql_4(p1, p2);
    case 5:
        return memeql_5(p1, p2);
    case 6:
        return memeql_6(p1, p2);
    case 7:
        return memeql_7(p1, p2);
    case 8:
        return memeql_8(p1, p2);
    case 9:
        return memeql_9(p1, p2);
    case 10:
        return memeql_10(p1, p2);
    case 11:
        return memeql_11(p1, p2);
    case 12:
        return memeql_12(p1, p2);
    case 13:
        return memeql_13(p1, p2);
    case 14:
        return memeql_14(p1, p2);
    case 15:
        return memeql_15(p1, p2);
    case 16:
        return memeql_16(p1, p2);
    }

    while (size >= 8)
    {
        if (*(uint64_t*)&p1[0] != *(uint64_t*)&p2[0])
            return false;
        p1 += 8;
        p2 += 8;
        size -= 8;
    }
    if (size >= 4)
    {
        if (*(uint32_t*)&p1[0] != *(uint32_t*)&p2[0])
            return false;
        p1 += 4;
        p2 += 4;
        size -= 4;
    }
    if (size >= 2)
    {
        if (*(uint16_t*)&p1[0] != *(uint16_t*)&p2[0])
            return false;
        p1 += 2;
        p2 += 2;
        size -= 2;
    }
    if (size == 1)
        return p1[0] == p2[0];

    return true;
#else
    return memcmp(a1, a2, size) == 0;
#endif
}

#ifndef __GNUC__
COMPATIBLE_INLINE const void* internal_memmem(
    const void *haystack,
    size_t haystack_len,
    const void *needle,
    size_t needle_len
    )
{
    const char *begin;
    const char *const last_possible
        = (const char *) haystack + haystack_len - needle_len;

    if (needle_len == 0)
    {
        /* The first occurrence of the empty string is deemed to occur at
           the beginning of the string.  */
        return CONST_CAST(void *, haystack);
    }

    /* Sanity check, otherwise the loop might search through the whole
       memory.  */
    if (haystack_len < needle_len)
        return NULL;

    for (begin = (const char *) haystack; begin <= last_possible; ++begin)
    {
        if (begin[0] == ((const char *) needle)[0] &&
            memeql(&begin[1], ((const char *) needle + 1), needle_len - 1))
            return begin;
    }

    return NULL;
}

#ifdef __cplusplus
COMPATIBLE_INLINE const void* memmem(
    const void *haystack,
    size_t haystack_len,
    const void *needle,
    size_t needle_len
    )
{
    return internal_memmem(haystack, haystack_len, needle, needle_len);
}
COMPATIBLE_INLINE void* memmem(
    void *haystack,
    size_t haystack_len,
    const void *needle,
    size_t needle_len
    )
{
    return CONST_CAST(void*, internal_memmem(haystack, haystack_len, needle, needle_len));
}
#else
COMPATIBLE_INLINE void* memmem(
    const void *haystack,
    size_t haystack_len,
    const void *needle,
    size_t needle_len
    )
{
    return CONST_CAST(void*, internal_memmem(haystack, haystack_len, needle, needle_len));
}
#endif

#endif

// token from linux kernel
/**
 * strlcpy - Copy a %NUL terminated string into a sized buffer
 * @param dest Where to copy the string to
 * @param src Where to copy the string from
 * @param size size of destination buffer
 * @return the total length of the string tried to create
 *
 * Compatible with *BSD: the result is always a valid
 * NUL-terminated string that fits in the buffer (unless,
 * of course, the buffer size is zero). It does not pad
 * out the result like strncpy() does.
 */
inline size_t strlcpy(char *dest, const char *src, size_t size)
{
    size_t ret = strlen(src);

    if (size) {
        size_t len = (ret >= size) ? size - 1 : ret;
        memcpy(dest, src, len);
        dest[len] = '\0';
    }
    return ret;
}

/**
 * strlcat - Append a length-limited, %NUL-terminated string to another
 * @param dest The string to be appended to
 * @param src The string to append to it
 * @param count The size of the destination buffer.
 * @return the total length of the string tried to create
 */
inline size_t strlcat(char *dest, const char *src, size_t count)
{
    size_t dsize = strlen(dest);
    size_t len = strlen(src);
    size_t res = dsize + len;

    if (dsize >= count) {
        dest += dsize;
        count -= dsize;
        if (len >= count)
            len = count - 1;
        memcpy(dest, src, len);
        dest[len] = '\0';
    }
    return res;
}

#ifdef _MSC_VER

COMPATIBLE_INLINE
const void* internal_memrchr(const void* start, int c, size_t len)
{
    const char* end = STATIC_CAST(const char*, start) + len;

    while (--end, len--)
    {
        if (*end == STATIC_CAST(char, c))
            return end;
    }

    return NULL;
}
#ifdef __cplusplus
COMPATIBLE_INLINE const void* memrchr(const void* start, int c, size_t len)
{
    return internal_memrchr(start, c, len);
}
inline void* memrchr(void* start, int c, size_t len)
{
    return const_cast<void*>(internal_memrchr(start, c, len));
}
#else
COMPATIBLE_INLINE void* memrchr(const void* start, int c, size_t len)
{
    return CONST_CAST(void*, internal_memrchr(start, c, len));
}
#endif

inline int strcasecmp(const char *s1, const char *s2)
{
    return _stricmp(s1, s2);
}

inline
int strncasecmp(const char *s1, const char *s2, size_t len)
{
    return _strnicmp(s1, s2, len);
}

inline int strerror_r(int errnum, char *buf, size_t buflen)
{
    return strerror_s(buf, buflen, errnum);
}

#endif

inline
int memcasecmp(const void *vs1, const void *vs2, size_t n)
{
    size_t i;
    const unsigned char *s1 = STATIC_CAST(const unsigned char*, vs1);
    const unsigned char *s2 = STATIC_CAST(const unsigned char*, vs2);
    for (i = 0; i < n; i++)
    {
        unsigned char u1 = s1[i];
        unsigned char u2 = s2[i];
        int U1 = tolower(u1);
        int U2 = tolower(u2);
        int diff = (UCHAR_MAX <= INT_MAX ? U1 - U2
                    : U1 < U2 ? -1 : U2 < U1);
        if (diff)
            return diff;
    }
    return 0;
}

/// search a string for any of a set of characters
/// @param str string to search
/// @param chars set of characters to be found
/// @return a pointer to the character in s that matches one of the characters in accept
/// @retval NULL no such character is found.
/// @sa strpbrk
inline const char* strnpbrk(const char* str, size_t length, const char* chars)
{
    unsigned char bitmap[UCHAR_MAX / CHAR_BIT] = {};
    const unsigned char* p = (const unsigned char*)chars;
    while (*p)
    {
        bitmap[*p / CHAR_BIT] |= 1U << (*p % CHAR_BIT);
        ++chars;
    }

    size_t i;
    for (i = 0; i < length; ++i)
    {
        if (bitmap[(unsigned char)str[i]/CHAR_BIT] & (1U << (str[i] % CHAR_BIT)))
            return str + i;
    }
    return NULL;
}

#endif // COMMON_BASE_COMPATIBLE_STRING_H
