#ifndef COMMON_SYSTEM_TIME_DATETIME_H
#define COMMON_SYSTEM_TIME_DATETIME_H

/****************************************************************************
*   TimeSpan：              时间段类
*   DateTime：              日期时间类，windows上精确到毫秒，linux上精确到微秒
*   TimeCounter：           计时器类，计时精确到微秒
*   DateTimeFormatInfo：    时间格式信息类，支持zh-CN,en-US两种日期时间格式
*
*   @modify history:
*       2010.04.20      添加DateTime的标准格式模式和自定义格式模式支持，编写ToString函数；编写TimeSpan的ToString和Parse函数
*       2010.04.21      编写DateTime的Parse函数
*       2010.11.23      修正DateTime::Today()和 Datetime::Time()的bug
*****************************************************************************/

/**
日期标准格式模式和自定义格式模式:
1.标准格式模式，标准格式模式都用一个字符表示。参见MSDN文档：ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/bb79761a-ca08-44ee-b142-b06b3e2fc22b.htm
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
s           使用本地时间的 SortableDateTimePattern（基于 ISO 8601）；在这种格式模式下，格式设置或分析操作始终使用固定区域性
t           ShortTimePattern
T           LongTimePattern
u           使用通用时间显示格式的 UniversalSortableDateTimePattern；在这种格式模式下，格式设置或分析操作始终使用固定区域性
U           使用通用时间的完整日期和时间（长日期和长时间）
y、Y        YearMonthPattern

2.自定义格式模式，其他非模式字符应该用引号括起来。一个字符的自定义模式需要在前面加上%，以区别于标准格式模式
参见MSDN文档：ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/98b374e3-0cc2-4c78-ab44-efb671d71984.htm
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
K       Kind 属性的不同值，即本地、Utc 或未指定。
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
\ c     其中 c 是任意字符。照原义显示字符。若要显示反斜杠字符，应用程序应使用“\\”。         */

#include <stdlib.h>
#include <time.h>
#include <iostream>
#include <string>
#include <vector>

// namespace common {
class TimeSpan;
// }

// namespace common {

/// 表示时间的类
class TimeTick
{
    time_t m_sec;   // 秒数,取值范围[0x8000000000000000,0x7FFFFFFFFFFFFFFF]
    int m_usec;     // 微秒数,取值范围(-1000000,1000000),正负与time相同
public:
    friend class TimeSpan;
    friend class DateTime;

    TimeTick(time_t tm, int us);
    TimeTick(const TimeTick &tt);
    TimeTick();
    void Normalize();
    bool IsNormalized()const;

    TimeTick operator+(const TimeTick &tt)const;
    TimeTick &operator+=(const TimeTick &tt);
    TimeTick operator-(const TimeTick &tt)const;
    TimeTick &operator-=(const TimeTick &tt);
    TimeTick operator-()const;

    bool operator>(const TimeTick &tt)const;
    bool operator<(const TimeTick &tt)const;
    bool operator>=(const TimeTick &tt)const;
    bool operator<=(const TimeTick &tt)const;
    bool operator==(const TimeTick &tt)const;
    bool operator!=(const TimeTick &tt)const;
};

/// 表示一段时间的类
class TimeSpan
{
protected:
    TimeTick m_Time;
public:
    friend class DateTime;
    TimeSpan();

    TimeSpan(const TimeTick &tmTick);
    /// 将新的 TimeSpan 初始化为指定的小时数、分钟数和秒数
    TimeSpan(int dwHour, int dwMinute, int dwSecond);
    /// 将新的 TimeSpan 初始化为指定的天数、小时数、分钟数和秒数
    TimeSpan(int dwDay, int dwHour, int dwMinute, int dwSecond);
    /// 将新的 TimeSpan 初始化为指定的天数、小时数、分钟数、秒数和毫秒数
    TimeSpan(int dwDay, int dwHour, int dwMinute, int dwSecond, int dwMilliSecond);
    /// 将新的 TimeSpan 初始化为指定的天数、小时数、分钟数、秒数、毫秒数和微秒数
    TimeSpan(int dwDay, int dwHour, int dwMinute, int dwSecond,
             int dwMilliSecond, int dwMicroSecond);

