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
	//初始化
	bool init(const std::string& addr);
	/*执行命令*/
	bool get(const std::string& key,std::string& val);		//获取指定key的val
	bool get(const std::vector<std::string>& keys,std::vector<std::string>& vals);		//获取多个key的val
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
