#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include "datetime.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <sys/timeb.h>
#include <sys/types.h>

#include <sstream>
#include <string>

#ifdef _WIN32
#include "common/base/common_windows.h"
#else
#include <unistd.h>
#include <sys/time.h>
#endif

// GLOBAL_NOLINT(runtime/printf)
// GLOBAL_NOLINT(readability/casting)

using namespace std;

// namespace common {

#define MICROSECONDS_PER_SECOND 1000000
#define SECONDS_PER_HOUR 3600
#define SECONDS_PER_DAY 86400

#define IS_ALPHA(x)             ( (x >= 'a' && x < 'z') || (x >= 'A' && x < 'Z') )
#define IS_DIGIT(x)             (x >= '0' && x <= '9')

#define IS_SEPARATE_CHAR(x) \
    (x == '\'' || x == '"' || x == '\\' || x == '/' || x == ':' || x == '%')

#define IS_PATTERN_CHAR(x) \
    (x == 'd' || x == 'f' || x == 'F' || x == 'g' || x == 'h' || x == 'H' || \
     x == 'K' || x == 'm' || x == 'M' || x == 's'||x == 't'||x == 'y'||x == 'z')

#define IS_BLANK_SPACE_CHAR(x)  (x == ' ' || x == '\t' || x == '\r' || x == '\n')


// 从一个字符串的头部得到字符串
// strSrc    源字符串
// dwIndex,  开始位置，返回结束位置
// num,  返回值，默认是0
// dwMaxNumLen   数字最长的长度
// bJumpHeadSpace    是否跳过从dwIndex开头的空白字符
bool GetNumFromString(
    const string& strSrc, size_t& dwIndex, int& num,
    const size_t dwMaxNumLen = string::npos,
    bool bJumpHeadSpace = true)
{
    num = 0;

    if (bJumpHeadSpace)
    {
        while (IS_BLANK_SPACE_CHAR(strSrc[dwIndex]) && dwIndex < strSrc.length())
        {
            dwIndex++;
        }

        if (dwIndex == strSrc.length())
        {
            return false;
        }
    }

    if (!(dwIndex < strSrc.length() && IS_DIGIT(strSrc[dwIndex])))
    {
        return false;
    }

    for (size_t i = 0; i < dwMaxNumLen; i++)
    {
        char ch = strSrc[dwIndex];

        if (IS_DIGIT(ch))
        {
            num  = num * 10 + ch - '0';
            dwIndex++;
        }
        else
            break;
    }

    return true;
}

// 检查字符串指定区域是否是空字符
bool IsSpaceChars(const string& strSrc, size_t dwBegin, size_t dwCount)
{
    size_t dwEnd = dwCount + dwBegin > strSrc.length() ? strSrc.length() : dwCount + dwBegin;

    for (; dwBegin < dwEnd; dwBegin++)
    {
        if (!IS_BLANK_SPACE_CHAR(strSrc[dwBegin]))
        {
            return false;
        }
    }

    return true;
}

// ************************* TimeTick ***********************************

TimeTick::TimeTick(time_t tm, int us)
{
    m_sec = tm;
    m_usec = us;
    Normalize();
}

TimeTick::TimeTick(const TimeTick& tt)
{
    m_sec = tt.m_sec;
    m_usec = tt.m_usec;
    Normalize();
}

TimeTick::TimeTick()
{
    m_sec = 0;
    m_usec = 0;
}

void TimeTick::Normalize()
{
    if (!IsNormalized())
    {
        if (m_sec >= 0)
        {
            if (m_usec >= 0)
            {
                m_sec += m_usec / MICROSECONDS_PER_SECOND;
                m_usec = m_usec % MICROSECONDS_PER_SECOND;
            }
            else
            {
                m_sec -= (-m_usec) / MICROSECONDS_PER_SECOND;
                m_usec = -((-m_usec) % MICROSECONDS_PER_SECOND);

                if (m_sec > 0 && m_usec < 0)
                {
                    --m_sec;
                    m_usec = MICROSECONDS_PER_SECOND + m_usec;
                }
            }
        }
        else
        {
            if (m_usec >= 0)
            {
                m_sec += m_usec / MICROSECONDS_PER_SECOND;
                m_usec = m_usec % MICROSECONDS_PER_SECOND;

                if (m_sec < 0 && m_usec > 0)
                {
                    ++m_sec;
                    m_usec = m_usec - MICROSECONDS_PER_SECOND;
                }
            }
            else
            {
                m_sec -= (-m_usec) / MICROSECONDS_PER_SECOND;
                m_usec = -((-m_usec) % MICROSECONDS_PER_SECOND);
            }
        }
    }
}

bool TimeTick::IsNormalized() const
{
    return (m_sec >= 0 && m_usec >= 0 && m_usec < MICROSECONDS_PER_SECOND) ||
           (m_sec <= 0 && m_usec <= 0 && m_usec > -MICROSECONDS_PER_SECOND);
}

TimeTick TimeTick::operator+(const TimeTick& tt) const
{
    TimeTick tick;
    tick.m_sec = this->m_sec + tt.m_sec;
    tick.m_usec = this->m_usec + tt.m_usec;
    tick.Normalize();
    return tick;
}

TimeTick TimeTick::operator-(const TimeTick& tt) const
{
    TimeTick tick;
    tick.m_sec = this->m_sec - tt.m_sec;
    tick.m_usec = this->m_usec - tt.m_usec;
    tick.Normalize();
    return tick;
}

TimeTick& TimeTick::operator+=(const TimeTick& tt)
{
    this->m_sec += tt.m_sec;
    this->m_usec += tt.m_usec;
    this->Normalize();
    return *this;
}

TimeTick& TimeTick::operator-=(const TimeTick& tt)
{
    this->m_sec -= tt.m_sec;
    this->m_usec -= tt.m_usec;
    this->Normalize();
    return *this;
}

TimeTick TimeTick::operator-() const
{
    TimeTick tick;
    tick.m_sec = -this->m_sec;
    tick.m_usec = -this->m_usec;
    return tick;
}

bool TimeTick::operator>(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec > tt.m_sec || (this->m_sec == tt.m_sec && this->m_usec > tt.m_usec);
}

bool TimeTick::operator<(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec < tt.m_sec || (this->m_sec == tt.m_sec && this->m_usec < tt.m_usec);
}

bool TimeTick::operator>=(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec >= tt.m_sec || (this->m_sec == tt.m_sec && this->m_usec >= tt.m_usec);
}

bool TimeTick::operator<=(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec <= tt.m_sec || (this->m_sec == tt.m_sec && this->m_usec <= tt.m_usec);
}

bool TimeTick::operator==(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec == tt.m_sec && this->m_usec == tt.m_usec;
}

bool TimeTick::operator!=(const TimeTick& tt) const
{
    assert(this->IsNormalized());
    assert(tt.IsNormalized());
    return this->m_sec != tt.m_sec && this->m_usec != tt.m_usec;
}


// ************************* TimeSpan **********************************************

const TimeSpan TimeSpan::Zero(TimeTick(0, 0));
const TimeSpan TimeSpan::MaxValue(TimeTick((time_t)0x7FFFFFFFFFFFFFFFLL, 999999));
const TimeSpan TimeSpan::MinValue(TimeTick((time_t)0x8000000000000000LL, -999999));

TimeSpan abs(const TimeSpan& ts)
{
    return ts > TimeSpan::Zero ? ts : -ts;
}

TimeSpan::TimeSpan(const TimeTick& tmTick)
{
    m_Time = tmTick;
    m_Time.Normalize();
}

TimeSpan::TimeSpan(int dwHour, int dwMinute, int dwSecond)
{
    assert(dwMinute < 60 && dwMinute > -60);
    assert(dwSecond < 60 && dwMinute > -60);
    m_Time.m_sec = (time_t)dwHour * SECONDS_PER_HOUR + dwMinute * 60 + dwSecond;
    m_Time.m_usec = 0;
    m_Time.Normalize();
}

TimeSpan::TimeSpan(int dwDay, int dwHour, int dwMinute, int dwSecond)
{
    assert(dwHour < 24 && dwHour > -24);
    assert(dwMinute < 60 && dwMinute > -60);
    assert(dwSecond < 60 && dwSecond > -60);
    m_Time.m_sec = (time_t)dwDay * SECONDS_PER_DAY + dwHour * SECONDS_PER_HOUR +
                   dwMinute * 60 + dwSecond;
    m_Time.m_usec = 0;
    m_Time.Normalize();
}

TimeSpan::TimeSpan(int dwDay, int dwHour, int dwMinute, int dwSecond, int dwMilliSecond)
{
    assert(dwHour < 24 && dwHour > -24);
    assert(dwMinute < 60 && dwMinute > -60);
    assert(dwSecond < 60 && dwSecond > -60);
    assert(dwMilliSecond < 1000 && dwMilliSecond > -1000);
    m_Time.m_sec = (time_t)dwDay * SECONDS_PER_DAY + dwHour * SECONDS_PER_HOUR +
                   dwMinute * 60 + dwSecond;
    m_Time.m_usec = dwMilliSecond * 1000;
    m_Time.Normalize();
}

TimeSpan::TimeSpan(
    int dwDay, int dwHour, int dwMinute, int dwSecond,
    int dwMilliSecond, int dwMicroSecond)
{
    assert(dwHour < 24 && dwHour > -24);
    assert(dwMinute < 60 && dwMinute > -60);
    assert(dwSecond < 60 && dwSecond > -60);
    assert(dwMilliSecond < 1000 && dwMilliSecond > -1000);
    assert(dwMicroSecond < 1000 && dwMicroSecond > -1000);
    m_Time.m_sec = (time_t)dwDay * SECONDS_PER_DAY + dwHour * SECONDS_PER_HOUR +
                   dwMinute * 60 + dwSecond;
    m_Time.m_usec = dwMilliSecond * 1000 + dwMicroSecond;
    m_Time.Normalize();
}

TimeSpan::TimeSpan()
{
    m_Time = TimeTick(0, 0);
}

int TimeSpan::GetDays() const
{
    return (int)(m_Time.m_sec / SECONDS_PER_DAY);
}

int TimeSpan::GetHours() const
{
    return (m_Time.m_sec % SECONDS_PER_DAY) / SECONDS_PER_HOUR;
}

int TimeSpan::GetMinutes() const
{
    return int(m_Time.m_sec % SECONDS_PER_HOUR) / 60;
}

int TimeSpan::GetSeconds() const
{
    return (int)(m_Time.m_sec % 60);
}

int TimeSpan::GetMilliSeconds() const
{
    return m_Time.m_usec / 1000;
}

int TimeSpan::GetMicroSeconds() const
{
    return m_Time.m_usec % 1000;
}

double TimeSpan::GetTotalDays() const
{
    return ((double)m_Time.m_sec + (double)m_Time.m_usec / MICROSECONDS_PER_SECOND) /
           SECONDS_PER_DAY;
}

double TimeSpan::GetTotalHours() const
{
    return ((double)m_Time.m_sec + (double)m_Time.m_usec / MICROSECONDS_PER_SECOND) /
           SECONDS_PER_HOUR;
}