    static const TimeSpan Zero;
    static const TimeSpan MaxValue;
    static const TimeSpan MinValue;

    int GetDays()const;
    int GetHours()const;
    int GetMinutes()const;
    int GetSeconds()const;
    int GetMilliSeconds()const;
    int GetMicroSeconds()const;

    double GetTotalDays()const;
    double GetTotalHours()const;
    double GetTotalMinutes()const;
    double GetTotalSeconds()const;
    double GetTotalMilliSeconds()const;
    double GetTotalMicroSeconds()const;


    /** 表示此实例的值的字符串。
    返回值形式如下：
    [-][d.]hh:mm:ss[.ff]
    方括号（“[”和“]”）中的项是可选的，冒号和句号（“:”和“.”）是原义字符，其他项如下。
    项      说明
    “-” 可选的负号，指示负时间
    “d”     可选的天数
    “hh”    小时，范围从 0 到 23
    “mm”    分钟，范围从 0 到 59
    “ss”    秒，范围从 0 到 59
    “ff”    可选的秒的小数部分，有 1 到 7 个小数位      */
    std::string ToString()const;
    /** 从字符串中指定的时间间隔构造新的TimeSpan对象，如果转换失败返回TimeSpan::Zero对象
    strTime 参数包含一个如下形式的时间间隔规范：
    [ws][-]{ d | [d.]hh:mm[:ss[.ff]] }[ws]
    方括号（“[”和“]”）中的项是可选的；需要从大括号（“{”和“}”）内由竖线 (|) 分隔的替换选项列表中选择一项；冒号和句号（“:”和“.”）是必需的原义字符；其他项如下。
    项      说明
    ws      可选的空白
    “-”     可选的减号，指示负 TimeSpan
    d       天，范围从 0 到 10675199
    hh      小时，范围从 0 到 23
    mm      分钟，范围从 0 到 59
    ss      可选的秒，范围从 0 到 59
    ff      可选的秒的小数部分，有 1 到 7 个小数位

    strTime 的分量必须整体指定大于或等于 MinValue 并小于或等于 MaxValue 的时间间隔。        */
    static TimeSpan Parse(const std::string &strTime);
    /// 返回指定TimeTick的TimeSpan
    static TimeSpan FromTick(const TimeTick &tt);
    /// 返回指定天的TimeSpan
    static TimeSpan FromDays(double dwDay);
    /// 返回指定小时的TimeSpan
    static TimeSpan FromHours(double dwHour);
    /// 返回指定分钟的TimeSpan
    static TimeSpan FromMinutes(double dwMinute);
    /// 返回指定秒的TimeSpan
    static TimeSpan FromSeconds(double dwSecond);
    /// 返回指定毫秒的TimeSpan
    static TimeSpan FromMilliSeconds(double dwMilliSecond);
    /// 返回指定微秒的TimeSpan
    static TimeSpan FromMicroSeconds(double dwMicroSecond);

    TimeSpan Abs() const {return *this > TimeSpan::Zero ? *this : -(*this);}

    TimeSpan operator -()const;
    TimeSpan operator +(const TimeSpan &ts)const;
    TimeSpan &operator +=(const TimeSpan &ts);
    TimeSpan operator -(const TimeSpan &ts)const;
    TimeSpan &operator -=(const TimeSpan &ts);
    bool operator>(const TimeSpan &ts)const;
    bool operator<(const TimeSpan &ts)const;
    bool operator>=(const TimeSpan &ts)const;
    bool operator<=(const TimeSpan &ts)const;
    bool operator==(const TimeSpan &ts)const;
    bool operator!=(const TimeSpan &ts)const;
};

