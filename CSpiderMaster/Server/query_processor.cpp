#include "http_server.hpp"
#include "query_processor.hpp"
#include "service_log.hpp"
#include <cstring>
#include <ctype.h>
#include <time.h>
#include <sys/time.h>
#include <errno.h>
#include <algorithm>
#include "json/json.h"

pthread_mutex_t gMutex=PTHREAD_MUTEX_INITIALIZER;
#define MAX_HTTP_CONTENT_LENGTH 20480
using namespace std;

Query_Processor::Query_Processor()
{
    //m_pRoute = NULL;
}

Query_Processor::~Query_Processor()
{
	//if (m_pRoute)
	//{
	//	delete m_pRoute;
	//	m_pRoute = NULL;
	//}
	pthread_mutex_destroy(&gMutex);
}

void Query_Processor::register_httpserver(Http_Server * server)
{
	m_httpserver = server;
}

int Query_Processor::submit_worker(Http_Server * formwho, Worker * &worker)
{
	m_task_list.put(*worker);
	worker = NULL;
	return 0;       
}

int Query_Processor::open(size_t thread_num, size_t stack_size, pthread_barrier_t *processor_init,const std::string& data_path)
{
	this->processor_init = processor_init;

	//Chat Server data initial
	//if (NULL == m_pRoute)
	//	m_pRoute = new Route;

	//if (NULL == m_pRoute)
	//	return false;

	//if (!m_pRoute->init(data_path))
	//{
	//	cerr<<"[Error]:m_pRoute->Init()!!"<<endl;
	//	return -1;
	//}

	m_master = Master::getInstance();
	m_workload = WorkloadMaster::getInstance();

	/*
	   if(!m_workload->connectDB("114.215.168.168", "workload", "root", "miaoji@2014!"))
	   {
	   _ERROR("[can't connect to mysql!]");
	   }
	   */
	return task_base::open(thread_num, stack_size);
}

int Query_Processor::stop()
{
	m_task_list.flush();
	join();
	_INFO("query process stop");
	return 0;
}

std::string Query_Processor::url_encode(const std::string& input,const std::string& wsplacer)
{
	std::string conv_words = "";
	const unsigned char* c = (const unsigned char*)input.c_str();
	for (size_t j = 0; j < input.size(); ++j)
	{
		if (c[j] == ' ')
		{
			conv_words += wsplacer;
			continue;
		}
		if (c[j] == '-' || c[j] == '.' || c[j] == '!' || c[j] == '~' || c[j] == '*' || c[j] == '\'' || c[j] == '(' || c[j] == ')' || (c[j] >= '0' && c[j] <= '9') || (c[j] >= 'a' && c[j] <= 'z') || (c[j] >= 'A' && c[j] <= 'Z'))
		{
			conv_words += c[j];
			continue;
		}
		char s[8] = {0};
		snprintf(s, 8, "%%%.2X", c[j]);
		s[7] = 0;
		conv_words += s;
	}  
	return conv_words;
}

int Query_Processor::char2num(char ch)
{
	if (ch >= '0' && ch <= '9')
		return(ch - '0');

	if (ch >= 'a' && ch <= 'f')
		return(ch- 'a' + 10);

	if (ch >= 'A' && ch <= 'F')
		return(ch- 'A' + 10);

	return -1;
}

int Query_Processor::gbk2utf8(char * in, int * inlen,char * out, int * outlen)
{
	char * outbuf = out;
	char * inbuf = in;
	size_t outlenbuf = *outlen;
	size_t inlenbuf = *inlen;
	//iconv_t m_gbk2utf16_ = iconv_open("utf-8//IGNORE", "gbk//IGNORE");
	iconv_t m_gbk2utf8_ = iconv_open("utf-8//IGNORE", "GB18030//IGNORE");
	size_t ret = iconv(m_gbk2utf8_, &inbuf, &inlenbuf, &outbuf, &outlenbuf);
	iconv_close(m_gbk2utf8_);

	if (ret == size_t(-1) && errno == EILSEQ)
	{
		*outlen = outbuf - out;
		*inlen = inbuf - in;
		return -2;
	}
	else
	{
		*outlen = outbuf - out;
		*inlen = inbuf - in;
		if (ret == size_t(-1) && errno == E2BIG)
			return -1;
		else
			return *outlen;
	}			       
}

