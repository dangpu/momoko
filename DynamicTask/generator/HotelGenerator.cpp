#include <iostream>
#include "common/datetime/datetime.h"
#include "HotelGenerator.hpp"

HotelGenerator::HotelGenerator()
{
}


HotelGenerator::~HotelGenerator()
{
}

// public
//
float HotelGenerator::getTaskScore(const string& workload_key, const string& updatetime, float price_wave)
{
    float score = 0.0;
    
    // 解析workload_key
    vector<string> vec;
    SplitString(workload_key, "|", &vec);
    string city = vec[0];
    string hotel_sourceid = vec[1];
    string source = vec[2];
    string days = vec[3];
    string checkin_day = vec[4];
    string hotel_id = getHotelId(const string& source, const string& hotel_sourceid);

    // 动态得分
    float update_score = getUpdateRewardScore(updatetime);
    
    // 静态日期得分
    float checkin_score = getCheckinDayScore(checkin_day);
    float interval_score = getDayIntervelScore(checkin_day);
    float days_score = getDaysScore(days);

    // 静态酒店得分
    float city_score = getCityScore(city);
    float hotel_score = getHotelScore(hotel_id);

    // 最终得分
    score ＝ price_wave*update_score + checkin_score*interval_score*days_score + city_score*hotel_score;
    return score;
}


float HotelGenerator::getCityScore(const string& city_en)
{
    if(city_en == 'NULL')
        return 1.0;
    else
        return m_city_level_map[city_en];
}

float HotelGenerator::getHotelScore(const string& uid)
{
    return 1.0;
}

float HotelGenerator::getCheckinDayScore(const string& checkin_day)
{
    return 1.0;
}

float HotelGenerator::getDayIntervalScore(const string& checkin_day)
{
    // 获取间隔天数
    DateTime checkin_dt = DateTime::Parse(checkin_day, "yyyyMMdd");
    TimeSpan ts = checkin_dt - m_today;
    int interval_days = ts.GetDays();
    // Interval越小，得分越高
    return (100.0 - interval_days) / 100.0
}

float HotelGenerator::getDaysScore(int days)
{
    return 1.0;
}

float HotelGenerator::getSourceScore(const string& source)
{
    return getSourceLevelScore(source) * getSourceRewardScore(source);
}


float HotelGenerator::getUpdateRewardScore(const string& updatetime)
{
    // 更新时间越久，得分越高
    //
    // 获取未更新时间（秒）
    Datetime update_dt  = DateTime::Parse(updatetime, "yyyyMMdd");
    TimeSpan ts = m_now - update_dt;
    int non_update_seconds = ts.GetSeconds();
    
    // 如果两天未更新，返回一个极大值
    if(non_update_seconds > 48*3600)
        return 100.0;
    else
        return 100*non_update_seconds/(48*3600)
}

// private
//
bool HotelGenerator::connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd)
{
    mysql_init(mysql);
    if (!mysql_real_connect(mysql, host.c_str(), user.c_str(), passwd.c_str(), db.c_str(), 0, NULL, 0)) 
    {   
        _ERROR("[Connect to %s error: %s]", db.c_str(), mysql_error(mysql));
        return false;
    }   
    // 设置字符编码
    if (mysql_set_character_set(mysql, "utf8"))
    {
        _ERROR("[Set mysql characterset: %s]", mysql_error(mysql));
        return false;
    }
    return true;
}


bool HotelGenerator::loadCityLevel()
{
}

bool HotelGenerator::loadHotelLevel()
{
}

bool HotelGenerator::loadHotelComment()
{
}

bool HotelGenerator::loadHotelGrade()
{
}

float HotelGenerator::getSourceLevelScore(const string& source)
{
    return 1.0;
}

float HotelGenerator::getSourceRewardScore(const string& source)
{
    return 1.0;
}