/// 模式串的一个原子片段的类型，详细参见自定义格式模式
enum FormatSegmentTokenKind
{
    FSTK_String = 0, // 常规字符串类型
    FSTK_d,      // 1-31日期
    FSTK_dd,     // 01-31日期
    FSTK_ddd,    // 一周中某一天的缩写
    FSTK_dddd_,  // 一周中某一天的全称
    FSTK_f,      // 秒精确到一位小数，不忽略后缀零
    FSTK_ff,     // 秒精确到两位小数，不忽略后缀零
    FSTK_fff,    // 秒精确到三位小数，不忽略后缀零
    FSTK_ffff,   // 秒精确到四位小数，不忽略后缀零
    FSTK_fffff,  // 秒精确到五位小数，不忽略后缀零
    FSTK_ffffff, // 秒精确到六位小数，不忽略后缀零
    FSTK_F,      // 秒精确到一位小数，忽略后缀零
    FSTK_FF,     // 秒精确到两位小数，忽略后缀零
    FSTK_FFF,    // 秒精确到三位小数，忽略后缀零
    FSTK_FFFF,   // 秒精确到四位小数，忽略后缀零
    FSTK_FFFFF,  // 秒精确到五位小数，忽略后缀零
    FSTK_FFFFFF, // 秒精确到六位小数，忽略后缀零
    FSTK_g_,     // 纪元，A.D.
    FSTK_h,      // 1-12
    FSTK_hh_,    // 01-12
    FSTK_H,      // 0-23
    FSTK_HH_,    // 00-23
    FSTK_K,      // 时区，localtime相当于zzz
    FSTK_m,      // 0-59
    FSTK_mm_,    // 00-59
    FSTK_M,      // 1-12
    FSTK_MM,     // 01-12
    FSTK_MMM,    // 月份简写
    FSTK_MMMM,   // 月份全称
    FSTK_s,      // 0-59
    FSTK_ss_,    // 00-59
    FSTK_t,      // AM，PMDesigner的第一个字符
    FSTK_tt_,    // AM，PMDesigner的全称
    FSTK_y,      // 一位或者两位年
    FSTK_yy,     // 两位年
    FSTK_yyy,    // 三位年
    FSTK_yyyy,   // 四位年
    FSTK_yyyyy_, // 五位年
    FSTK_z,      // +8
    FSTK_zz,     // +08
    FSTK_zzz,    // +08:00
    FSTK_TIMESEP_CHAR,  // 时间分隔符，一般是:
    FSTK_DATESEP_CHAR,  // 日期分隔符，一般是/
};

struct DateTimeInfo
{
    int year;
    int month;
    int day_of_month;
    int hour;
    int minute;
    int second;
    int microseconds;
    int timezone_seconds;

    bool is_hour12;         // 标示是否是12小时制
    bool is_set_am_or_pm;   // 标示是否设置am或者pm
    bool am_or_pm;          // 当is_set_am_or_pm有效时，设置am或者pm

    DateTimeInfo()
    {
        year = -1;
        month = -1;
        day_of_month = -1;
        hour = -1;
        minute = -1;
        second = -1;
        microseconds = -1;
        timezone_seconds = -1;
        is_hour12 = false;
        is_set_am_or_pm = false;
        am_or_pm = false;
    }
};

/// DateTime格式串片段
struct FormatSegment
{
    std::string strSeg;
    FormatSegmentTokenKind dwKind;
};

/// DateTimeFormatInfo
class DateTimeFormatInfo
{
    // 标准模式
    std::string m_ShortDatePattern;
    std::string m_LongDatePattern;
    std::string m_FullDateTimePattern;
    std::string m_MonthDayPattern;
    std::string m_RFC1123Pattern;
    std::string m_SortableDateTimePattern;
    std::string m_ShortTimePattern;
    std::string m_LongTimePattern;
    std::string m_UniversalSortableDateTimePattern;
    std::string m_YearMonthPattern;
    std::string m_RetureBackPattern;

    std::vector<std::string> m_AbbreviatedDayNames;
    std::vector<std::string> m_DayNames;
    std::vector<std::string> m_AbbreviatedMonthNames;
    std::vector<std::string> m_MonthNames;

    std::vector<std::string> m_EraNames;

