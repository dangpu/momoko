#include "http_server.hpp"
#include "query_processor.hpp"
#include "configuration.hpp"
#include <malloc.h>
#include <signal.h>
#include "service_log.hpp"
#define DEFAULT_CONFIG_KEYNAME          "SERVER"

//#define WRITE_CERR_LOG_INTO_FILE

void sigterm_handler(int signo) {}
void sigint_handler(int signo) {}

int main(int argc, char* argv[])
{
	mallopt(M_MMAP_THRESHOLD, 64*1024);
	const char *config_filename = argv[1];
	const char *config_keyname = DEFAULT_CONFIG_KEYNAME;
	if(argc>=3) config_keyname = argv[2];	

	close(STDIN_FILENO);
	signal(SIGPIPE, SIG_IGN);
	signal(SIGTERM, &sigterm_handler);
	signal(SIGINT, &sigint_handler);

	_INFO("[Server starting...] ");
	{
		int ret;
		Configuration config;
		if (config.open(config_filename, config_keyname))
		{
			_ERROR("open configure file and key name < %s : %s >error",config_filename,config_keyname);
			return -1;
		}

		Http_Server htp;

		Query_Processor processor;

		pthread_barrier_t processor_init;
		pthread_barrier_init(&processor_init, NULL, config.processor_num + 1);

		processor.register_httpserver(&htp);
		htp.register_processor(&processor);

		if((ret = processor.open(config.processor_num,config.thread_stack_size,&processor_init,config.data_path)) < 0)
		{
			_ERROR("open processor error! ret:%d,thread:%d",ret,config.processor_num);
			exit(-1);
		}
		if((ret = htp.open(config.receiver_num,config.thread_stack_size,config.listen_port)) <0 )
		{
			_ERROR("open http server error! ret:%d,thread:%d,listen port:%d",ret,config.receiver_num,config.listen_port);
			exit(-1);	
		}

		_INFO("Server initialized OK");
		processor.activate();
		pthread_barrier_wait(&processor_init);	// wait for all processors fully initialized
		//WEBSEARCH_DEBUG((LM_DEBUG,"processor activate\n"));
		sleep(1);
		htp.activate();
		//WEBSEARCH_DEBUG((LM_DEBUG,"http activate\n"));
		_INFO("[Server started]");

		pause();
		htp.stop();
		processor.stop();
		pthread_barrier_destroy(&processor_init);
	}
	_INFO("[Server stop]");

#ifdef WRITE_CERR_LOG_INTO_FILE
	file.close();
#endif
	return 0;
}

