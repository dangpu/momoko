#ifndef QUERY_CORE_SERVER_CONFIGURATION_HPP
#define QUERY_CORE_SERVER_CONFIGURATION_HPP

#include <vector>
#include <netinet/in.h>
#include <string>

class Configuration {
	public:
		int open(const char *filename, const char *key);
		static std::string readString(char const * filename, char const * path, char const * name);

	protected:
		int readParameter(const char *filename, const char * key);
		int readThreadNumber(const char *filename, const char * key);
		int SeparateIP(const char *value,char * ip,int * port);
    		int readDataPath(const char *data_path, const char * key);
	public:
		unsigned int listen_port;
		unsigned int thread_stack_size;

		unsigned int receiver_num;
		unsigned int processor_num;

		int commandlengthwarning; //qo 的result结果长度最长为4k 因为此处是人工编辑 所以限定最大长度 否则可能被丢弃结果
		std::string data_path;
};

#endif /* QUERY_CORE_SERVER_CONFIGURATION_HPP */