    std::vector<std::string> m_AllPatterns;

    std::string m_AMDesignator;
    std::string m_PMDesignator;
    std::string m_TimeSeparator;
    std::string m_DateSeparator;

    std::string m_Name;
    // 常用pattern
    std::vector<std::string> m_vecGeneralPattern;
    // zh-CN,en-US等
    explicit DateTimeFormatInfo(const std::string &cultureStr = "zh-CN");
public:
    const std::string &ShortDatePattern()const {
        return m_ShortDatePattern;
    }
    const std::string &RetureBackPattern()const {
        return m_RetureBackPattern;
    }
    const std::string &LongDatePattern()const {
        return m_LongDatePattern;
    }
    const std::string &FullDateTimePattern()const {
        return m_FullDateTimePattern;
    }
    const std::string &MonthDayPattern()const {
        return m_MonthDayPattern;
    }
    const std::string &RFC1123Pattern()const {
        return m_RFC1123Pattern;
    }
    const std::string &SortableDateTimePattern()const {
        return m_SortableDateTimePattern;
    }
    const std::string &ShortTimePattern()const {
        return m_ShortTimePattern;
    }
    const std::string &LongTimePattern()const {
        return m_LongTimePattern;
    }
    const std::string &UniversalSortableDateTimePattern()const {
        return m_UniversalSortableDateTimePattern;
    }
    const std::string &YearMonthPattern()const {
        return m_YearMonthPattern;
    }

    /// 获取常用模式集合
    const std::vector<std::string> &GeneralPatterns()const {
        return m_vecGeneralPattern;
    }
    /// 周中某天缩写
    const std::vector<std::string> &AbbreviatedDayNames()const {
        return m_AbbreviatedDayNames;
    }
    /// 周中某天全称
    const std::vector<std::string> &DayNames()const {
        return m_DayNames;
    }
    /// 月份的缩写
    const std::vector<std::string> &AbbreviatedMonthNames()const {
        return m_AbbreviatedMonthNames;
    }
    /// 月份的全称
    const std::vector<std::string> &MonthNames()const {
        return m_MonthNames;
    }
    /// 纪元名，如：A.D.， 公元等
    const std::vector<std::string> &EraNames()const {
        return m_EraNames;
    }
    /// AM描述符
    const std::string &AMDesignator()const {
        return m_AMDesignator;
    }
    /// PM描述符
    const std::string &PMDesignator()const {
        return m_PMDesignator;
    }
    /// 时分秒之间的分隔符，默认为':'
    const std::string &TimeSeparator()const {
        return m_TimeSeparator;
    }
    /// 年月日之间的分隔符，默认为'/'
    const std::string &DateSeparator()const {
        return m_DateSeparator;
    }

    /// datetimeformatinfo的名字，zh-CN,en-US等
    const std::string &Name()const {
        return m_Name;
    }

    /// 获取所有的时间模式
    const std::vector<std::string> &GetAllPatterns()const;

    /// en-US的DateTimeFormatInfo
    static const DateTimeFormatInfo en_USInfo;
    /// zh-CN的DateTimeFormatInfo
    static const DateTimeFormatInfo zh_CNInfo;

private:
    void _Creat_zh_CN();
    void _Creat_en_US();
};


/// 表示日期时间的类
class DateTime
{
    // 从1970年1月1日午夜(00:00:00)起累计的时间
    TimeTick m_Time;
    // UTC时间的差值,秒，local = utc + dw
    int m_dwTimezoneSeconds;
public:
    friend class TimeCounter;
    explicit DateTime(int dwTimezoneSeconds = -1);
    explicit DateTime(const TimeTick &tmTick, int dwTimezoneSeconds = -1);
    explicit DateTime(const time_t &tm, int usec = 0,  int dwTimezoneSeconds = -1);
    DateTime(int dwYear, int dwMonth , int dwDay ,
             int dwHour = 0, int dwMinute = 0, int dwSecond = 0,
             int dwMilliSecond = 0, int dwMicroSecond = 0,
             int dwTimezoneSeconds = -1);

