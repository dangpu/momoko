#ifndef __MY_REDIS_H__
#define __MY_REDIS_H__

#include <vector>
#include <string>
#include <hiredis/hiredis.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>


class MyRedis{
public:
	MyRedis();
	~MyRedis();
	//��ʼ��
	bool init(const std::string& addr);
	/*ִ������*/
	bool get(const std::string& key,std::string& val);		//��ȡָ��key��val
	bool get(const std::vector<std::string>& keys,std::vector<std::string>& vals);		//��ȡ���key��val
	bool set(const std::string& key,const std::string& val);
private:
	redisReply* doCMD(const char* key);
	bool reConnect();
private:
	redisContext* _redis_cnn;
	std::string _ip;
	int _port;
	pthread_mutex_t mutex_locker_;
};




#endif	//__MY_REDIS_H__