int Query_Processor::utf82gbk( char * in, int * inlen,char * out, int * outlen)
{
	if ((out == NULL) || (outlen == NULL) || (inlen == NULL))
		return -1;
	if (in == NULL)
	{
		*outlen = 0; 
		*inlen = 0; 
		return 0;
	}

	char * outbuf = (char *)out;
	char * inbuf = (char *)in;
	size_t outlenbuf = *outlen;
	size_t inlenbuf = *inlen;
	//      iconv_t m_utf162gbk_ = iconv_open("gbk//IGNORE", "gbk//IGNORE");
	iconv_t m_utf82gbk_ = iconv_open("GB18030//IGNORE", "utf-8//IGNORE");
	size_t ret = iconv(m_utf82gbk_, &inbuf, &inlenbuf, &outbuf, &outlenbuf);
	iconv_close(m_utf82gbk_ );

	if (ret == size_t(-1) && errno == EILSEQ)
	{
		*outlen = outbuf - out;
		*inlen = inbuf - in;
		_ERROR("utf82gbk error(-2),input:%s,inlen:%d",in,*inlen);
		return -2;
	}
	else
	{
		*outlen = outbuf - out;
		*inlen = inbuf - in;
		if (ret == size_t(-1) && errno == E2BIG)
		{
			_ERROR("utf82gbk error(-1),input:%s,inlen:%d",in,*inlen);
			return -1;
		}
		else if (ret == size_t(-1))
		{
			_ERROR("utf82gbk error(-3),input:%s,inlen:%d",in,*inlen);
			return -3;
		}
		else
			return *outlen;
	}
}

char Query_Processor::unhex(unsigned char c)
{
	if (c < '@')
		return c - '0';
	return(c & 0x0f) + 9;
}

int Query_Processor::url_utf8_decode(const char *url, const int url_len, char * dec, const int max_len)
{
	//_INFO("The url is: %s\n" , url);
	//_INFO("The url_len is: %d\n" , url_len);

	//_INFO("The dec is: %s\n" , dec);

	//_INFO("The max_len is: %d\n", max_len);

	const char* url_end = url+url_len;
	const char* dst_end = dec+max_len-1;
	char * dst_uri = dec;
	//_INFO("ori query: %s\n" , url);
	while ( url < url_end && dst_uri < dst_end)
	{
		// 以%开始的串转化为二进制
		if (url[0] == '%' && url + 2 <= url_end && isxdigit(url[1]) && isxdigit(url[2]))
		{
			*dst_uri = (unhex(url[1]) << 4) | unhex(url[2]);
			url += 3;
		}
		// 其它直接拷贝
		else if (url[0] == '+')
		{
			*dst_uri = ' ';
			url++;
		}
		else
		{
			*dst_uri = *url;
			url++;
		}
		dst_uri++;
	}
	*dst_uri = 0;
	int dst_len = dst_uri - dec;
	//int dec_len = max_len;

	//_INFO("The dst is : ");
	//for(int i=0;i<dst_len;i++){
	//      _INFO("%d",dst[i]);
	//}    
	//_INFO("The dst is End\n");
	//_INFO("ori query: %s\n %d\n" , dst,dst_len);
	//_INFO("The dst_len is %d\n" , dst_len);
	//int utf_len = utf82gbk(dst,&dst_len,dec,&dec_len);
	//delete [] dst;
	return dst_len;
}

int Query_Processor::parse_content(const char * key,const std::string &request,char * key_result,const int max_len)
{
	//memset(key_result,0,max_len);
	int key_start = request.find(key);
	//_INFO("The pos of %s is %d \n", key, key_start);
	if (key_start < 0 )
	{
		//_ERROR("can't find the key symbol (%s)\n",key);
		return -1;
	}
	key_start += strlen(key);
	int key_end;
	if ((key_end= request.find("?",key_start)) <0 && (key_end= request.find("&",key_start)) <0 && (key_end = request.find("\r\n")) <0 && (key_end = request.find("\n")) <0 && (key_end = request.find("\r")) <0)
	{
		key_end = request.length();
	}
	int key_len = key_end - key_start;      

	return url_utf8_decode(request.c_str()+key_start,key_len,key_result,max_len);
}

int Query_Processor::parse_worker(Worker * worker)
{
	worker->querystring = (char*)worker->GetMem(MAX_HTTP_CONTENT_LENGTH);
	if (NULL == worker->querystring)
		return -1;

	worker->query_len = parse_content("/", worker->uri, worker->querystring, MAX_HTTP_CONTENT_LENGTH );

	//_INFO("In parse worker :%s\n" , worker->querystring);
	if (worker->query_len<=0 || worker->query_len >=MAX_HTTP_CONTENT_LENGTH)
	{
		_ERROR("In parse worker parse queryString error, querylen:%d(info:uri:%s)",worker->query_len,worker->uri.c_str());
		worker->FreeMem(worker->querystring);
		worker->query_len = -1;
		worker->querystring = NULL;
		return -1;
	}
	worker->querystring[worker->query_len] = 0;
	_INFO("Recv Query:%s" , worker->querystring);
	return 0;
}

string Query_Processor::get_param(const char * key, const std::string& request)
{
	int max_len = 614400;
	char* res = new char[max_len];
	int len = parse_content(key, request, res, max_len);
	if(len < 0 || len > max_len)
	{
		delete res;
		return "";
	}
	std::string res_str = res;
	delete res;
	return res_str;
}