    time_t GetSecondsSinceEpoch() const;

    // by zhangyang
    //std::string ToString(DateTime& dt, const std::string& format);
    
    /// 获取年
    int GetYear()const;
    /// 获取月份
    int GetMonth()const;
    /// 获取一个月的第几天，1-31
    int GetDayOfMonth()const;
    /// 获取一年的第几天
    int GetDayOfYear()const;
    /// 获取一周的某天，0-6
    int GetDayOfWeek()const;
    /// 获取小时，24小时制
    int GetHour()const;
    /// 获取小时，12小时制
    int GetHour12()const;
    /// 获取分钟部分
    int GetMinute()const;
    /// 获取秒部分
    int GetSecond()const;
    /// 获取毫秒部分
    int GetMilliSecond()const;
    /// 获取微秒部分
    int GetMicroSecond()const;
    /// 获取时区，北京时间是+8
    int GetTimeZone()const;
    /// 获取时区，用与UTC时间相差的秒数表示
    int GetTimeZoneSeconds()const;
    /// 获取日期
    DateTime GetDay()const;
    /// 获取时间
    TimeSpan GetTime()const;
    /// 获取UTC时间
    DateTime GetUTCDateTime()const;
    /// 设置年
    void SetYear(int dwYear);
    /// 设置月份
    void SetMonth(int dwMonth);
    /// 设置一个月的第几天，1-31
    void SetDayOfMonth(int dwDay);
    /// 设置小时，24小时制
    void SetHour(int dwHour);
    /// 设置小时，12小时制
    void SetHour12(int dwHour12, bool bAM);
    /// 设置分钟部分
    void SetMinute(int dwMinute);
    /// 设置秒部分
    void SetSecond(int dwSecond);
    /// 设置毫秒部分
    void SetMilliSecond(int dwMilliSecond);
    /// 设置微秒部分
    void SetMicroSecond(int dwMicroSecond);
    /// 设置时区，北京时间是+8
    void SetTimeZone(int dwTimeZone);
    /// 设置时区，用与UTC时间相差的秒数表示
    void SetTimeZoneSeconds(int dwTimezoneSeconds);
    /// 设置日期
    void SetDay(const DateTime &dt);
    /// 设置时间
    void SetTime(const TimeSpan &ts);
    /// 设置AM或者PM
    void SetAMOrPM(bool bAM);
    /// 是否是AM
    bool IsAM()const;
    /// 是否是PM
    bool IsPM()const;
    /// 是否是闰年
    bool IsLeapYear()const;
    /// 是否是闰年
    static bool IsLeapYear(int dwYear);
    /// 是否是一个有效的年月日
    static bool IsValidDate(int dwYear, int dwMonth , int dwDay);

    /// 将时间转化为时间串,默认使用模式：标准模式"F"与自定义模式"FFFFFF"的组合，中间用'.'隔开，zh-CN
    std::string ToString(const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo)const;

    /// 把时间转换为字符串，按照指定的格式
    /// 格式串详情参见MSDN文档 ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/bb79761a-ca08-44ee-b142-b06b3e2fc22b.htm
    /// 和ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/98b374e3-0cc2-4c78-ab44-efb671d71984.htm
    std::string ToString(
        const std::string &strFormat,
        const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo)const;

    /// 从时间串读取时间,按照指定的格式，创建失败会返回当前时间，
    /// 默认为本地时间，缺失date用当前日期代替
    /// 格式串详情参见MSDN文档 ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/bb79761a-ca08-44ee-b142-b06b3e2fc22b.htm
    /// 和ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/98b374e3-0cc2-4c78-ab44-efb671d71984.htm
    static DateTime Parse(
        const std::string &strTime,
        const std::string &strFormat,
        const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo);

    /// 从时间串读取时间,创建失败会返回当前时间,尽可能的把字符串转换为DateTime,
    /// 缺失的年月日用当前年月日代替，没有time用12:00:00.000000代替,默认为本地时间
    /// 该函数没有优化性能，如果可能请使用指定strFormat的函数版本
    static DateTime Parse(
        const std::string &strTime,
        const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo);