double TimeSpan::GetTotalMinutes() const
{
    return ((double)m_Time.m_sec + (double)m_Time.m_usec / MICROSECONDS_PER_SECOND) / 60;
}

double TimeSpan::GetTotalSeconds() const
{
    return (double)m_Time.m_sec + (double)m_Time.m_usec / MICROSECONDS_PER_SECOND;
}

double TimeSpan::GetTotalMilliSeconds() const
{
    return (double)m_Time.m_sec * 1000 + (double)m_Time.m_usec / 1000;
}

double TimeSpan::GetTotalMicroSeconds() const
{
    return (double)m_Time.m_sec * MICROSECONDS_PER_SECOND + (double)m_Time.m_usec;
}

TimeSpan TimeSpan::FromTick(const TimeTick& tt)
{
    return TimeSpan(tt);
}

TimeSpan TimeSpan::FromDays(double dwDay)
{
    TimeTick tk;
    double fSecond = dwDay * SECONDS_PER_DAY;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::FromHours(double dwHour)
{
    TimeTick tk;
    double fSecond = dwHour * SECONDS_PER_HOUR;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::FromMinutes(double dwMinute)
{
    TimeTick tk;
    double fSecond = dwMinute * 60;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::FromSeconds(double dwSecond)
{
    TimeTick tk;
    double fSecond = dwSecond;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::FromMilliSeconds(double dwMilliSecond)
{
    TimeTick tk;
    double fSecond = dwMilliSecond / 1000;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::FromMicroSeconds(double dwMicroSecond)
{
    TimeTick tk;
    double fSecond = dwMicroSecond / MICROSECONDS_PER_SECOND;
    tk.m_sec = (time_t)(fSecond);
    tk.m_usec = (int)((fSecond - (double)tk.m_sec) * MICROSECONDS_PER_SECOND);
    return TimeSpan(tk);
}

TimeSpan TimeSpan::operator-() const
{
    return TimeSpan(-this->m_Time);
}

TimeSpan TimeSpan::operator+(const TimeSpan& ts) const
{
    return TimeSpan(this->m_Time + ts.m_Time);
}

TimeSpan TimeSpan::operator-(const TimeSpan& ts) const
{
    return TimeSpan(this->m_Time - ts.m_Time);
}

bool TimeSpan::operator>(const TimeSpan& ts) const
{
    return this->m_Time > ts.m_Time;
}

bool TimeSpan::operator<(const TimeSpan& ts) const
{
    return this->m_Time < ts.m_Time;
}

bool TimeSpan::operator>=(const TimeSpan& ts) const
{
    return this->m_Time >= ts.m_Time;
}

bool TimeSpan::operator<=(const TimeSpan& ts) const
{
    return this->m_Time <= ts.m_Time;
}

bool TimeSpan::operator==(const TimeSpan& ts) const
{
    return this->m_Time == ts.m_Time;
}

bool TimeSpan::operator!=(const TimeSpan& ts) const
{
    return this->m_Time != ts.m_Time;
}

/*  表示此实例的值的字符串。返回值形式如下：
[-][d.]hh:mm:ss[.ff]
方括号（“[”和“]”）中的项是可选的，冒号和句号（“:”和“.”）是原义字符，其他项如下。
项      说明
“-”   可选的负号，指示负时间
“d”   可选的天数
“hh”  小时，范围从 0 到 23
“mm”  分钟，范围从 0 到 59
“ss”  秒，范围从 0 到 59
“ff”  可选的秒的小数部分，有 1 到 7 个小数位      */
string TimeSpan::ToString() const
{
    string strRst;
    char buf[200];
    int dwDay = GetDays();

    if (dwDay != 0)
    {
        sprintf(buf, "%d.", dwDay);
        strRst.append(buf);
    }

    sprintf(buf, "%02d:%02d:%02d", abs(GetHours()), abs(GetMinutes()), abs(GetSeconds()));
    strRst.append(buf);

    if (m_Time.m_usec != 0)
    {
        sprintf(buf, ".%06d", abs(m_Time.m_usec));
        strRst.append(buf);
    }

    return string(strRst);
}

/* 从字符串中指定的时间间隔构造新的TimeSpan对象
strTime 参数包含一个如下形式的时间间隔规范：
[ws][-]{ d | [d.]hh:mm[:ss[.ff]] }[ws]
方括号（“[”和“]”）中的项是可选的；需要从大括号（“{”和“}”）内由竖线 (|) 分隔的替换选项列表中选择一项；冒号和句号（“:”和“.”）是必需的原义字符；其他项如下。
项      说明
ws      可选的空白
“-”   可选的减号，指示负 TimeSpan
d       天，范围从 0 到 10675199
hh      小时，范围从 0 到 23
mm      分钟，范围从 0 到 59
ss      可选的秒，范围从 0 到 59
ff      可选的秒的小数部分，有 1 到 7 个小数位

strTime 的分量必须整体指定大于或等于 MinValue 并小于或等于 MaxValue 的时间间隔。        */
TimeSpan TimeSpan::Parse(const string& strTime)
{
    size_t dwIndex = 0;

    while (IS_BLANK_SPACE_CHAR(strTime[dwIndex]) && dwIndex < strTime.length())
    {
        dwIndex++;
    }

    // 空白字符串
    if (dwIndex == strTime.length())
    {
        assert(false);
        return TimeSpan::Zero;
    }

    // 查找第一个:和第一个.
    size_t dwPosSepM = strTime.find(':', dwIndex);
    stringstream strStream(strTime);

    // 只有天数
    if (dwPosSepM == string::npos)
    {
        double fDay;

        if (strStream >> fDay)
        {
            return TimeSpan::FromDays(fDay);
        }

        assert(false);
        return TimeSpan::Zero;
    }

    size_t dwPosSepD = strTime.find('.', dwIndex);
    int dwDay = 0;
    int dwHour = 0;
    int dwMin = 0;
    int dwSec = 0;
    int dwUsec = 0;
    char ch = 0;

    // hh:mm[:ss]格式
    if (dwPosSepD == string::npos)
    {
        strStream >> dwHour >> ch;

        if (ch != ':')
        {
            assert(false);
            return TimeSpan::Zero;
        }

        strStream >> dwMin;

        if (!strStream.eof())
        {
            strStream >> ch;

            if (ch == ':')
            {
                strStream >> dwSec;
            }
        }

        assert(dwHour >= 0 && dwHour < 24);
        assert(dwMin >= 0 && dwMin < 60);
        assert(dwSec >= 0 && dwSec < 60);
        return TimeSpan(dwHour, dwMin, dwSec);
    }
    // [-]d.hh:mm[:ss[.ff]]格式
    else if (dwPosSepD < dwPosSepM)
    {
        if (!(strStream >> dwDay >> ch >> dwHour >> ch >> dwMin))
        {
            assert(false);
            return TimeSpan::Zero;
        }

        if (!strStream.eof())
        {
            strStream >> ch;

            if (ch == ':')
            {
                strStream >> dwSec;

                if (!strStream.eof())
                {
                    strStream >> ch;

                    if (ch == '.')
                    {
                        int dwMode = 100000;

                        while ((strStream >> ch) && dwMode > 0)
                        {
                            if (ch >= '0' && ch <= '9')
                            {
                                dwUsec += (ch - '0') * dwMode;
                            }
                            else
                            {
                                break;
                            }

                            dwMode /= 10;
                        }
                    }
                }
            }
        }

        if (dwDay > 0)
        {
            assert(dwHour >= 0 && dwHour < 24);
            assert(dwMin >= 0 && dwMin < 60);
            assert(dwSec >= 0 && dwSec < 60);
            return TimeSpan(dwDay, dwHour, dwMin, dwSec, dwUsec / 1000, dwUsec % 1000);
        }
        else
        {
            return TimeSpan(dwDay, -dwHour, -dwMin, -dwSec, -dwUsec / 1000, -dwUsec % 1000);
        }
    }
    // hh:mm:ss.ff格式
    else if (dwPosSepD > dwPosSepM)
    {
        if (!(strStream >> dwHour >> ch >> dwMin >> ch >> dwSec >> ch))
        {
            assert(false);
            return TimeSpan::Zero;
        }

        int dwMode = 100000;

        while ((strStream >> ch) && dwMode > 0)
        {
            if (ch >= '0' && ch <= '9')
            {
                dwUsec += (ch - '0') * dwMode;
            }
            else
            {
                break;
            }

            dwMode /= 10;
        }

        return TimeSpan(dwDay, dwHour, dwMin, dwSec, dwUsec / 1000, dwUsec % 1000);
    }

    assert(false);
    return TimeSpan::Zero;
}

TimeSpan& TimeSpan::operator+=(const TimeSpan& ts)
{
    this->m_Time += ts.m_Time;
    return *this;
}

TimeSpan& TimeSpan::operator-=(const TimeSpan& ts)
{
    this->m_Time -= ts.m_Time;
    return *this;
}

// ********************* DateTime **********************************

DateTime::DateTime(const TimeTick& tmTick, int dwTimezoneSeconds)
{
    m_dwTimezoneSeconds = (dwTimezoneSeconds < 0) ?
        DateTime::GetCurrentTimezoneSeconds() : dwTimezoneSeconds;
    m_Time = tmTick;
    // 加上时区
    m_Time.m_sec += m_dwTimezoneSeconds;
    m_Time.Normalize();
}

DateTime::DateTime(int dwYear, int dwMonth, int dwDay,
                   int dwHour /*= 0*/, int dwMinute /*= 0*/, int dwSecond /*= 0*/,
                   int dwMilliSecond /*= 0*/, int dwMicroSecond /*= 0*/ ,
                   int dwTimezoneSeconds)
{
    assert(IsValidDate(dwYear, dwMonth, dwDay));
    m_dwTimezoneSeconds = (dwTimezoneSeconds < 0) ?
        DateTime::GetCurrentTimezoneSeconds() : dwTimezoneSeconds;
    struct tm oTime;
    oTime.tm_hour = dwHour;
    oTime.tm_min = dwMinute;
    oTime.tm_sec = dwSecond;
    oTime.tm_year = dwYear - 1900;
    oTime.tm_mon = dwMonth - 1;
    oTime.tm_mday = dwDay;
    time_t t = mktime(&oTime);
    // mktime得到的时间跟当前系统时区有关，加上系统当前时区转换为时区无关时间
    m_Time.m_sec = t + DateTime::Now().m_dwTimezoneSeconds;
    m_Time.m_usec = dwMilliSecond * 1000 + dwMicroSecond;
    m_Time.Normalize();
}

DateTime::DateTime(int dwTimezoneSeconds)
{
    m_dwTimezoneSeconds = (dwTimezoneSeconds < 0) ?
        DateTime::GetCurrentTimezoneSeconds() : dwTimezoneSeconds;
    // DateTime::Now的值由gettimeofday得到，该函数返回值与系统当前时区无关，
    // 并且在计算Now时已经加了时区时间，因此这里不用加
    m_Time = DateTime::Now().m_Time;
}

DateTime::DateTime(const time_t& tm, int usec /*= 0*/, int dwTimezoneSeconds)
{
    m_dwTimezoneSeconds = (dwTimezoneSeconds < 0) ?
        DateTime::GetCurrentTimezoneSeconds() : dwTimezoneSeconds;
    // 这里的time_t指的是时区无关函数的到的值，如time函数，不能是mktime这种和系统时区相关函数
    // 的返回值。这里加上需要转换的时区时间
    m_Time.m_sec = tm + m_dwTimezoneSeconds;
    m_Time.m_usec = usec;
    m_Time.Normalize();
}

time_t DateTime::GetSecondsSinceEpoch() const
{
    return this->m_Time.m_sec - m_dwTimezoneSeconds;
}

TimeSpan DateTime::operator-(const DateTime& dt) const
{
    // 不同时区减没有意义
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return TimeSpan(this->m_Time - dt.m_Time);
}

DateTime DateTime::operator-(const TimeSpan& ts) const
{
    TimeTick temp_tick = this->m_Time - ts.m_Time;
    temp_tick.m_sec -= this->GetTimeZoneSeconds();
    return DateTime(temp_tick);
}

DateTime DateTime::operator+(const TimeSpan& ts) const
{
    TimeTick temp_tick = this->m_Time + ts.m_Time;
    temp_tick.m_sec -= this->GetTimeZoneSeconds();
    return DateTime(temp_tick);
}

DateTime& DateTime::operator-=(const TimeSpan& ts)
{
    this->m_Time -= ts.m_Time;
    return *this;
}

DateTime& DateTime::operator+=(const TimeSpan& ts)
{
    this->m_Time += ts.m_Time;
    return *this;
}

bool DateTime::operator>(const DateTime& dt) const
{
    return this->m_Time > dt.m_Time;
}

bool DateTime::operator<(const DateTime& dt) const
{
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return this->m_Time < dt.m_Time;
}

bool DateTime::operator>=(const DateTime& dt) const
{
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return this->m_Time >= dt.m_Time;
}

bool DateTime::operator<=(const DateTime& dt) const
{
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return this->m_Time <= dt.m_Time;
}

bool DateTime::operator==(const DateTime& dt) const
{
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return this->m_Time == dt.m_Time;
}

bool DateTime::operator!=(const DateTime& dt) const
{
    assert(this->GetTimeZoneSeconds() == dt.GetTimeZoneSeconds());
    return this->m_Time != dt.m_Time;
}

#ifdef _WIN32
static inline void gmtime_r(const time_t* sec, struct tm* tm_now)
{
    gmtime_s(tm_now, sec);
}
#endif

int DateTime::GetYear() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_year + 1900;
}

int DateTime::GetMonth() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_mon + 1;
}

int DateTime::GetDayOfMonth() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_mday;
}

int DateTime::GetDayOfYear() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_yday;
}

int DateTime::GetDayOfWeek() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_wday;
}