int Query_Processor::get_param_int(const char * key, const std::string& request)
{
	std::string res_str = get_param(key, request);
	if(res_str != "")
	{
		return atoi(res_str.c_str());
	}
	return 0;
}


int Query_Processor::svc()
{
	Worker * worker;
	int ret,cached;
	//char * result = new char [MAX_HTTP_CONTENT_LENGTH];
	//ScribeProxyClient *client=NULL;
	std::vector<std::string> category;
	int queueLen = 0;
	cerr<<"initialized thread..."<<endl;

	pthread_barrier_wait(processor_init);

	while ((worker = m_task_list.get()) != NULL)
	{
		queueLen = m_task_list.len();

		ret = parse_worker(worker);
		if(ret >= 0)
		{
			// TODO: process the request and fill the result in result
			//snprintf(result, MAX_HTTP_CONTENT_LENGTH, "<h1>Hello world!</h1>Query string: %s", worker->querystring);
			ret = 0;
			//clock_t start=clock();

			//Chat Server 
			string szOrigInput = worker->querystring;
			/*
			   if (0 != pthread_mutex_lock(&gMutex))//加锁
			   {
			   cerr<<"[ERROR]::Thread lock failed!!"<<endl;
			   exit(-1);
			   }*/

			//Json::Reader jr;
			//Json::FastWriter jw;
			//Json::Value req,resp;
			//jr.parse(worker->querystring,req);

			//if (!m_pRoute->doRoute(req, resp))
			//{
			//	cerr<<"ERROR::m_pRoute->doRoute()!!!"<<endl;
			//pthread_mutex_unlock(&gMutex);
			//	m_httpserver->retrieve_worker(worker);
			//	continue;
			//}

			string res = "";
            //usleep(300000);

			if(szOrigInput == "register_slave")
			{
				std::string name = get_param("name=", worker->uri);
				std::string server = get_param("server=", worker->uri);
				std::string path = get_param("path=", worker->uri);
				std::string server_ip = get_param("server_ip=", worker->uri);
				std::string type = get_param("type=", worker->uri);
				std::string recv_realtime_req_str = get_param("recv_real_time_request=", worker->uri);
				bool recv_realtime_req = (recv_realtime_req_str == "True")?true:false;
				res = m_master->registerSlave(name, server, path, server_ip, type, recv_realtime_req);
			}
			else if(szOrigInput == "heartbeat")
			{
				std::string id = get_param("id=", worker->uri);
				int thread_num = get_param_int("thread_num=", worker->uri);
				int process_task_num = get_param_int("process_task_num=", worker->uri);
				int error_task_num = get_param_int("errror_task_num=", worker->uri);
				int request_task_num = get_param_int("request_task_num=", worker->uri);
				m_master->heartbeat(id, thread_num, process_task_num, error_task_num, request_task_num);
            }
			else if(szOrigInput == "workload")
			{
				string source = get_param("source=", worker->uri);
				int count = get_param_int("count=", worker->uri);
				res = m_workload->assignTask(source, count);
			}
			else if(szOrigInput == "complete_workload")
			{
				string task_str = get_param("q=", worker->uri);
				//_INFO("[TASK %s begin!]", task_str);
				m_workload->completeTask(task_str);
			}
			else if(szOrigInput == "updateTasks")
			{
				m_workload->updateWorkload();
				_INFO("[task size is : %d]", m_workload->m_tasks.size());
            }

			//clock_t end = clock();
			//double dbWaste = 1.0f*(end-start);
			//cerr<<"Total wasted time:"<<dbWaste<<"us"<<endl;

			// copy the result into worker
			int max_len = 65536000;
			worker->result = (char*)worker->GetMem(max_len);
			if (worker->result == NULL)
			{
				pthread_mutex_unlock(&gMutex);//解锁
				m_httpserver->retrieve_worker(worker);
				continue;
			}
			if("" != res)
			{
				//int max_len = MAX_HTTP_CONTENT_LENGTH;
				worker->result_len = std::min(res.length(), size_t(max_len) - 1) + 1;
				memcpy(worker->result, res.c_str(), worker->result_len);
				worker->result[worker->result_len] = 0;
				_INFO("[ Result: %s]", worker->result);
			}
			//worker->result_len -= 1;
			//fprintf(stderr,"[realresult]:%s\n", worker->result);
			//cerr<<"write_rst_WASTED_TIME:"<<(clock()-end)<<"us"<<endl;

			//pthread_mutex_unlock(&gMutex);//解锁
		}//if

		int retlen = (ret==-1)?-1:worker->result_len;
		const char * queryStr = (worker->query_len<=0)?"NULL":worker->querystring;
		_INFO("[Observer,cost=%d,ret=%d,querystring=%s,Owner=OP]",WASTE_TIME_US(worker->receive_time),retlen,queryStr);

		m_httpserver->retrieve_worker(worker);
	}//while

	cerr<<"closed thread!!"<<endl;
	//delete [] result;

	return 0;
}