    /// 从时间串读取时间,按照指定的格式，创建失败会返回当前时间。
    /// 默认为本地时间，缺失date用当前日期代替
    /// 格式串详情参见MSDN文档 ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/bb79761a-ca08-44ee-b142-b06b3e2fc22b.htm
    /// 和ms-help://MS.MSDNQTR.v90.chs/dv_fxfund/html/98b374e3-0cc2-4c78-ab44-efb671d71984.htm
    static bool TryParse(
        const std::string &strTime,
        const std::string &strFormat,
        DateTime & dt,
        const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo);

    /// 从时间串读取时间,创建失败会返回当前时间,尽可能的把字符串转换为DateTime,
    /// 缺失的年月日用当前年月日代替，没有time用12:00:00.000000代替,默认为本地时间
    static bool TryParse(
        const std::string &strTime,
        DateTime& dt,
        const DateTimeFormatInfo &formatInfo = DateTimeFormatInfo::zh_CNInfo);


    /// 返回当前日期和时间
    static DateTime Now();
    /// UTC当前时间
    static DateTime UTCNow();
    /// 返回当前日期
    static DateTime Today();
    /// 返回当前时间
    static TimeSpan Time();

    TimeSpan operator-(const DateTime &dt) const;
    DateTime operator-(const TimeSpan &ts) const;
    DateTime operator+(const TimeSpan &ts) const;

    DateTime &operator-=(const TimeSpan &ts);
    DateTime &operator+=(const TimeSpan &ts);

    bool operator>(const DateTime &ts)const;
    bool operator<(const DateTime &ts)const;
    bool operator>=(const DateTime &ts)const;
    bool operator<=(const DateTime &ts)const;
    bool operator==(const DateTime &ts)const;
    bool operator!=(const DateTime &ts)const;

private:
    /// 展开预定义模式为自定义模式串
    std::string ExpandPredefinedFormat(
        const std::string &strFormat,
        const DateTimeFormatInfo &formatInfo,
        DateTime& dt) const;

    /// 根据格式串片段获取模式类别
    static bool ParseFormatSegment(FormatSegment* seg);

    /// 格式串分割成一系列片段
    static bool SegmentFormatString(const std::string &strFormat,
                                    std::vector<FormatSegment> &vecSegment);

    /// 将dt按照自定义模式串转化为字符串
    static std::string ToFormatString(
        const DateTime &dt,
        const std::string &strFormat,
        const DateTimeFormatInfo& formatInfo);

    /// 将dt按照自定义模式串片段序列转化为字符串
    static std::string ToFormatString(
        const DateTime &dt,
        const std::vector<FormatSegment> &vecSegment,
        const DateTimeFormatInfo& formatInfo);

    /// 匹配一个segment，返回成功与否
    static bool TryParseSegment(
        const std::string &strTime,
        size_t &dwIndex, const std::vector<FormatSegment> &vecSegment,
        const size_t dwSegIndex,
        DateTimeInfo* dateInfo,
        const DateTimeFormatInfo &formatInfo);

    /// 根据DateTimeInfo的内容设置dt的各个项
    static void MakeDateTime(const DateTimeInfo& dateInfo, DateTime* dt);

    /// 得到当前时区和UTC时间的差值（秒数）
    static int GetCurrentTimezoneSeconds();
};

/// 计时器类
class TimeCounter
{
    TimeSpan m_TimeSpan;
    TimeTick m_LastTick;
public:
    TimeCounter();
    explicit TimeCounter(const TimeSpan &ts);

    /// 重新计时
    void Reset();
    /// 开始计时
    void Start();
    /// 暂停计时
    void Pause();
    /// 获取计时器累计时间
    TimeSpan GetTimeSpan()const;
    /// 将计时器时间，转换为字符串
    std::string ToString()const;
private:
    TimeTick GetCurTick()const;
};

// } // namespace common

#endif // COMMON_SYSTEM_TIME_DATETIME_H