int DateTime::GetHour() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_hour;
}

int DateTime::GetHour12() const
{
    int dwHour = GetHour() % 12;

    if (dwHour == 0)
    {
        dwHour = 12;
    }

    return dwHour;
}

int DateTime::GetMinute() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_min;
}

int DateTime::GetSecond() const
{
    struct tm   tm_now;
    gmtime_r(&this->m_Time.m_sec, &tm_now);
    return tm_now.tm_sec;
}

int DateTime::GetMilliSecond() const
{
    return m_Time.m_usec / 1000;
}

int DateTime::GetMicroSecond() const
{
    return m_Time.m_usec % 1000;
}

// 返回日期
DateTime DateTime::GetDay()const
{
    return DateTime(GetYear(), GetMonth(), GetDayOfMonth());
}
// 返回时间
TimeSpan DateTime::GetTime()const
{
    return TimeSpan(0, GetHour(), GetMinute(), GetSecond(), GetMilliSecond(), GetMicroSecond());
}

DateTime DateTime::Now()
{
    int dwTimezoneSeconds;
#ifdef _WIN32
    struct _timeb   tbNow;
    _ftime_s(&tbNow);
    dwTimezoneSeconds = -tbNow.timezone * 60;
    TimeTick tt(tbNow.time, tbNow.millitm * 1000);
#else
    struct timeval  tvNow;
    gettimeofday(&tvNow, NULL);
    tzset();
    dwTimezoneSeconds = -timezone;
    TimeTick tt(tvNow.tv_sec, (int) tvNow.tv_usec);
#endif
    return DateTime(tt, dwTimezoneSeconds);
}

DateTime DateTime::UTCNow()
{
    DateTime dt = DateTime::Now();
    // 减去时区时间，得到0时区的时间
    dt.m_Time.m_sec -= dt.m_dwTimezoneSeconds;
    dt.m_dwTimezoneSeconds = 0;
    return dt;
}

// 返回当前日期
DateTime DateTime::Today()
{
    time_t t;
    int tz_offset;
#ifdef _WIN32
    struct _timeb   tbNow;
    _ftime_s(&tbNow);
    tz_offset = -tbNow.timezone * 60;
    t = tbNow.time;
#else
    t = time(NULL);
    tzset();
    tz_offset = -timezone;
#endif
    // Today返回当前日期
    // 减去时区时间取整到当天后，得到本日0点时间
    t = (t + tz_offset) / SECONDS_PER_DAY * SECONDS_PER_DAY - tz_offset;
    TimeTick tt(t, 0);
    return DateTime(tt, tz_offset);
}


// 返回当前时间
TimeSpan DateTime::Time()
{
    time_t sec;
    int usec;
    int tz_offset;
#ifdef _WIN32
    struct _timeb   tbNow;
    _ftime_s(&tbNow);
    sec = tbNow.time;
    usec = tbNow.millitm * 1000;
    tz_offset = -tbNow.timezone * 60;
#else
    struct timeval  tvNow;
    gettimeofday(&tvNow, NULL);
    sec = tvNow.tv_sec;
    usec = tvNow.tv_usec;
    tzset();
    tz_offset = -timezone;
#endif
    TimeTick tt((sec + tz_offset) % SECONDS_PER_DAY , usec);
    return TimeSpan(tt);
}

DateTime DateTime::Parse(
    const std::string& strTime,
    const DateTimeFormatInfo& formatInfo /*= DateTimeFormatInfo::zh_CNInfo*/)
{
    DateTime dt;
    dt.SetTime(TimeSpan(12, 0, 0));

    if (!TryParse(strTime, dt, formatInfo))
    {
        return DateTime::Now();
    }

    return dt;
}

DateTime DateTime::Parse(
    const std::string& strTime,
    const std::string& strFormat,
    const DateTimeFormatInfo& formatInfo /*= DateTimeFormatInfo::zh_CNInfo*/)
{
    DateTime dt;
    dt.SetTime(TimeSpan(12, 0, 0));

    if (!TryParse(strTime, strFormat, dt, formatInfo))
    {
        return DateTime::Now();
    }

    return dt;
}

static bool HasSegmentStartsWith(const std::vector<FormatSegment>& segments, char p)
{
    for (std::vector<FormatSegment>::const_iterator it = segments.begin();
        it != segments.end();
        ++it) {
        if ((*it).strSeg[0] == p) {
            return true;
        }
    }
    return false;
}

bool DateTime::TryParse(
    const std::string& strTime,
    const std::string& strFormat,
    DateTime& dt,
    const DateTimeFormatInfo& formatInfo /*= DateTimeFormatInfo::zh_CNInfo*/)
{
    vector<FormatSegment> vecSegment;

    if (!SegmentFormatString(strFormat, vecSegment))
        return false;

    //
    // The following ugly code is for a bug.
    // When user try to parse date with string "2010-11-3 12:23:34" at 2012-1-31,
    // the default value in 'dt' is "2012-1-31 12:00:00".
    // In TryParse,
    //      1. YEAR is set to 2010
    //      2. MONTH is set to 11. But now, the DAY of MONTH is 31. there isn't 31st
    //      days in November.
    // We happen to store the time stamp as the time span from 1970. so now the time
    // is "2010-12-1 12:00:00".
    // After the DAY of month is set, the value is "2010-12-3 12:00:00".
    // Finally, we get "2010-12-3 12:23:34".
    //
    DateTime dt2 = dt;
    // if the YEAR will be reset, it's safe to set to a fake one.
    if (HasSegmentStartsWith(vecSegment, 'y')) {
        const int dammy_year = 2008; // don't change it. it's a fake leap year. A leap
                                     // year is safe to handle 29th Feb staff.
        dt2.SetYear(dammy_year);
    }
    if (HasSegmentStartsWith(vecSegment, 'M')) {
        dt2.SetMonth(1);            // be careful when touch the magic number here.
                                    // use Jan as default, it safe to handle 31th case.
        dt2.SetDayOfMonth(1);
    }

    DateTimeInfo date_info;
    size_t dwIndex = 0;

    for (size_t dwSegIndex = 0; dwSegIndex < vecSegment.size(); dwSegIndex++)
    {
        if (!TryParseSegment(strTime, dwIndex, vecSegment, dwSegIndex, &date_info, formatInfo))
            return false;
    }
    MakeDateTime(date_info, &dt2);
    dt = dt2;

    return true;
}

bool DateTime::TryParse(
    const std::string& strTime,
    DateTime& dt,
    const DateTimeFormatInfo& formatInfo /*= DateTimeFormatInfo::zh_CNInfo*/)
{
    const vector<string> &vecAllPattern = formatInfo.GetAllPatterns();
    DateTime tm = dt;

    for (vector<string>::const_iterator itr = vecAllPattern.begin();
         itr != vecAllPattern.end();
         ++itr)
    {
        dt = tm;

        if (TryParse(strTime, *itr, dt, formatInfo))
        {
            return true;
        }
    }

    return false;
}
/*
string DateTime::ToString(DateTime dt, const string& format)
{
    time_t tz = dt.GetSecondsSinceEpoch();
    struct tm TM;
    gmtime_r(&tz,&TM);
    char buff[15];
    strftime(buff,15,format.c_str(),&TM);
    buff[14] = '\0';
    return (std::string)buff
}
*/
string DateTime::ToString(
        const DateTimeFormatInfo& formatInfo /*= DateTimeFormatInfo::zh_CNInfo*/) const
{
    DateTime dt = *this;
    string strDstFormat = ExpandPredefinedFormat("F", formatInfo, dt);
    strDstFormat += ".FFFFFF zzz";

    // 处理自定义格式
    return ToFormatString(dt, strDstFormat, formatInfo);
}
/*
   1.标准格式模式
   格式模式    关联属性/说明
   d           ShortDatePattern
   D           LongDatePattern
   f           完整日期和时间（长日期和短时间）
   F           FullDateTimePattern（长日期和长时间）
   g           常规（短日期和短时间）
   G           常规（短日期和长时间）
   m、M        MonthDayPattern
   o、O        往返日期/时间模式；在这种格式模式下，格式设置或分析操作始终使用固定区域性
   r、R        RFC1123Pattern；在这种格式模式下，格式设置或分析操作始终使用固定区域性
   s           使用本地时间的 SortableDateTimePattern（基于 ISO 8601）；在这种格式模式下，
   格式设置或分析操作始终使用固定区域性
   t           ShortTimePattern
   T           LongTimePattern
   u           使用通用时间显示格式的 UniversalSortableDateTimePattern；在这种格式模式下，
   格式设置或分析操作始终使用固定区域性
   U           使用通用时间的完整日期和时间（长日期和长时间）
   y、Y        YearMonthPattern        */
