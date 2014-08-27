#ifndef __SOGOU_CLIENT_H_
#define __SOGOU_CLIENT_H_

//#include "QuestionAnswer.h"
//#include "NLPTools_Number.h"
//#include "QuestionClassify.h"
//
#include <stddef.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>
#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <ctype.h> 
//#include <boost/algorithm/string.hpp>
#include <sstream>
//#include "Platform/encoding/EncodingConvertor.h"
#include <pthread.h>
//#include "Cache.h"


class ServerInfo{
	public:
	std::string ip;
	int port;
};

class ServerRst
{
	public:
		int ret_num;
		std::string ret_str;

	public:
		ServerRst()
		{
			ret_num = 0;
			ret_str = "";
		};
		~ServerRst(){};
};

class SocketClient
{
	public:
		SocketClient(){m_dns_cache=0;};
		~SocketClient(){};
		bool init(const std::string& addr,const long& timeout);
		
	private:
		int read_timeout(int fd, char* buf ,int len, timeval *timeout);
		int readn_timeout(int fd, char* content, int need_to_read, timeval *timeout);
		int read_http_header_timeout(int fd, std::string& header, char* content, timeval *timeout);
		int read_http_header_timeout_zy(int fd, std::string& header, char* content, timeval *timeout);
		int recv_result(char* result, int& len, int fd,long time_out_us);
		int recv_result_zy(char* result, int& len, int fd,long time_out_us);
		bool string_split(const std::string& str, const std::string& pattern, std::vector<std::string>& v);

	public:
		std::string m_ip;
		int m_port;
		long m_timeout;
		unsigned int m_dns_cache;

		bool getRstFromHost(const std::string& query,ServerRst& sr,unsigned short type=0);
};

#endif
