#ifndef QO_MANAGER_HPP
#define QO_MANAGER_HPP

#include "task_base.hpp"
#include "worker.hpp"
#include "wait_list.hpp"
#include <iconv.h>
#include <pthread.h>
#include <vector>
#include <map>
#include "json/json.h"
#include "../validation/validation.hpp"

class Http_Server;

class Query_Processor : public task_base
{
public:
	Query_Processor();
	~Query_Processor();

	void register_httpserver(Http_Server * server);
	int submit_worker(Http_Server * formwho, Worker*& worker);

	int open(size_t thread_num, size_t stack_size, pthread_barrier_t *processor_init,const std::string& data_path);
	int stop();	
	int svc();

protected:
	int url_utf8_decode(const char *url, const int url_len, char * dec, const int max_len);
	std::string url_encode(const std::string& input, const std::string& wsplacer);
	int char2num(char ch);
	char unhex(unsigned char c);
	int utf82gbk( char * in, int * inlen,char * out, int * outlen);
	int gbk2utf8( char * in, int * inlen,char * out, int * outlen);
	int parse_content(const char * key,const std::string &request,char * key_result,const int max_len);
	int parse_worker(Worker * worker);
    std::string get_param(const char * key, const std::string& request);
    int get_param_int(const char * key, const std::string& request);

protected:
	Http_Server *m_httpserver;
	Query_Processor *m_processor;	
	wait_list_t<Worker, &Worker::task_list_node>  m_task_list;
	pthread_barrier_t *processor_init;

    Validation* m_validation;
};

#endif /* QUERY_CORE_SERVER_MANAGER_HPP */


