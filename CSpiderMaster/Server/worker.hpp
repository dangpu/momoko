#ifndef  QO_WORKER_HPP
#define  QO_WORKER_HPP

#include "string"
#include "socket_handle.hpp"
#include "linked_list.hpp"

#include "json/json.h"

#define MAX_HTTP_CONTENT_LENGTH   2048

class Worker
{
	public:
		Worker()
		{
			handle = NULL;
			result_len = -1;
			query_len = -1;
			result = NULL;
			querystring = NULL;
		}
		virtual ~Worker()
		{
			if (result)
			{
				free(result);
				result = NULL;
			}
			if (querystring)
			{
				free(querystring);
				querystring = NULL;
			}
		}

		void * GetMem(size_t size)
		{
			return malloc(size);
		}
		void FreeMem(void * mem)
		{
			free(mem);
			mem = NULL;
		}

	public:
		timeval receive_time;
		std::string  uri;
		int query_len;
		char * querystring;
		
		char *  result;
		int result_len;

		Json::Value jv_parameter;

		SocketHandle * handle;	

		linked_list_node_t task_list_node;
};

#endif //QO_WORKER_HPP

