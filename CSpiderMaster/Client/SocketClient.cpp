#include "SocketClient.h"
//#include "define.h"
#include "CommonFuc.h"
#include <time.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <arpa/inet.h>

using namespace std;
using namespace COMMON;



typedef unsigned char BYTE;

const static int MAX_NUM = 1024*10;
const static int MAXSTRLEN = 1024;
const static int max_buf_len = 64*1024;
#define SEG_BUF 50


bool SocketClient::init(const std::string& addr,const long& timeout){
	int pos = addr.find(":");
	if (pos==string::npos)
		return false;
	m_ip = addr.substr(0,pos);
	m_port = Transfer<string,int>::convert(addr.substr(pos+1));
	m_timeout = timeout;
}

int SocketClient::read_timeout(int fd, char* buf ,int len, timeval *timeout) 
{
    fd_set wset;
    FD_ZERO(&wset);
    FD_SET(fd, &wset);
    if (select(fd + 1, &wset, NULL, NULL, timeout) <= 0) {
        return -1;
    }
    return read(fd, buf, len);
}


int SocketClient::readn_timeout(int fd, char* content, int need_to_read, timeval *timeout)
{
    char buf[SEG_BUF + 1];
    int n, left;
    int len;
    int ptr = 0;
    left = need_to_read;
    while (left > 0) {
        len = left > SEG_BUF ? SEG_BUF : left;
        n = read_timeout(fd, buf, len, timeout);
        if (n <= 0 ) {
            return need_to_read - left;
        }
        buf[n] = '\0';
        memcpy(content + ptr, buf, len);
        ptr = ptr + n;
        left = left - n;
    }
    return 0;
    //return need_to_read - left;
}

int SocketClient::read_http_header_timeout_zy(int fd, string& header, string& content, timeval *timeout)
{
    char buf[SEG_BUF + 1];
    string pkg = "";
    while(1)
    {
        int ret = read_timeout(fd, buf, SEG_BUF, timeout);
        if(ret > 0)
        {
            buf[ret] = '\0';
            pkg += buf;
            //printf("zy: %s\n", pkg.c_str());
        }
        else if(ret < 0)
            return -1;
        else
            break;
    }
    content = pkg.substr(pkg.find("\r\n\r\n")+4);
    printf("content: %s\n", content.c_str());
    return 0;
}


int SocketClient::read_http_header_timeout(int fd, string& header, char* content, timeval *timeout) 
{
    char buf[SEG_BUF + 1];
    int n, pos;
    string pkg="";
    while (1) {
        pos = pkg.find("\r\n\r\n");
        if (pos != string::npos) {
            header = pkg.substr(0, pos);
            printf("[n:%d pos:%d]\n",n,pos);
            memcpy(content, buf + (pos + 4) % SEG_BUF, n - (pos + 4) % SEG_BUF);
            return n - (pos + 4) % SEG_BUF;
        }
        n = read_timeout(fd, buf, SEG_BUF, timeout);
        if (n <= 0) {
            return -1;
        }
        buf[n] = '\0';
        pkg += buf;
        printf("zy: pkg:%s\n", pkg.c_str());
    }
    //buf[n] = '\0';
    return -1;
}


int SocketClient::recv_result_zy(string& result, int& len, int fd, long time_out_us)
{
    //int max_buf_len = len;
    int ret;
    len = 0;
    struct timeval timeout = {0, time_out_us};
    string header;
    ret = read_http_header_timeout_zy(fd, header, result, &timeout);
    printf("result: %s\n", result.c_str());
    return ret;
}

int SocketClient::recv_result(char* result, int& len, int fd, long time_out_us)
{
    //int max_buf_len = len;
    int ret;
    len = 0;
    struct timeval timeout = {0, time_out_us};
    string header;
    ret = read_http_header_timeout(fd, header, result, &timeout);
    if (ret < 0) {
        return -1;
    }
    fprintf(stderr,"head:\n%s\n",header.c_str());
    int idx = header.find("Content-Length:");
    if (idx == string::npos) {
        return -2;
    }
    int sep_index = header.find("\r\n", idx);
    int body_len = atoi(header.substr(idx + strlen("Content-Length:"), sep_index - idx - strlen("Content-Length:")).c_str());
    int need_to_read = body_len - ret;
    ret = readn_timeout(fd, result + ret, need_to_read, &timeout);
    if (ret != 0) {
        return -3;
    }
    len = body_len;
    return 0;

}

