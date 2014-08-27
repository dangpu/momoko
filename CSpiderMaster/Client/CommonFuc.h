#ifndef __COMMONFUC_FUNC_H__
#define __COMMONFUC_FUNC_H__

#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <fstream>
#include <sys/time.h>

namespace COMMON
{
	
class MYLog{
private:
	static pthread_mutex_t _locker;
	static time_t _time;
	static std::ofstream _file;
	static std::string _dir;
public:
	static void write(const std::string& log);
	static void write(const int& log);
	static void init(const std::string& dir);
};

//������ʱ����
class MYTimer{
private:
	struct timeval _b;
	struct timeval _e;
public:
	MYTimer(){
		gettimeofday(&_b,NULL);
	}
	void start(){
		gettimeofday(&_b,NULL);
	};
	int cost(){
		gettimeofday(&_e,NULL);
		return (_e.tv_sec-_b.tv_sec)*1000000+(_e.tv_usec-_b.tv_usec);
	}
};

template<class InT,class OutT>
class Transfer{
	public:
	static OutT convert(const InT& inValue){
		std::stringstream ss;
		ss<<inValue;
		OutT res;
		ss>>res;
		return res;
	}
};


template<class InT,class OutT>
OutT convert(const InT& inValue){
	std::stringstream ss;
	ss<<inValue;
	OutT res;
	ss>>res;
	return res;
}

std::vector<std::string> toCharactor(const std::string& in);

//���ַ����и�Ϊ����
std::vector<std::string> sepString(std::string input, const std::string& sep);
//���ַ����и�Ϊ����
void sepString(std::string input, const std::string& sep,std::vector<std::string>& output);
//���ַ����и�Ϊmap
std::map<std::string,std::string> sepString2Map(std::string input, const std::string& item_sep,const std::string& kv_sep);
//�ַ���ɾ��ǰ��ĺͺ��������
std::string rmHeadTail(const std::string& str,const std::string& head,const std::string& tail);

void removeCharsFirstANDLast(std::string& strIn, const std::string& firstChars,const std::string& lastChars);
bool replaceString(std::string& ori_str,const std::string& rep_from,const std::string& rep_to);
std::string Unicode2UTF8(const std::vector<unsigned int>& unicode);

std::vector<unsigned int> UTF82Unicode(const std::string& utf8);
int getUTF8CharLength(const char curChar);
std::vector<std::string> extractAlphaNumberString(const std::string& in);


//���תȫ�� ����ȫ���ַ�������Ҫ�Լ��ͷŷ��ص�ָ��ָ����ڴ档
std::string Half2Full4GBK(const char *src);

//ȫ��ת��� ����ȫ���ַ�������Ҫ�Լ��ͷŷ��ص�ָ��ָ����ڴ档
std::string Full2Half4GBK(const char *src);

std::string extractChars4GBK(const char *src,const std::string& gap);

//ȥ������ĩβ�����
std::string removeVarIndex(const std::string& str);

//˫�ֽڱ����ַ�����find
int find2Byte(const std::string& str,const std::string& tar,int pos=0);

//˫�ֽڱ����ַ�����rfind
int rfind2Byte(const std::string& str,const std::string& tar,int pos=std::string::npos);

//�ַ�����������㷨SUNDAY
int find_sunday(const char* t,const char* p,const int& t_size,const int& p_size);

//�ַ�����������㷨SUNDAY
int rfind_sunday(const char* t,const char* p,const int& t_size,const int& p_size);

//������õ�vector�в����Ƿ����һ��Ԫ��
bool isfind_vec(const int& val,const std::vector<int>& vec);


//ɾ��ȫ��GBK�����еı�����
std::string removePunctuation4GBK_Full(const std::string& str);
//GBKתUTF8
int gbk_to_utf8(const char * in, size_t inlen,char * out, size_t* outlen);

		

int code_convert(char *from_charset,char *to_charset,const char *inbuf, size_t inlen,char *outbuf, size_t& outlen);
 
/* UTF-8 to GBK  */
int u2g(const char *inbuf, size_t inlen, char *outbuf, size_t& outlen);
 
/* GBK to UTF-8 */
int g2u(const char *inbuf, size_t inlen, char *outbuf, size_t& outlen);

/*URL ENCODE*/
std::string url_encode(const std::string& src);

//10:10���Ʊ�ʾ 2:�����Ʊ�ʾ 8:�˽���
void printString(const std::string& str,int type=10);

//���滯XML����ԭʼXML(data)�Ĺ淶���ı��ŵ�val��
int xml_parse(const char *data, size_t data_len, char *val, size_t &val_len);

//ʱ��ת��
class MYTime{
public:
//���ݵ�ǰʱ���ȡָ��ʱ����������ʱ�����Ϣ
//"%Y":�� "%M":�� "%D":�� "%h":Сʱ "%m":����
static int get(const time_t& t,const std::string& mod,int zone=8){
	struct tm *TM;
	time_t nt = t+zone*3600;
	TM = gmtime(&nt);
	if (TM==NULL || mod.length()<2){
		return -1;
	}
	int ret = 0;
	for (size_t i=1;i<mod.size();i++){
		switch(mod[i]){
			case 'Y':
				ret = ret*10000 + TM->tm_year+1900;
				break;
			case 'M':
				ret = ret*100 + TM->tm_mon + 1;
				break;
			case 'D':
				ret = ret*100 + TM->tm_mday;
				break;
			case 'h':
				ret = ret*100 +  TM->tm_hour;
				break;
			case 'm':
				ret = ret*100 +  TM->tm_min;
				break;
			default:
				break;
		}
	}
	return ret;
}

static int getHour(const time_t& t,int zone=8){
	return ((t/3600+zone)%24);
}

static std::string toString(const time_t& t,int zone=8,const char* disp="%Y%m%d_%R"){
	time_t tz = t + zone*3600;
	struct tm *TM;
	TM = gmtime(&tz);
	if (TM==NULL){
		return "";
	}
	char buff[15];
	//strftime(buff,15,"%Y%m%d_%R",TM);
	strftime(buff,15,disp,TM);
	buff[14] = '\0';
	return (std::string)buff;
}

static time_t toTime(const std::string& s/*20131122_18:40*/,int zone=8){
	/*
	int y,mon,d,h,min;
	sscanf(s.c_str(),"%4d%2d%2d_%d:%d",&y,&mon,&d,&h,&min);
	struct tm TM;
	TM.tm_year = y-1900;
	TM.tm_mon = mon-1;
	TM.tm_mday = d;
	TM.tm_hour = h;
	TM.tm_min = min;
	std::cerr<<TM.tm_year<<" "<<TM.tm_mon<<" "<<TM.tm_mday<<" "<<TM.tm_hour<<" "<<TM.tm_min<<std::endl;
	return mktime(&TM);
	*/

	char* tz;
	tz = getenv("TZ");
    setenv("TZ", "", 1);
    tzset();
	struct tm TM;
	strptime(s.c_str(),"%Y%m%d_%H:%M",&TM);
    TM.tm_sec = 0;
	
	//std::cerr<<TM.tm_year<<" "<<TM.tm_mon<<" "<<TM.tm_mday<<" "<<TM.tm_hour<<" "<<TM.tm_min<<std::endl;
	time_t ret = mktime(&TM)-zone*3600;
	if (tz)
		setenv("TZ", tz, 1);
	else
		unsetenv("TZ");
	tzset();
	return ret;
}
static int compareDayStr(const std::string& a,const std::string& b){
	if (a==b)
		return 0;
	time_t a_t = toTime(a+"_00:00",0);
	time_t b_t = toTime(b+"_00:00",0);
	return (b_t-a_t)/86400;
}
static int compareTimeStr(const std::string& a,const std::string& b){
	time_t a_t = toTime(a,0);
	time_t b_t = toTime(b,0);
	return (b_t-a_t);
}
};


};//namespace SOGOUCHAT

#endif //__COMMONFUC_FUNC_H__


