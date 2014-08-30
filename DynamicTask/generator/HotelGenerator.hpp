#ifndef _HOTEL_GENERATOR_HPP
#define _HOTEL_GENERATOR_HPP

/*
 *  AUTHOR: ZHANGYANG
 *  DATE: 2014.08.19
 *  BRIEF: 酒店任务自动生成
 */

#include <string>
#include <vector>
#include <mysql/mysql.h>
#include <tr1/unordered_map>
#include "json/json.h"
using namespace std;

typedef tr1::unordered_map< string, tr1::unordered_map<string, string> > TASK_DATA;
typedef tr1::unordered_map< string, float > TASK_SCORE;
typedef tr1::unordered_map< string, float > HOTEL_DATA;
typedef tr1::unordered_map< string, float > CITY_DATA;

class HotelGenerator
{
    public:
        HotelGenerator();
        ~HotelGenerator();

    public:
        /*
         * 获得下一个时间槽的任务
         * @param: hotel_data, 回写的hotel任务数据
         * @param: hotel_score, 返回的任务key及评分
         */
        void genNext5minTasks(const TASK_DATA& hotel_data, TASK_SCORE& hotel_score);
        
        /*
         * 计算一个任务的得分
         * @param: workload_key
         * @param: updatetime, 上次更新时间
         * @param: price_wave, 价格波动
         */
        float getTaskScore(const string& workload_key, const string& updatetime, float price_wave);
        
        // 城市得分
        float getCityScore(const string& city_en);
        // 酒店得分
        float getHotelScore(const string& uid);
        // 入住日期得分，比如圣诞，元旦等假期
        float getCheckinDayScore(const string& checkin_day);
        // 入住日期距离当前间隔的得分
        float getDayIntervalScore(const string& checkin_day);
        // 入住天数的得分
        float getDaysScore(int days);
        // 源加权
        float getSourceScore(const string& source);
        // 更新时间加权
        float getUpdateRewardScore(const string& updatetime);

    private:
        bool connect2DB(MYSQL* mysql, const string& host, const string& user, const string& passwd, const string& db);
        bool loadCityLevel();
        bool loadHotelLevel();
        bool loadHotelGrade();
        bool loadHotelComment();
        float getSourceLevelScore(const string& source);
        float getSourceRewardScore(const string& source);

    private:
        CITY_DATA m_city_level_map;
        HOTEL_DATA m_hotel_comment_map;
        HOTEL_DATA m_hotel_grade_map;
        HOTEL_DATA m_hotel_level_map;
        DateTime m_now;
};


#endif  // _HOTEL_GENERATOR_HPP