bool SocketClient::string_split(const string& str, const string& pattern, vector<string>& v)
{
    v.clear();
    size_t bpos = 0;
    
    while(str.find(pattern, bpos) != std::string::npos)
    {
        size_t epos = str.find(pattern, bpos);
        if(epos == 0)
        {
            bpos = epos + pattern.size();
            continue;
        }
        v.push_back(str.substr(bpos, epos - bpos));
        bpos = epos + pattern.size();
        if(bpos >= str.size())
            break;
    }
    
    if(bpos < str.size())
        v.push_back(str.substr(bpos, str.size() - bpos));
    return true;
}
//bool SocketClient::getRstFromHost(const string& query, const string& ip, const int& port, ServerRst& sr,long time_out_us,int type,const string& hostname)
bool SocketClient::getRstFromHost(const std::string& query,ServerRst& sr,unsigned short type)
{
    int sock;
    struct sockaddr_in server;
    struct hostent *hp;
    sock = socket(AF_INET, SOCK_STREAM, 0);
    cout<<"Sock id:"<<sock<<endl;
    if (sock < 0) {
        perror("opening stream socket");
        return  false;
    }
    server.sin_family = AF_INET;
    
    //DNS缓存 CACHE查询
	if(m_dns_cache!=0){
		cerr<<"DNS Cached"<<endl;
		server.sin_addr.s_addr = m_dns_cache;
	}else{
        struct hostent *pHost,host;
        memset(&host,0, sizeof(hostent));
        int tmp_errno=0;
        char host_buff[2048];
        memset(host_buff,0, sizeof(host_buff));
		if (gethostbyname_r(m_ip.c_str(),
					&host, host_buff, sizeof(host_buff),
					&pHost, &tmp_errno)) {
			cerr<<"get host Fail!!!"<<endl;
			return false;
		} else {
			if (pHost && AF_INET == pHost->h_addrtype) {
				memcpy(&server.sin_addr, pHost->h_addr_list[0], sizeof(server.sin_addr));
				//cerr<<"HOST:["<<m_ip<<"]"<<endl;
				//cerr<<"IP:["<<inet_ntoa(server.sin_addr)<<"]"<<endl;
				//Cache录入
				m_dns_cache = server.sin_addr.s_addr;
			} else {
				cerr<<"host create Fail!!!"<<endl;
				return false;
			}
		}
	}
    
    
    server.sin_port = htons(m_port);
    int ret;

    unsigned long ul = 1;
    ioctl(sock, FIONBIO, &ul);//设置为非阻塞模式
	fd_set fdset;
	bool bSucc = false;
	struct timeval tm = {0, m_timeout};
    int nErr = -1;

    if ((ret = connect(sock, (struct sockaddr*)&server, sizeof(server))) < 0) {
        //设置连接超时
        FD_ZERO(&fdset);
        FD_SET(sock, &fdset);
        if (select(sock+1, NULL, &fdset, NULL, &tm) > 0)
			bSucc = true;
	    else{
			bSucc = false;
		}
    }
	else{
		bSucc = true;
	}

     ul = 0;
     ioctl(sock, FIONBIO, &ul);//设置为阻塞模式
     if (!bSucc)
     {
               close(sock);
               cerr<<"ERROR:connecting stream socket"<<endl;
               fprintf(stderr,"err:%d(%s),ret:%d\n",errno,strerror(errno),ret);
               fprintf(stderr,"EINPROGRESS:%d, EALREADY:%d\n",EINPROGRESS,EALREADY);
               return false;
     }

    //if(_SHOW_DEBUG_%10==1 && _SHOW_DEBUG_/10==1){
	//	printf("connected ok sock:%d\n",sock);
	//}

    ostringstream oss_qlen;
    oss_qlen << query.size();

	string use_host = "default";
	string sendmsg_str;
	if (type==0){
        sendmsg_str = (string)"GET /" + query + " HTTP/1.1\r\n"+
				(string)"Accept: */*\r\n" +
    	        (string)"Accept-Language: zh-cn\r\n" +
				(string)"Host: " + use_host + "\r\n"+
				(string)"Content-Length: "+ oss_qlen.str() + (string)" \r\n"+ 
				(string)"Content-Type: application/x-www-form-urlencoded;charset=utf-8\r\n\r\n";
	}else if (type==2){
        sendmsg_str = (string)"GET /" + query + " HTTP/1.1\r\n"+
				(string)"Accept: */*\r\n" +
    	        (string)"Accept-Language: zh-cn\r\n" +
				(string)"Host: " + use_host + "\r\n"+
				(string)"Content-Type: application/x-www-form-urlencoded;charset=gbk\r\n\r\n";
	}
	else if (type==1){
        sendmsg_str = (string)"POST /" + "servermanager" + " HTTP/1.1\r\n"+
            (string)"Accept: */*\r\n" +
            (string)"Accept-Language: zh-cn\r\n" +
            (string)"Host: " + use_host + "\r\n"+
            (string)"Content-Type: application/x-www-form-urlencoded;charset=gbk\r\n"+
        	(string)"Content-Length: "+ oss_qlen.str() + (string)" \r\n\r\n"+ query;
	}

   cerr<<"[Socket Send]:"<<sendmsg_str<<"\r\n[--Socket Send--]"<<endl;
    
    if (send(sock, sendmsg_str.c_str(), sendmsg_str.size(), 0) < 0)
    {
        perror("sending on stream socket");
        fprintf(stderr,"err:%d(%s)",errno,strerror(errno));
        close(sock);
        return false;
    }

    //char rcvbuf[max_buf_len];
    //memset(rcvbuf, 0, max_buf_len);
    int buf_len=max_buf_len;
    //string header;
    //struct timeval timeout = {0, m_timeout};
    //int rt = read_http_header_timeout(sock, header, rcvbuf, &timeout);
    
    string res_zy;
    int rt = recv_result_zy(res_zy, buf_len, sock,m_timeout);
    //printf("rcvbuf: %s\n", rcvbuf);
    if(rt != 0)
    {
    	cerr<<"Return Error:"<<rt<<endl;
        fprintf(stderr, "[receive nothing, return]\n");
        close(sock);
        return false;
    }
    
    //int total_len = strlen(rcvbuf);
    //fprintf(stderr, "[receive number size = %d]\n", total_len);

    //string rcvstr = rcvbuf;
    
    //sr.ret_str=rcvstr;


    sr.ret_str = res_zy;
    close(sock);
    return true;
}


