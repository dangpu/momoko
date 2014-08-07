#include "MyRedis.h"
#include <iostream>

using namespace std;


redisReply* MyRedis::doCMD(const char* cmd){
	if (_redis_cnn)
		return (redisReply*)redisCommand(_redis_cnn,cmd);
	else
		return NULL;
}


bool MyRedis::set(const std::string& key,const std::string& val){
	if (pthread_mutex_lock(&mutex_locker_)!=0){
		cerr<<"[ERROR]::MyRedis lock failed"<<endl;
		return false;
	}
	redisReply* r = doCMD(("set "+key+" "+val).c_str());
	if (r==NULL){
		if (reConnect()){
			r = doCMD(("set "+key+" "+val).c_str());
		}else{
			cerr<<"[MyRedis::set] failed->"<<key<<endl;
			pthread_mutex_unlock(&mutex_locker_);
			return false;
		}
	}
	if (r==NULL){
		cerr<<"[MyRedis::set] failed->"<<key<<endl;
		pthread_mutex_unlock(&mutex_locker_);
		return false;
	}
	if(!(r->type == REDIS_REPLY_STATUS && strcasecmp(r->str,"OK")==0)){  
		cerr<<"[MyRedis::set] failed->"<<key<<endl;
		freeReplyObject(r);
		pthread_mutex_unlock(&mutex_locker_);
		return false;
	}
	freeReplyObject(r);
	pthread_mutex_unlock(&mutex_locker_);
	return true;
}
bool MyRedis::get(const std::vector<std::string>& keys,std::vector<std::string>& vals){
	string cmd = "mget";
	vals.clear();
	int i;
	for (i=0;i<keys.size();i++){
		cmd += (" "+keys[i]);
	}
	
	if (pthread_mutex_lock(&mutex_locker_)!=0){
		cerr<<"[ERROR]::MyRedis lock failed"<<endl;
		return false;
	}
	
	redisReply* r = doCMD(cmd.c_str());
	if (r==NULL){
		if (reConnect()){
			r = doCMD(cmd.c_str());
		}else{
			cerr<<"[MyRedis::mget] failed->"<<cmd<<endl;
			pthread_mutex_unlock(&mutex_locker_);
			return false;
		}
	}
	if (r==NULL){
		cerr<<"[MyRedis::mget] failed->"<<cmd<<endl;
		pthread_mutex_unlock(&mutex_locker_);
		return false;
	}
	if(r->type != REDIS_REPLY_ARRAY){ 
		cerr<<"[MyRedis::mget] failed->"<<cmd<<endl;
		freeReplyObject(r);
		pthread_mutex_unlock(&mutex_locker_);
		return false;
  }
  for (i=0;i<r->elements;i++){
  	redisReply* childReply = r->element[i];
  	if (childReply->type == REDIS_REPLY_STRING){
  		vals.push_back(childReply->str);
  	}else if (childReply->type == REDIS_REPLY_NIL){
  		vals.push_back("");
  	}
  }

	freeReplyObject(r);

	pthread_mutex_unlock(&mutex_locker_);
	
	if (vals.size()!=keys.size()){
  	vals.clear();
  	cerr<<"[ERROR]:MyRedis::mget() keys' size not match vals'->"<<cmd<<endl;
  }
	return true;
}

bool MyRedis::get(const std::string& key,std::string& val){
	val = "";
	if (key.length()==0){
		cerr<<"null key"<<endl;
		return false;
	}
	
	if (pthread_mutex_lock(&mutex_locker_)!=0){
		cerr<<"[ERROR]::MyRedis lock failed"<<endl;
		return false;
	}
	
	redisReply* r = doCMD(("get "+key).c_str());
	if (r==NULL){
		if (reConnect()){
			r = doCMD(("get "+key).c_str());
		}else{
			cerr<<"[MyRedis::get] failed->"<<key<<endl;
			pthread_mutex_unlock(&mutex_locker_);
			return false;
		}
	}
	if (r==NULL){
		cerr<<"[MyRedis::get] failed->"<<key<<endl;
		pthread_mutex_unlock(&mutex_locker_);
		return false;
	}

	if(r->type != REDIS_REPLY_STRING){ 
		if (r->type != REDIS_REPLY_NIL){
			cerr<<"[MyRedis::get] failed->"<<key<<endl;
			freeReplyObject(r);
			pthread_mutex_unlock(&mutex_locker_);
			return false;
		}else{
			freeReplyObject(r);
			pthread_mutex_unlock(&mutex_locker_);
			return true;
		}
	}    

	val = r->str;
	freeReplyObject(r);
	pthread_mutex_unlock(&mutex_locker_);
	return true;
}

MyRedis::MyRedis(){
	_redis_cnn = NULL;
}
MyRedis::~MyRedis(){
	if (_redis_cnn){
		redisFree(_redis_cnn);
		_redis_cnn = NULL;
	}
	pthread_mutex_destroy(&mutex_locker_);
}
bool MyRedis::reConnect(){
	cerr<<"Connecting MyRedis"<<endl;
	if (_redis_cnn){
		redisFree(_redis_cnn);
		_redis_cnn = NULL;
	}
	_redis_cnn = redisConnect(_ip.c_str(), _port);
	if (_redis_cnn==NULL){
		cerr<<"[ERROR]:Redis Connect return NULL"<<endl;
		return false;
	}
	if (_redis_cnn->err){
		cerr<<"[ERROR]:Redis Connect failed [" << _redis_cnn->err << "] [" << _redis_cnn->errstr << "]"<<endl;
		redisFree(_redis_cnn);
		return false;
	}
	return true;
}
bool MyRedis::init(const std::string& addr){
	pthread_mutex_init(&mutex_locker_,NULL);
	int pos;
	if ((pos=addr.find(":"))==std::string::npos){
		cerr<<"[ERROR]:MyRedis::init() error addr->"<<addr<<endl;
		return false;
	}
    cout << addr << endl;
    cout << pos << endl;
	_ip = addr.substr(0,pos);
	_port = atoi(addr.substr(pos+1).c_str());
	return reConnect();
}