std::string DateTime::ToString(
        const std::string& strFormat,
        const DateTimeFormatInfo& formatInfo/* = DateTimeFormatInfo::zh_CNInfo*/)const
{
    DateTime dt = *this;
    string strDstFormat = ExpandPredefinedFormat(strFormat, formatInfo, dt);
    // 处理自定义格式
    return ToFormatString(dt, strDstFormat, formatInfo);
}

bool DateTime::IsLeapYear() const
{
    int dwYear = GetYear();
    return IsLeapYear(dwYear);
}

bool DateTime::IsLeapYear(int dwYear)
{
    if (dwYear % 4 == 0)
    {
        if (dwYear % 100 == 0)
        {
            if (dwYear % 400 == 0)
            {
                return true;
            }
            return false;
        }
        return true;
    }
    return false;
}

static int s_day_number_of_month[12] = {31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

bool DateTime::IsValidDate(int dwYear, int dwMonth , int dwDay)
{
    if (dwMonth < 1 || dwMonth > 12)
    {
        return false;
    }

    if (dwDay < 1 || dwDay > s_day_number_of_month[dwMonth-1])
    {
        return false;
    }

    if (dwMonth == 2 && dwDay == 29 && !IsLeapYear(dwYear))
    {
        return false;
    }
    return true;
}

bool DateTime::SegmentFormatString(
        const std::string& strFormat,
        std::vector<FormatSegment> &vecSegment)
{
    for (size_t dwIndex = 0; dwIndex < strFormat.length(); dwIndex++)
    {
        char ch = strFormat[dwIndex];

        if (ch == '\'')   // 字符串开始
        {
            size_t dwPos = strFormat.find('\'', dwIndex + 1);

            if (dwPos == string::npos)
            {
                return false;
            }

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex + 1, dwPos - dwIndex - 1);
            seg.dwKind = FSTK_String;
            vecSegment.push_back(seg);
            dwIndex = dwPos;
        }
        else if (ch == '"')     // 字符串开始
        {
            size_t dwPos = strFormat.find('"', dwIndex + 1);

            if (dwPos == string::npos)
            {
                return false;
            }

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex + 1, dwPos - dwIndex - 1);
            seg.dwKind = FSTK_String;
            vecSegment.push_back(seg);
            dwIndex = dwPos;
        }
        else if (ch == ':')     // 时间分隔符
        {
            FormatSegment seg;
            seg.strSeg = ":";
            seg.dwKind = FSTK_TIMESEP_CHAR;
            vecSegment.push_back(seg);
        }
        else if (ch == '/')     // 日期分隔符
        {
            FormatSegment seg;
            seg.strSeg = "/";
            seg.dwKind = FSTK_DATESEP_CHAR;
            vecSegment.push_back(seg);
        }
        else if (ch == '%')     // 模式转义符
        {
            if (dwIndex == strFormat.length() - 1)
            {
                assert(false);
                return false;
            }

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex + 1, 1);

            if (!ParseFormatSegment(&seg))
            {
                assert(false);
                return false;
            }

            vecSegment.push_back(seg);
            dwIndex++;
        }
        else if (ch == '\\')     // 字符转义符
        {
            if (dwIndex == strFormat.length() - 1)
            {
                assert(false);
                return false;
            }

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex + 1, 1);
            seg.dwKind = FSTK_String;
            vecSegment.push_back(seg);
            dwIndex++;
        }
        else if (IS_PATTERN_CHAR(ch))
        {
            // 模式字符串,时间模式字符串都是重复出现的字符如：d,dd,ddd,dddddd等
            size_t dwPos = dwIndex;

            while (dwPos < strFormat.length() && strFormat[dwPos] == ch)
                dwPos++;

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex, dwPos - dwIndex);

            if (!ParseFormatSegment(&seg))
            {
                assert(false);
                return false;
            }

            vecSegment.push_back(seg);
            dwIndex = dwPos - 1;
        }
        else     // 非模式字符串
        {
            size_t dwPos = dwIndex;

            while (!IS_PATTERN_CHAR(strFormat[dwPos]) &&
                    !IS_SEPARATE_CHAR(strFormat[dwPos]) &&
                    dwPos < strFormat.length())
            {
                dwPos++;
            }

            FormatSegment seg;
            seg.strSeg = strFormat.substr(dwIndex, dwPos - dwIndex);
            seg.dwKind = FSTK_String;
            vecSegment.push_back(seg);
            dwIndex = dwPos - 1;
        }
    }

    return true;
}

/*2.自定义格式模式，其他非模式字符应该用单引号括起来
  格式模式    说明
  d、%d       月中的某一天。一位数的日期没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%d”。
  dd      月中的某一天。一位数的天有一个前导零。
  ddd     周中某天的缩写名称，在 AbbreviatedDayNames 中定义。
  dddd    周中某天的完整名称，在 DayNames 中定义。
  f、%f   秒的小数精度为一位。其余数字被截断。如果此格式模式没有与其他格式模式组合，应用程序将指定“%f”。
  ff      秒的小数精度为两位。其余数字被截断。
  fff     秒的小数精度为三位。其余数字被截断。
  ffff    秒的小数精度为四位。其余数字被截断。
  fffff   秒的小数精度为五位。其余数字被截断。
  ffffff  秒的小数精度为六位。其余数字被截断。
  fffffff 秒的小数精度为七位。其余数字被截断。
  F、%F   显示秒的小数部分的最高有效数字。如果该数字为零，则不显示任何内容。如果此格式模式没有与其他格式模式组合，应用程序将指定“%F”。
  FF      显示秒的小数部分的两个最高有效数字。但是，不显示尾随的零（两个零数字）。
  FFF     显示秒的小数部分的三个最高有效数字。但是，不显示尾随的零（三个零数字）。
  FFFF    显示秒的小数部分的四个最高有效数字。但是，不显示尾随的零（四个零数字）。
  FFFFF   显示秒的小数部分的五个最高有效数字。但是，不显示尾随的零（五个零数字）。
  FFFFFF  显示秒的小数部分的六个最高有效数字。但是，不显示尾随的零（六个零数字）。
  FFFFFFF 显示秒的小数部分的七个最高有效数字。但是，不显示尾随的零（七个零数字）。
  gg      时期或纪元。如果要设置格式的日期不具有关联的时期或纪元字符串，则忽略该模式。
  h、%h   12 小时制的小时。一位数的小时数没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%h”。
  hh      12 小时制的小时。一位数的小时有一个前导零。
  H、%H   24 小时制的小时。一位数的小时数没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%H”。
  HH      24 小时制的小时。一位数的小时有一个前导零。
  K       Kind 属性的不同值，即本地、Utc 或未指定，同zzz。
  m、%m   分钟。一位数的分钟数没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%m”。
  mm      分钟。一位数的分钟有一个前导零。
  M、%M   月份数字。一位数的月份没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%M”。
  MM      月份数字。一位数的月份有一个前导零。
  MMM     月份的缩写名称，在 AbbreviatedMonthNames 中定义。
  MMMM    月份的完整名称，在 MonthNames 中定义。
  s、%s   秒。一位数的秒数没有前导零。如果此格式模式没有与其他格式模式组合，应用程序将指定“%s”。
  ss      秒。一位数的秒有一个前导零。
  t、%t   在 AMDesignator 或 PMDesignator 中定义的 AM/PM 指示项的第一个字符（如果存在）。如果此格式模式没有与其他格式模式组合，应用程序将指定“%t”。
  tt      在 AMDesignator 或 PMDesignator 中定义的 AM/PM 指示项（如果存在）。对于需要维护 AM 与 PM 之间的差异的语言，应用程序应使用此格式模式。以日语为例，其 AM 和 PM 指示符的差异点为第二个字符，而非第一个字符。
  y、%y   不包含纪元的年份。如果不包含纪元的年份小于 10，则显示不具有前导零的年份。如果此格式模式没有与其他格式模式组合，应用程序将指定“%y”。
  yy      不包含纪元的年份。如果不包含纪元的年份小于 10，则显示具有前导零的年份。
  yyy     三位数的年份。如果年份小于 100，则会以带前导零的方式显示。
  yyyy    包括纪元的四位或五位数的年份（取决于所使用的日历）。对于不够四位数的年份，将使用前导零填充。泰国佛历和朝鲜历采用五位数的年份。对于具有五位数的日历，选择“yyyy”模式的用户将看到不带前导零的所有这五位数。例外情况：对于日本历和台湾日历，其行为始终都像是用户选择了“yy”。
  yyyyy   五位数的年份。对于不够五位数的年份，将使用前导零填充。例外情况：对于日本历和台湾日历，其行为始终都像是用户选择了“yy”。
  yyyyyy  六位数的年份。对于不够六位数的年份，将使用前导零填充。例外情况：对于日本历和台湾日历，其行为始终都像是用户选择了“yy”。此模式可不断续加“y”，从而形成一个更长的字符串，这时将需要使用更多的前导零。
  z、%z   时区偏移量（“+”或“-”后面仅跟小时）。一位数的小时数没有前导零。例如，太平洋标准时间是“-8”。如果此格式模式没有与其他格式模式组合，应用程序将指定“%z”。
  zz      时区偏移量（“+”或“-”后面仅跟小时）。一位数的小时有一个前导零。例如，太平洋标准时间是“-08”。
  zzz     完整时区偏移量（“+”或“-”后面跟有小时和分钟）。一位数的小时数和分钟数有前导零。例如，太平洋标准时间是“-08:00”。
  :       在 TimeSeparator 中定义的默认时间分隔符。
  /       在 DateSeparator 中定义的默认日期分隔符。
  % c     其中 c 是格式模式（如果单独使用）。若要使用格式模式“d”、“f”、“F”、“h”、“m”、“s”、“t”、“y”、“z”、“H”、或“M”本身，应用程序应指定“%d”、“%f”、“%F”、“%h”、“%m”、“%s”、“%t”、“%y”、“%z”、“%H”或“%M”。如果格式模式与原义字符或其他格式模式合并，则可以省略“%”字符。
  \ c     其中 c 是任意字符。照原义显示字符。若要显示反斜杠字符，应用程序应使用“\\”。           */
std::string DateTime::ToFormatString(
        const DateTime& dt,
        const std::string& strFormat,
        const DateTimeFormatInfo& formatInfo)
{
    vector<FormatSegment> vecSegment;

    if (!SegmentFormatString(strFormat, vecSegment))
        return "";

    return ToFormatString(dt, vecSegment, formatInfo);
}

