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

		int commandlengthwarning; //qo ��result��������Ϊ4k ��Ϊ�˴����˹��༭ �����޶���󳤶� ������ܱ��������
		std::string data_path;
};

#endif /* QUERY_CORE_SERVER_CONFIGURATION_HPP */