std::string DateTime::ToFormatString(
        const DateTime& dt,
        const std::vector<FormatSegment> &vecSegment,
        const DateTimeFormatInfo& formatInfo)
{
    string strRst;
    char buf[100];

    for (vector<FormatSegment>::const_iterator itr = vecSegment.begin();
            itr != vecSegment.end(); ++itr)
    {
        switch (itr->dwKind)
        {
            case FSTK_String:
                strRst.append(itr->strSeg);
                break;
            case FSTK_d:
                sprintf(buf, "%d", dt.GetDayOfMonth());
                strRst.append(buf);
                break;
                // dd,   01-31
            case FSTK_dd:
                sprintf(buf, "%02d", dt.GetDayOfMonth());
                strRst.append(buf);
                break;
                // ddd,  一周中某天的缩略名称
            case FSTK_ddd:
                strRst.append(formatInfo.AbbreviatedDayNames()[dt.GetDayOfWeek()]);
                break;
                // dddd或者更多的d   ，一周中某天的全称
            case FSTK_dddd_:
                strRst.append(formatInfo.DayNames()[dt.GetDayOfWeek()]);
                break;
                // f,ff,fff,ffff,fffff,ffffff
            case FSTK_f:
            case FSTK_ff:
            case FSTK_fff:
            case FSTK_ffff:
            case FSTK_fffff:
            case FSTK_ffffff:
                {
                    int usec = dt.m_Time.m_usec;
                    size_t dwLen = itr->strSeg.length() > 6 ? 6 : itr->strSeg.length();
                    sprintf(buf, "%06d", usec);
                    strRst.append(buf, dwLen);
                }
                break;
                // F,FF,FFF,FFFF,FFFFF,FFFFFF
            case FSTK_F:
            case FSTK_FF:
            case FSTK_FFF:
            case FSTK_FFFF:
            case FSTK_FFFFF:
            case FSTK_FFFFFF:
                {
                    int usec = dt.m_Time.m_usec;
                    size_t dwLen = itr->strSeg.length() > 6 ? 6 : itr->strSeg.length();
                    sprintf(buf, "%06d", usec);

                    while (dwLen > 0 && buf[dwLen - 1] == '0')
                    {
                        dwLen--;
                    }

                    if (dwLen > 0)
                    {
                        strRst.append(buf, dwLen);
                    }
                    else if (*strRst.rbegin() == '.')     // 小数点
                    {
                        strRst.erase(strRst.length() - 1);
                    }
                }
                break;
                // g,gg或者更多g
            case FSTK_g_:
                strRst.append(formatInfo.EraNames()[0]);
                break;
                // h     1-12数字
            case FSTK_h:
                sprintf(buf, "%d", dt.GetHour12());
                strRst.append(buf);
                break;
                // hh或者更多h，01-12数字
            case FSTK_hh_:
                sprintf(buf, "%02d", dt.GetHour12());
                strRst.append(buf);
                break;
                // H     0-23数字
            case FSTK_H:
                sprintf(buf, "%d", dt.GetHour());
                strRst.append(buf);
                break;
                // HH或者更多H，00-23数字
            case FSTK_HH_:
                sprintf(buf, "%02d", dt.GetHour());
                strRst.append(buf);
                break;
                // K,    表示时区，localtime等效于zzz
            case FSTK_K:
                sprintf(buf, "%c%02d%s%02d",
                        dt.m_dwTimezoneSeconds >= 0 ? '+' : '-',
                        abs(dt.m_dwTimezoneSeconds) / SECONDS_PER_HOUR,
                        formatInfo.TimeSeparator().c_str(),
                        (abs(dt.m_dwTimezoneSeconds) % SECONDS_PER_HOUR) / 60);
                strRst.append(buf);
                break;
                // m     0-59
            case FSTK_m:
                sprintf(buf, "%d", dt.GetMinute());
                strRst.append(buf);
                break;
                // mm,或更多m，00-59
            case FSTK_mm_:
                sprintf(buf, "%02d", dt.GetMinute());
                strRst.append(buf);
                break;
                // M     1-12
            case FSTK_M:
                sprintf(buf, "%d", dt.GetMonth());
                strRst.append(buf);
                break;
                // MM    01-12
            case FSTK_MM:
                sprintf(buf, "%02d", dt.GetMonth());
                strRst.append(buf);
                break;
                // MMM   月份缩略词
            case FSTK_MMM:
                strRst.append(formatInfo.AbbreviatedMonthNames()[dt.GetMonth() - 1]);
                break;
                // MMMM  月份全名
            case FSTK_MMMM:
                strRst.append(formatInfo.MonthNames()[dt.GetMonth() - 1]);
                break;
                // s     0-59
            case FSTK_s:
                sprintf(buf, "%d", dt.GetSecond());
                strRst.append(buf);
                break;
                // ss,或者更多s  00-59
            case FSTK_ss_:
                sprintf(buf, "%02d", dt.GetSecond());
                strRst.append(buf);
                break;
                // t     AM，PM标识符的第一个字母
            case FSTK_t:

                if (dt.IsAM() && formatInfo.AMDesignator().length() > 0)
                {
                    strRst.push_back(formatInfo.AMDesignator()[0]);

                    if (formatInfo.AMDesignator()[0] < 0)
                    {
                        assert(formatInfo.AMDesignator().length() > 1);
                        strRst.push_back(formatInfo.AMDesignator()[1]);
                    }
                }
                else if (dt.IsPM() && formatInfo.PMDesignator().length() > 0)
                {
                    strRst.push_back(formatInfo.PMDesignator()[0]);

                    if (formatInfo.PMDesignator()[0] < 0)
                    {
                        assert(formatInfo.PMDesignator().length() > 1);
                        strRst.push_back(formatInfo.PMDesignator()[1]);
                    }
                }

                break;
                // tt，或更多t   AM，PM标识符全称
            case FSTK_tt_:

                if (dt.IsAM())
                {
                    strRst.append(formatInfo.AMDesignator());
                }
                else
                {
                    strRst.append(formatInfo.PMDesignator());
                }

                break;
                // y     1-99,将年份表示为1位或者两位数字
            case FSTK_y:
                {
                    int dwYear = dt.GetYear();

                    if (dwYear > 100)
                    {
                        sprintf(buf, "%02d", dwYear % 100);
                    }
                    else
                    {
                        sprintf(buf, "%d", dwYear);
                    }

                    strRst.append(buf);
                }
                break;
                // yy    两位数，前导符0
            case FSTK_yy:
                sprintf(buf, "%02d", dt.GetYear() % 100);
                strRst.append(buf);
                break;
                // yyy，三位数，前导符0
            case FSTK_yyy:
                sprintf(buf, "%03d", dt.GetYear());
                strRst.append(buf);
                break;
                // yyyy，四位数，前导符0
            case FSTK_yyyy:
                sprintf(buf, "%04d", dt.GetYear());
                strRst.append(buf);
                break;
                // yyyyy,或更多y，表示为5位数，前导符0
            case FSTK_yyyyy_:
                sprintf(buf, "%05d", dt.GetYear());
                strRst.append(buf);
                break;
                // z     +8
            case FSTK_z:
                {
                    int dwTimezoneSeconds = dt.GetTimeZoneSeconds();
                    sprintf(buf, "%c%d",
                            dwTimezoneSeconds >= 0 ? '+' : '-',
                            abs(dwTimezoneSeconds) / SECONDS_PER_HOUR);
                    strRst.append(buf);
                }
                break;
                // zz    +08
            case FSTK_zz:
                {
                    int dwTimezoneSeconds = dt.GetTimeZoneSeconds();
                    sprintf(buf, "%c%02d",
                            dwTimezoneSeconds >= 0 ? '+' : '-',
                            abs(dwTimezoneSeconds) / SECONDS_PER_HOUR);
                    strRst.append(buf);
                }
                break;
                // zzz   +08:00
            case FSTK_zzz:
                {
                    int dwTimezoneSeconds = dt.GetTimeZoneSeconds();
                    sprintf(buf, "%c%02d%s%02d",
                            dwTimezoneSeconds >= 0 ? '+' : '-',
                            abs(dwTimezoneSeconds) / SECONDS_PER_HOUR,
                            formatInfo.TimeSeparator().c_str(),
                            (abs(dwTimezoneSeconds) % SECONDS_PER_HOUR) / 60);
                    strRst.append(buf);
                }
                break;
            case FSTK_DATESEP_CHAR:
                strRst.append(formatInfo.DateSeparator());
                break;
            case FSTK_TIMESEP_CHAR:
                strRst.append(formatInfo.TimeSeparator());
                break;
            default:
                assert(false);
                return "";
        }
    }

    return strRst;
}

int DateTime::GetTimeZone() const
{
    return m_dwTimezoneSeconds / SECONDS_PER_HOUR;
}

int DateTime::GetTimeZoneSeconds() const
{
    return m_dwTimezoneSeconds;
}

DateTime DateTime::GetUTCDateTime() const
{
    DateTime dt = *this;
    dt.m_Time.m_sec -= m_dwTimezoneSeconds;
    dt.m_dwTimezoneSeconds = 0;
    return dt;
}

bool DateTime::IsAM() const
{
    return GetHour() < 12;
}

bool DateTime::IsPM() const
{
    return GetHour() >= 12;
}

std::string DateTime::ExpandPredefinedFormat(
        const std::string& strFormat,
        const DateTimeFormatInfo& formatInfo,
        DateTime& dt) const
{
    string strDstFormat = strFormat;

    // 处理标准格式
    if (strFormat.length() == 1)
    {
        switch (strFormat[0])
        {
            /*格式模式  关联属性/说明*/
            // d         ShortDatePattern
            case 'd':
                strDstFormat = formatInfo.ShortDatePattern();
                break;
                // D             LongDatePattern
            case 'D':
                strDstFormat = formatInfo.LongDatePattern();
                break;
                // f             完整日期和时间（长日期和短时间）
            case 'f':
                strDstFormat = formatInfo.LongDatePattern() + " " + formatInfo.ShortTimePattern();
                break;
                // F             FullDateTimePattern（长日期和长时间）
            case 'F':
                strDstFormat = formatInfo.LongDatePattern() + " " + formatInfo.LongTimePattern();
                break;
                // g             常规（短日期和短时间）
            case 'g':
                strDstFormat = formatInfo.ShortDatePattern() + " " + formatInfo.ShortTimePattern();
                break;
                // G             常规（短日期和长时间）
            case 'G':
                strDstFormat = formatInfo.ShortDatePattern() + " " + formatInfo.LongTimePattern();
                break;
                // m、M      MonthDayPattern
            case 'm':
            case 'M':
                strDstFormat = formatInfo.MonthDayPattern();
                break;
                // o、O      往返日期/时间模式；在这种格式模式下，格式设置或分析操作始终使用固定区域性
            case 'o':
            case 'O':
                // "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffzz";
                strDstFormat = formatInfo.RetureBackPattern();
                break;
                // r、R      RFC1123Pattern；在这种格式模式下，格式设置或分析操作始终使用固定区域性
            case 'r':
            case 'R':
                strDstFormat = formatInfo.RFC1123Pattern();
                break;
                // s         使用本地时间的 SortableDateTimePattern（基于 ISO 8601）；
                // 在这种格式模式下，格式设置或分析操作始终使用固定区域性
            case 's':
                strDstFormat = formatInfo.SortableDateTimePattern();
                break;
                // t             ShortTimePattern
            case 't':
                strDstFormat = formatInfo.ShortTimePattern();
                break;
                // T             LongTimePattern
            case 'T':
                strDstFormat = formatInfo.LongTimePattern();
                break;
                // u    使用通用时间显示格式的 UniversalSortableDateTimePattern；
                //      在这种格式模式下，格式设置或分析操作始终使用固定区域性
            case 'u':
                dt = this->GetUTCDateTime();
                strDstFormat = formatInfo.UniversalSortableDateTimePattern();
                break;
                // U             使用通用时间的完整日期和时间（长日期和长时间）
            case 'U':
                dt = this->GetUTCDateTime();
                strDstFormat = formatInfo.FullDateTimePattern();
                break;
                // y、Y      YearMonthPattern
            case 'y':
            case 'Y':
                strDstFormat = formatInfo.YearMonthPattern();
                break;
            default:
                strDstFormat = "";
        }
    }

    return strDstFormat;
}

bool DateTime::ParseFormatSegment(FormatSegment* seg)
{
    if (seg->strSeg == "d")
    {
        seg->dwKind = FSTK_d;
    }
    // dd,   01-31
    else if (seg->strSeg == "dd")
    {
        seg->dwKind = FSTK_dd;
    }
    // ddd,  一周中某天的缩略名称
    else if (seg->strSeg == "ddd")
    {
        seg->dwKind = FSTK_ddd;
    }
    // dddd或者更多的d   ，一周中某天的全称
    else if (seg->strSeg.length() >= 4 && seg->strSeg.find("dddd") == 0)
    {
        seg->dwKind = FSTK_dddd_;
    }
    // f,ff,fff,ffff,fffff,ffffff
    else if (seg->strSeg[0] == 'f')
    {
        seg->dwKind = (FormatSegmentTokenKind)(FSTK_f + seg->strSeg.length() - 1);
    }
    // F,FF,FFF,FFFF,FFFFF,FFFFFF
    else if (seg->strSeg[0] == 'F')
    {
        seg->dwKind = (FormatSegmentTokenKind)(FSTK_F + seg->strSeg.length() - 1);
    }
    // g,gg或者更多g
    else if (seg->strSeg[0] == 'g')
    {
        seg->dwKind = FSTK_g_;
    }
    // h     1-12数字
    else if (seg->strSeg == "h")
    {
        seg->dwKind = FSTK_h;
    }
    // hh或者更多h，01-12数字
    else if (seg->strSeg.find("hh") == 0)
    {
        seg->dwKind = FSTK_hh_;
    }
    // H     0-23数字
    else if (seg->strSeg == "H")
    {
        seg->dwKind = FSTK_H;
    }
    // HH或者更多H，00-23数字
    else if (seg->strSeg.find("HH") == 0)
    {
        seg->dwKind = FSTK_HH_;
    }
    // K,    表示时区，localtime等效于zzz
    else if (seg->strSeg == "K")
    {
        seg->dwKind = FSTK_K;
    }
    // m     0-59
    else if (seg->strSeg == "m")
    {
        seg->dwKind = FSTK_m;
    }
    // mm,或更多m，00-59
    else if (seg->strSeg.find("mm") == 0)
    {
        seg->dwKind = FSTK_mm_;
    }
    // M     1-12
    else if (seg->strSeg == "M")
    {
        seg->dwKind = FSTK_M;
    }
    // MM    01-12
    else if (seg->strSeg == "MM")
    {
        seg->dwKind = FSTK_MM;
    }
    // MMM   月份缩略词
    else if (seg->strSeg == "MMM")
    {
        seg->dwKind = FSTK_MMM;
    }
    // MMMM  月份全名
    else if (seg->strSeg == "MMMM")
    {
        seg->dwKind = FSTK_MMMM;
    }
    // s     0-59
    else if (seg->strSeg == "s")
    {
        seg->dwKind = FSTK_s;
    }
    // ss,或者更多s  00-59
    else if (seg->strSeg.find("ss") == 0)
    {
        seg->dwKind = FSTK_ss_;
    }
    // t     AM，PM标识符的第一个字母
    else if (seg->strSeg == "t")
    {
        seg->dwKind = FSTK_t;
    }
    // tt，或更多t   AM，PM标识符全称
    else if (seg->strSeg.find("tt") == 0)
    {
        seg->dwKind = FSTK_tt_;
    }
    // y     1-99,将年份表示为1位或者两位数字
    else if (seg->strSeg == "y")
    {
        seg->dwKind = FSTK_y;
    }
    // yy    两位数，前导符0
    else if (seg->strSeg == "yy")
    {
        seg->dwKind = FSTK_yy;
    }
    // yyy，三位数，前导符0
    else if (seg->strSeg == "yyy")
    {
        seg->dwKind = FSTK_yyy;
    }
    // yyyy，四位数，前导符0
    else if (seg->strSeg == "yyyy")
    {
        seg->dwKind = FSTK_yyyy;
    }
    // yyyyy,或更多y，表示为5位数，前导符0
    else if (seg->strSeg.find("yyyyy") == 0)
    {
        seg->dwKind = FSTK_yyyyy_;
    }
    // z     +8
    else if (seg->strSeg == "z")
    {
        seg->dwKind = FSTK_z;
    }
    // zz    +08
    else if (seg->strSeg == "zz")
    {
        seg->dwKind = FSTK_zz;
    }
    // zzz   +08:00
    else if (seg->strSeg == "zzz")
    {
        seg->dwKind = FSTK_zzz;
    }
    else if (seg->strSeg == "/")
    {
        seg->dwKind = FSTK_DATESEP_CHAR;
    }
    else if (seg->strSeg == ":")
    {
        seg->dwKind = FSTK_TIMESEP_CHAR;
    }
    else
        return false;

    return true;
}

void DateTime::SetYear(int dwYear)
{
    *this = DateTime(dwYear, this->GetMonth(), this->GetDayOfMonth(),
            this->GetHour(), this->GetMinute(), this->GetSecond(),
            this->GetMilliSecond(), this->GetMicroSecond(),
            this->GetTimeZoneSeconds());
}

void DateTime::SetMonth(int dwMonth)
{
    assert(dwMonth >= 1 && dwMonth <= 12);
    *this = DateTime(this->GetYear(), dwMonth, this->GetDayOfMonth(),
            this->GetHour(), this->GetMinute(), this->GetSecond(),
            this->GetMilliSecond(), this->GetMicroSecond(),
            this->GetTimeZoneSeconds());
}

void DateTime::SetDayOfMonth(int dwDay)
{
    assert(dwDay >= 1 && dwDay <= 31);
    *this = DateTime(this->GetYear(), this->GetMonth(), dwDay,
            this->GetHour(), this->GetMinute(), this->GetSecond(),
            this->GetMilliSecond(), this->GetMicroSecond(),
            this->GetTimeZoneSeconds());
}

void DateTime::SetHour(int dwHour)
{
    m_Time.m_sec = ((m_Time.m_sec - m_Time.m_sec % SECONDS_PER_DAY +
                m_Time.m_sec % SECONDS_PER_HOUR) +
            (dwHour % 24) * SECONDS_PER_HOUR);
}

void DateTime::SetHour12(int dwHour12, bool bAM)
{
    dwHour12 = (dwHour12 + (bAM ? 0 : 12));

    if (dwHour12 == 24)
    {
        dwHour12 = 0;
    }

    SetHour(dwHour12);
}

void DateTime::SetMinute(int dwMinute)
{
    m_Time.m_sec = (m_Time.m_sec - m_Time.m_sec % SECONDS_PER_HOUR + m_Time.m_sec % 60) +
        (dwMinute % 60) * 60;
}

void DateTime::SetSecond(int dwSecond)
{
    m_Time.m_sec = (m_Time.m_sec - m_Time.m_sec % 60) + dwSecond % 60;
}

void DateTime::SetMilliSecond(int dwMilliSecond)
{
    m_Time.m_usec = m_Time.m_usec % 1000 + (dwMilliSecond % 1000) * 1000;
}

void DateTime::SetMicroSecond(int dwMicroSecond)
{
    m_Time.m_usec = (m_Time.m_usec - m_Time.m_usec % 1000) + dwMicroSecond % 1000;
}

void DateTime::SetTimeZone(int dwTimeZone)
{
    this->m_dwTimezoneSeconds = dwTimeZone * SECONDS_PER_HOUR;
}

void DateTime::SetTimeZoneSeconds(int dwTimezoneSeconds)
{
    this->m_dwTimezoneSeconds = dwTimezoneSeconds;
}

void DateTime::SetDay(const DateTime& dt)
{
    *this = DateTime(dt.GetYear(), dt.GetMonth(), dt.GetDayOfMonth(),
            this->GetHour(), this->GetMinute(), this->GetSecond(),
            this->GetMilliSecond(), this->GetMicroSecond(),
            this->GetTimeZoneSeconds());
}

void DateTime::SetTime(const TimeSpan& ts)
{
    SetHour(ts.GetHours());
    SetMinute(ts.GetMinutes());
    SetSecond(ts.GetSeconds());
    SetMilliSecond(ts.GetMilliSeconds());
    SetMicroSecond(ts.GetMicroSeconds());
}

void DateTime::SetAMOrPM(bool bAM)
{
    if (IsAM() == bAM)
    {
        return;
    }
    else
    {
        int dwHour = GetHour();

        if (bAM)
        {
            dwHour -= 12;
        }
        else
        {
            dwHour += 12;
        }

        SetHour(dwHour);
    }
}

bool DateTime::TryParseSegment(
        const std::string& strTime,
        size_t& dwIndex,
        const vector<FormatSegment> &vecSegment,
        const size_t dwSegIndex,
        DateTimeInfo* date_info,
        const DateTimeFormatInfo& formatInfo)
{
    size_t dwPos = 0;
    int dwNum = 0;
    vector<FormatSegment>::const_iterator itr = vecSegment.begin() + dwSegIndex;
    const size_t dwLen = strTime.length();

    switch (itr->dwKind)
    {
        case FSTK_String:
            dwPos = strTime.find(itr->strSeg, dwIndex);

            // dwPosd
            if (dwPos != string::npos &&
                    (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
            {
                dwIndex = dwPos + itr->strSeg.length();
            }
            else
            {
                if (itr->strSeg == ".")
                {
                    vector<FormatSegment>::const_iterator itrNext =  itr + 1;

                    if (itrNext == vecSegment.end())
                    {
                        return false;
                    }

                    // s.F可以匹配s
                    if (itrNext->dwKind != FSTK_String &&
                            itrNext->strSeg.length() > 0 &&
                            itrNext->strSeg[0] == 'F')
                    {
                        break;
                    }
                }

                return false;
            }

            break;
        case FSTK_d:
            // dd,   01-31
        case FSTK_dd:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 1 && dwNum <= 31)
                {
                    date_info->day_of_month = dwNum;
                    break;
                }
            }

            return false;
            // ddd,  一周中某天的缩略名称
        case FSTK_ddd:

            for (vector<string>::const_iterator itrNames = formatInfo.AbbreviatedDayNames().begin();
                    itrNames != formatInfo.AbbreviatedDayNames().end(); ++itrNames)
            {
                dwPos = strTime.find(*itrNames, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex += dwPos + itrNames->length();
                    break;
                }
            }

            return false;
            // dddd或者更多的d   ，一周中某天的全称
        case FSTK_dddd_:

            for (vector<string>::const_iterator itrNames = formatInfo.DayNames().begin();
                    itrNames != formatInfo.DayNames().end(); ++itrNames)
            {
                dwPos = strTime.find(*itrNames, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex = dwPos + itrNames->length();
                    break;
                }
            }

            return false;
            // f,ff,fff,ffff,fffff,ffffff
        case FSTK_f:
        case FSTK_ff:
        case FSTK_fff:
        case FSTK_ffff:
        case FSTK_fffff:
        case FSTK_ffffff: // f必须匹配一个数字，F可以匹配省略的零

            if (!IS_DIGIT(strTime[dwIndex]))
            {
                return false;
            }

            // F,FF,FFF,FFFF,FFFFF,FFFFFF
        case FSTK_F:
        case FSTK_FF:
        case FSTK_FFF:
        case FSTK_FFFF:
        case FSTK_FFFFF:
        case FSTK_FFFFFF:
            {
                dwNum = 0;
                int dwMode = 100000;

                while (dwIndex < dwLen && IS_DIGIT(strTime[dwIndex]) && dwMode > 0)
                {
                    dwNum += (strTime[dwIndex] - '0') * dwMode;
                    dwIndex++;
                    dwMode /= 10;
                }

                date_info->microseconds = dwNum;
            }
            break;
            // g,gg或者更多g
        case FSTK_g_:
            dwPos = strTime.find(formatInfo.EraNames()[0], dwIndex);

            if (dwPos != string::npos &&
                    (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
            {
                dwIndex += formatInfo.EraNames()[0].length();
            }
            else
                return false;

            break;
            // h     1-12数字
        case FSTK_h:
            // hh或者更多h，01-12数字
        case FSTK_hh_:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 1 && dwNum <= 12)
                {
                    // dwHour12 = dwNum;
                    date_info->hour = dwNum;
                    date_info->is_hour12 = true;
                    break;
                }
            }

            return false;
            // H     0-23数字
        case FSTK_H:
            // HH或者更多H，00-23数字
        case FSTK_HH_:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 0 && dwNum <= 23)
                {
                    date_info->hour = dwNum;
                    date_info->is_hour12 = false;
                    break;
                }
            }

            return false;
            // K,    表示时区，localtime等效于zzz，+08:00
        case FSTK_K:
            {
                int dwTimezoneSeconds = 0;

                while (IS_BLANK_SPACE_CHAR(strTime[dwIndex]) && dwIndex < dwLen)
                {
                    dwIndex++;
                }

                if (dwIndex == dwLen)
                {
                    return false;
                }

                if (strTime[dwIndex] == '+')
                {
                    dwIndex++;

                    if (!GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        return false;
                    }

                    if (dwNum < 0 || dwNum > 23)
                    {
                        return false;
                    }
                }
                else if (strTime[dwIndex] == '-')
                {
                    dwIndex++;

                    if (!GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        return false;
                    }

                    if (dwNum < 0 || dwNum > 23)
                    {
                        return false;
                    }

                    dwNum = -dwNum;
                }

                dwTimezoneSeconds = dwNum * SECONDS_PER_HOUR;
                // 读取:00
                dwPos = strTime.find(formatInfo.TimeSeparator(), dwIndex);

                if (dwPos == dwIndex)
                {
                    dwIndex += formatInfo.TimeSeparator().length();

                    if (GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        if (dwNum >= 0 && dwNum < 60)
                        {
                            dwTimezoneSeconds += dwNum * 60;
                        }
                    }
                }

                // K需要设置时区
                date_info->timezone_seconds = dwTimezoneSeconds;
            }
            return false;
            // m     0-59
        case FSTK_m:
            // mm,或更多m，00-59
        case FSTK_mm_:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 0 && dwNum <= 59)
                {
                    date_info->minute = dwNum;
                    break;
                }
            }

            return false;
            // M     1-12
        case FSTK_M:
            // MM    01-12
        case FSTK_MM:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 1 && dwNum <= 12)
                {
                    date_info->month = dwNum;
                    break;
                }
            }

            return false;
            // MMM   月份缩略词
        case FSTK_MMM:
            dwNum = 1;

            for (vector<string>::const_iterator itrNames = formatInfo.AbbreviatedMonthNames().begin();
                    itrNames != formatInfo.AbbreviatedMonthNames().end(); ++itrNames)
            {
                dwPos = strTime.find(*itrNames, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex = dwPos + itrNames->length();
                    date_info->month = dwNum;
                    break;
                }

                dwNum++;
            }

            return false;
            // MMMM  月份全名
        case FSTK_MMMM:
            dwNum = 1;

            for (vector<string>::const_iterator itrNames = formatInfo.MonthNames().begin();
                    itrNames != formatInfo.MonthNames().end(); ++itrNames)
            {
                dwPos = strTime.find(*itrNames, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex = dwPos + itrNames->length();
                    date_info->month = dwNum;
                    break;
                }

                dwNum++;
            }

            return false;
            break;
            // s     0-59
        case FSTK_s:
            // ss,或者更多s  00-59
        case FSTK_ss_:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                if (dwNum >= 0 && dwNum <= 59)
                {
                    date_info->second = dwNum;
                    break;
                }
            }

            return false;
            // t     AM，PM标识符的第一个字符
        case FSTK_t:
            {
                string strDst = formatInfo.AMDesignator()[0] < 0 ?
                    formatInfo.AMDesignator().substr(0, 2) :
                    formatInfo.AMDesignator().substr(0, 1);
                dwPos = strTime.find(strDst, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex = dwPos + strDst.length();
                    date_info->is_set_am_or_pm = true;
                    date_info->am_or_pm = true;
                    break;
                }

                strDst = formatInfo.PMDesignator()[0] < 0 ?
                    formatInfo.PMDesignator().substr(0, 2) :
                    formatInfo.PMDesignator().substr(0, 1);
                dwPos = strTime.find(strDst, dwIndex);

                if (dwPos != string::npos &&
                        (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
                {
                    dwIndex = dwPos + strDst.length();
                    date_info->is_set_am_or_pm = true;
                    date_info->am_or_pm = false;
                    break;
                }
            }
            return false;
            // tt，或更多t   AM，PM标识符全称
        case FSTK_tt_:
            dwPos = strTime.find(formatInfo.AMDesignator(), dwIndex);

            if (dwPos != string::npos &&
                    (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
            {
                dwIndex = dwPos + formatInfo.AMDesignator().length();
                date_info->is_set_am_or_pm = true;
                date_info->am_or_pm = true;
                break;
            }

            dwPos = strTime.find(formatInfo.PMDesignator(), dwIndex);

            if (dwPos != string::npos &&
                    (dwPos == dwIndex || IsSpaceChars(strTime, dwIndex, dwPos - dwIndex)))
            {
                dwIndex = dwPos + formatInfo.PMDesignator().length();
                date_info->is_set_am_or_pm = true;
                date_info->am_or_pm = false;
                break;
            }

            return false;
            // y     1-99,将年份表示为1位或者两位数字
        case FSTK_y:
            // yy    两位数，前导符0
        case FSTK_yy:

            if (GetNumFromString(strTime, dwIndex, dwNum, 2))
            {
                int dwCurYear = DateTime::Now().GetYear();
                dwNum += (dwCurYear - dwCurYear % 100);

                if (dwCurYear % 100 > dwNum)
                {
                    dwNum -= 100;
                }

                date_info->year = dwNum;
                break;
            }

            return false;
            // yyy，三位数，前导符0
        case FSTK_yyy:

            if (GetNumFromString(strTime, dwIndex, dwNum, 3))
            {
                date_info->year = dwNum;
                break;
            }

            return false;
            // yyyy，四位数，前导符0
        case FSTK_yyyy:

            if (GetNumFromString(strTime, dwIndex, dwNum, 4))
            {
                date_info->year = dwNum;
                break;
            }

            return false;
            // yyyyy,或更多y，表示为5位数，前导符0
        case FSTK_yyyyy_:

            if (GetNumFromString(strTime, dwIndex, dwNum, 5))
            {
                date_info->year = dwNum;
                break;
            }

            return false;
            // z     +8
        case FSTK_z:
            // zz    +08
        case FSTK_zz:
            // zzz   +08:00
        case FSTK_zzz:
            {
                int dwTimezoneSeconds = 0;

                while (IS_BLANK_SPACE_CHAR(strTime[dwIndex]) && dwIndex < dwLen)
                {
                    dwIndex++;
                }

                if (dwIndex == dwLen)
                {
                    return false;
                }

                if (strTime[dwIndex] == '+')
                {
                    dwIndex++;

                    if (!GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        return false;
                    }

                    if (dwNum < 0 || dwNum > 23)
                    {
                        return false;
                    }
                }
                else if (strTime[dwIndex] == '-')
                {
                    dwIndex++;

                    if (!GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        return false;
                    }

                    if (dwNum < 0 || dwNum > 23)
                    {
                        return false;
                    }

                    dwNum = -dwNum;
                }

                dwTimezoneSeconds = dwNum * SECONDS_PER_HOUR;
                // 读取:00
                dwPos = strTime.find(formatInfo.TimeSeparator(), dwIndex);

                if (dwPos == dwIndex)
                {
                    dwIndex += formatInfo.TimeSeparator().length();

                    if (GetNumFromString(strTime, dwIndex, dwNum, 2))
                    {
                        if (dwNum >= 0 && dwNum < 60)
                        {
                            dwTimezoneSeconds += dwNum * 60;
                        }
                    }
                }

                date_info->timezone_seconds = dwTimezoneSeconds;
                break;
            }
            return false;
            // /
        case FSTK_DATESEP_CHAR:
            dwPos = strTime.find(formatInfo.DateSeparator(), dwIndex);

            if (dwIndex == dwPos)
            {
                dwIndex += formatInfo.DateSeparator().length();
                break;
            }

            return false;
            // :
        case FSTK_TIMESEP_CHAR:
            dwPos = strTime.find(formatInfo.TimeSeparator(), dwIndex);

            if (dwIndex == dwPos)
            {
                dwIndex += formatInfo.TimeSeparator().length();
                break;
            }

            return false;
        default:
            return false;
    }
    return true;
}

void DateTime::MakeDateTime(const DateTimeInfo& date_info, DateTime* dt)
{
    // 首先设置时区
    if (date_info.timezone_seconds != -1) {
        dt->SetTimeZoneSeconds(date_info.timezone_seconds);
    } else {
        dt->SetTimeZoneSeconds(DateTime::Now().GetTimeZoneSeconds());
    }
    if (date_info.hour != -1) {
        if (date_info.is_hour12) {
            dt->SetHour12(date_info.hour, dt->IsAM());
        } else {
            dt->SetHour(date_info.hour);
        }
    }
    if (date_info.day_of_month != -1) {
        dt->SetDayOfMonth(date_info.day_of_month);
    }
    if (date_info.microseconds != -1) {
        dt->m_Time.m_usec = date_info.microseconds;
    }
    if (date_info.minute != -1) {
        dt->SetMinute(date_info.minute);
    }
    if (date_info.month != -1) {
        dt->SetMonth(date_info.month);
    }
    if (date_info.second != -1) {
        dt->SetSecond(date_info.second);
    }
    if (date_info.is_set_am_or_pm) {
        dt->SetAMOrPM(date_info.am_or_pm);
    }
    if (date_info.year != -1) {
        dt->SetYear(date_info.year);
    }
}

int DateTime::GetCurrentTimezoneSeconds()
{
    tzset();
    return -timezone;
}

// *************** TimeCounter *************************

TimeCounter::TimeCounter()
{
    m_TimeSpan = TimeSpan::Zero;
    m_LastTick = GetCurTick();
}

TimeCounter::TimeCounter(const TimeSpan& ts)
{
    m_TimeSpan = ts;
    m_LastTick = GetCurTick();
}

void TimeCounter::Reset()
{
    m_TimeSpan = TimeSpan::Zero;
    m_LastTick = GetCurTick();
}

void TimeCounter::Start()
{
    m_LastTick = GetCurTick();
}

void TimeCounter::Pause()
{
    TimeTick dtNow = GetCurTick();
    m_TimeSpan += TimeSpan(dtNow - m_LastTick);
    m_LastTick = dtNow;
}

TimeSpan TimeCounter::GetTimeSpan() const
{
    return m_TimeSpan;
}

std::string TimeCounter::ToString() const
{
    return m_TimeSpan.ToString();
}

TimeTick TimeCounter::GetCurTick() const
{
#ifdef _WIN32
    LARGE_INTEGER ddwTick;
    QueryPerformanceCounter(&ddwTick);
    LARGE_INTEGER ddwFreq;
    QueryPerformanceFrequency(&ddwFreq);
    TimeTick tt(ddwTick.QuadPart / ddwFreq.QuadPart,
            (int)((ddwTick.QuadPart % ddwFreq.QuadPart) * MICROSECONDS_PER_SECOND /
                ddwFreq.QuadPart));
    return tt;
#else
    return DateTime::Now().m_Time;
#endif
}

// ************************** DateTimeFormatInfo **********************************************

// en-US的DateTimeFormatInfo
const DateTimeFormatInfo DateTimeFormatInfo::en_USInfo("en-US");
// zh-CN的DateTimeFormatInfo
const DateTimeFormatInfo DateTimeFormatInfo::zh_CNInfo("zh-CN");

DateTimeFormatInfo::DateTimeFormatInfo(const std::string& cultureStr /*= "zh-CN"*/)
{
    m_Name = cultureStr;

    if (cultureStr == "en-US")
    {
        _Creat_en_US();
        return;
    }
    else if (cultureStr == "zh-CN")
    {
        _Creat_zh_CN();
        return;
    }

    _Creat_zh_CN();
}

void DateTimeFormatInfo::_Creat_zh_CN()
{
    m_ShortDatePattern = "yyyy-M-d";
    m_LongDatePattern = "yyyy'年'M'月'd'日'";
    m_FullDateTimePattern = "yyyy'年'M'月'd'日' H:mm:ss";
    m_MonthDayPattern = "M'月'd'日'";
    m_RFC1123Pattern = "ddd, dd MMM yyyy HH':'mm':'ss 'GMT'";
    m_SortableDateTimePattern = "yyyy'-'MM'-'dd'T'HH':'mm':'ss";
    m_ShortTimePattern = "H:mm";
    m_LongTimePattern = "H:mm:ss";
    m_UniversalSortableDateTimePattern = "yyyy'-'MM'-'dd HH':'mm':'ss'Z'";
    m_YearMonthPattern = "yyyy'年'M'月'";
    m_RetureBackPattern = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffzz";

    m_EraNames.assign(1, "公元");

    m_AbbreviatedDayNames.assign(7, "");
    m_AbbreviatedDayNames[0] = "日";
    m_AbbreviatedDayNames[1] = "一";
    m_AbbreviatedDayNames[2] = "二";
    m_AbbreviatedDayNames[3] = "三";
    m_AbbreviatedDayNames[4] = "四";
    m_AbbreviatedDayNames[5] = "五";
    m_AbbreviatedDayNames[6] = "六";

    m_DayNames.assign(7, "");
    m_DayNames[0] = "星期日";
    m_DayNames[1] = "星期一";
    m_DayNames[2] = "星期二";
    m_DayNames[3] = "星期三";
    m_DayNames[4] = "星期四";
    m_DayNames[5] = "星期五";
    m_DayNames[6] = "星期六";

    m_AbbreviatedMonthNames.assign(13, "");
    m_AbbreviatedMonthNames[0] = "一月";
    m_AbbreviatedMonthNames[1] = "二月";
    m_AbbreviatedMonthNames[2] = "三月";
    m_AbbreviatedMonthNames[3] = "四月";
    m_AbbreviatedMonthNames[4] = "五月";
    m_AbbreviatedMonthNames[5] = "六月";
    m_AbbreviatedMonthNames[6] = "七月";
    m_AbbreviatedMonthNames[7] = "八月";
    m_AbbreviatedMonthNames[8] = "九月";
    m_AbbreviatedMonthNames[9] = "十月";
    m_AbbreviatedMonthNames[10] = "十一月";
    m_AbbreviatedMonthNames[11] = "十二月";

    m_MonthNames.assign(13, "");
    m_MonthNames[0] = "一月";
    m_MonthNames[1] = "二月";
    m_MonthNames[2] = "三月";
    m_MonthNames[3] = "四月";
    m_MonthNames[4] = "五月";
    m_MonthNames[5] = "六月";
    m_MonthNames[6] = "七月";
    m_MonthNames[7] = "八月";
    m_MonthNames[8] = "九月";
    m_MonthNames[9] = "十月";
    m_MonthNames[10] = "十一月";
    m_MonthNames[11] = "十二月";

    m_AMDesignator = "上午";
    m_PMDesignator = "下午";
    m_TimeSeparator = ":";
    m_DateSeparator = "-";
}

void DateTimeFormatInfo::_Creat_en_US()
{
    m_ShortDatePattern = "M/d/yyyy";
    m_LongDatePattern = "dddd, MMMM dd, yyyy";
    m_FullDateTimePattern = "dddd, MMMM dd, yyyy h:mm:ss tt";
    m_MonthDayPattern = "MMMM dd";
    m_RFC1123Pattern = "ddd, dd MMM yyyy HH':'mm':'ss 'GMT'";
    m_SortableDateTimePattern = "yyyy'-'MM'-'dd'T'HH':'mm':'ss";
    m_ShortTimePattern = "h:mm tt";
    m_LongTimePattern = "h:mm:ss tt";
    m_UniversalSortableDateTimePattern = "yyyy'-'MM'-'dd HH':'mm':'ss'Z'";
    m_YearMonthPattern = "MMMM, yyyy";
    m_RetureBackPattern = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffzz";
    m_EraNames.assign(1, "A.D.");

    m_AbbreviatedDayNames.assign(7, "");
    m_AbbreviatedDayNames[0] = "Sun";
    m_AbbreviatedDayNames[1] = "Mon";
    m_AbbreviatedDayNames[2] = "Tue";
    m_AbbreviatedDayNames[3] = "Wed";
    m_AbbreviatedDayNames[4] = "Thu";
    m_AbbreviatedDayNames[5] = "Fri";
    m_AbbreviatedDayNames[6] = "Sat";

    m_DayNames.assign(7, "");
    m_DayNames[0] = "Sunday";
    m_DayNames[1] = "Monday";
    m_DayNames[2] = "Tuesday";
    m_DayNames[3] = "Wednesday";
    m_DayNames[4] = "Thursday";
    m_DayNames[5] = "Friday";
    m_DayNames[6] = "Saturday";

    m_AbbreviatedMonthNames.assign(13, "");
    m_AbbreviatedMonthNames[0] = "Jan";
    m_AbbreviatedMonthNames[1] = "Feb";
    m_AbbreviatedMonthNames[2] = "Mar";
    m_AbbreviatedMonthNames[3] = "Apr";
    m_AbbreviatedMonthNames[4] = "May";
    m_AbbreviatedMonthNames[5] = "Jun";
    m_AbbreviatedMonthNames[6] = "Jul";
    m_AbbreviatedMonthNames[7] = "Aug";
    m_AbbreviatedMonthNames[8] = "Sep";
    m_AbbreviatedMonthNames[9] = "Oct";
    m_AbbreviatedMonthNames[10] = "Nov";
    m_AbbreviatedMonthNames[11] = "Dec";

    m_MonthNames.assign(13, "");
    m_MonthNames[0] = "January";
    m_MonthNames[1] = "February";
    m_MonthNames[2] = "March";
    m_MonthNames[3] = "April";
    m_MonthNames[4] = "May";
    m_MonthNames[5] = "June";
    m_MonthNames[6] = "July";
    m_MonthNames[7] = "August";
    m_MonthNames[8] = "September";
    m_MonthNames[9] = "October";
    m_MonthNames[10] = "November";
    m_MonthNames[11] = "December";

    m_AMDesignator = "AM";
    m_PMDesignator = "PM";
    m_TimeSeparator = ":";
    m_DateSeparator = "/";
}

const std::vector<std::string> &DateTimeFormatInfo::GetAllPatterns()const
{
    if (m_AllPatterns.size() == 0)
    {
        vector<string> *pVec = (vector<string> *)&m_AllPatterns;
        pVec->push_back(m_LongDatePattern + " " + m_LongTimePattern);
        pVec->push_back(m_LongDatePattern + " " + m_ShortTimePattern);
        pVec->push_back(m_ShortDatePattern + " " + m_LongTimePattern);
        pVec->push_back(m_ShortDatePattern + " " + m_ShortTimePattern);

        pVec->push_back(m_FullDateTimePattern);
        pVec->push_back(m_RFC1123Pattern);
        pVec->push_back(m_RetureBackPattern);
        pVec->push_back(m_SortableDateTimePattern);
        pVec->push_back(m_UniversalSortableDateTimePattern);
        pVec->push_back(m_LongDatePattern);
        pVec->push_back(m_ShortDatePattern);
        pVec->push_back(m_YearMonthPattern);
        pVec->push_back(m_MonthDayPattern);
        pVec->push_back(m_LongTimePattern);
        pVec->push_back(m_ShortTimePattern);
    }

    return m_AllPatterns;
}

// } // namespace common
