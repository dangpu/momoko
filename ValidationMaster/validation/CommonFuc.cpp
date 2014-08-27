
#include "CommonFuc.h"
#include <sstream>
#include <string>
#include <string.h>
#include <vector>
#include <iostream>
#include <iconv.h>


using namespace std;

namespace COMMON
{
	

pthread_mutex_t MYLog::_locker = PTHREAD_MUTEX_INITIALIZER;
time_t MYLog::_time = 0;
ofstream MYLog::_file;
std::string MYLog::_dir = ".";
	
void MYLog::init(const std::string& dir){
	time_t t;
	time(&t);
	string time_str = MYTime::toString(t,8);
	_dir = dir;
	if (_dir[_dir.length()-1]=='/')
		_dir = _dir.substr(0,_dir.length()-1);
	_time = MYTime::toTime(time_str,8);
	_file.open((_dir+"/"+time_str.substr(0,11)+".txt").c_str(),ios::app|ios::out);
	cerr<<_dir+"/"+time_str.substr(0,11)+".txt"<<endl;
	if (!_file){
		cerr<<"Log file open failed!"<<endl;
		exit(0);
	}
	return;
}
void MYLog::write(const std::string& log){
	pthread_mutex_lock(&_locker);
	time_t t;
	time(&t);
	if (t>_time+3599){
		if (_time){
			_file.close();
		}
		_time += 3600*((t-_time)/3600);
		string hour_str = MYTime::toString(_time,8);
		_file.open((_dir+"/"+hour_str+".txt").substr(0,11).c_str(),ios::app|ios::out);
		if (!_file){
			cerr<<"Log file open failed!"<<endl;
			exit(0);
		}
	}
	_file<<"["<<MYTime::toString(t,8,"%Y%m%d_%H:%M:%S")<<"]"<<log<<std::endl;
	pthread_mutex_unlock(&_locker);
	return;
}
void MYLog::write(const int& log){
	pthread_mutex_lock(&_locker);
	time_t t;
	time(&t);
	if (t>_time+3599){
		if (_time){
			_file.close();
		}
		_time += 3600*((t-_time)/3600);
		string hour_str = MYTime::toString(_time,8);
		_file.open((_dir+"/"+hour_str+".txt").substr(0,11).c_str(),ios::app|ios::out);
		if (!_file){
			cerr<<"Log file open failed!"<<endl;
			exit(0);
		}
	}
	
	_file<<"["<<MYTime::toString(t,8,"%Y%m%d_%H:%M:%S")<<"]"<<log<<std::endl;
	pthread_mutex_unlock(&_locker);
	return;
}
	


std::vector<std::string> toCharactor(const std::string& in){
	std::vector<std::string> v;
	for(size_t i=0;i<in.length();){
		if((in[i] & 0x80) == 0x00){
			v.push_back(in.substr(i++,1));
		}else if((in[i] & 0xE0) == 0xC0){
			v.push_back(in.substr(i,2));
			i+=2;
		}else if((in[i] & 0xF0) == 0xE0){
			v.push_back(in.substr(i,3));
			i+=3;
		}else{
			v.clear();
			return v;
		}
	}
	return v;
}

std::vector<std::string> sepString(std::string input, const std::string& sep)
{
	std::vector<std::string> output;
	while(input.length()) {
	int pos = input.find(sep);
		if(pos >= 0) {
			output.push_back(input.substr(0, pos));
			input = input.substr(pos + sep.length());
			if (input.length()==0)
				output.push_back("");
		} else {
			output.push_back(input);
			break;
		}
	}
	return output;
}

void sepString(std::string input, const std::string& sep,std::vector<std::string>& output)
{
	while(input.length()) {
	int pos = input.find(sep);
		if(pos >= 0) {
			output.push_back(input.substr(0, pos));
			input = input.substr(pos + sep.length());
			if (input.length()==0)
				output.push_back("");
		} else {
			output.push_back(input);
			break;
		}
	}
	return;
}

//将字符串切割为map
std::map<std::string,std::string> sepString2Map(std::string input, const std::string& item_sep,const std::string& kv_sep){
	std::map<std::string,std::string> ret;
	while(input.length()>0){
		int pos = input.find(item_sep);
		string kv;
		if (pos!=std::string::npos){
			kv = input.substr(0,pos);
			input = input.substr(pos+item_sep.length());
		}else{
			kv = input;
			input = "";
		}
		pos = kv.find(kv_sep);
		if (pos==std::string::npos)
			continue;
		ret[kv.substr(0,pos)] = kv.substr(pos+kv_sep.length());
	}
	return ret;
}



void removeCharsFirstANDLast(std::string& strIn, const std::string& firstChars,const std::string& lastChars)
{
	if (strIn.length()==0)
		return;
	size_t begPos = strIn.find_first_not_of(firstChars);
	size_t endPos = strIn.find_last_not_of(lastChars);
	if (begPos == std::string::npos || endPos == std::string::npos){
		strIn = "";
	}else{
		strIn = strIn.substr(begPos,endPos-begPos+1);
	}
	return;
}

bool replaceString(std::string& ori_str,const std::string& rep_from,const std::string& rep_to)
{
	size_t pos = 0;
	while(true)
	{
		pos = ori_str.find(rep_from,pos);
		if (rep_from.length()==0)
			return false;
		if(pos != std::string::npos)
		{
			ori_str.replace(pos,rep_from.length(),rep_to);
			pos += rep_to.length();
		}
		else
			break;
	}
	return true;
}


std::string Unicode2UTF8(const std::vector<unsigned int>& unicode)
{
	std::string resUTF8 = "";
	unsigned char curChar;
	for(size_t i=0;i<unicode.size();i++){
		if (unicode[i] <0x80){	//0XXXXXXX
			resUTF8.push_back((unsigned char)unicode[i]);
		}else if (unicode[i] < 0x800){	//110XXXXX 10XXXXXX
			curChar = (unsigned char)(((unicode[i])>>6)|0xC0);
			resUTF8.push_back(curChar);
			curChar = (unsigned char)((unicode[i]&0x3F)|0x80);
			resUTF8.push_back(curChar);
		}else if (unicode[i] < 0x10000){	//1110XXXX 10XXXXXX 10XXXXXX
			curChar = (unsigned char)(unicode[i]>>12|0xE0);
			resUTF8.push_back(curChar);
			curChar = (unsigned char)(((unicode[i]>>6)&0x3F)|0x80);
			resUTF8.push_back(curChar);
			curChar = (unsigned char)((unicode[i]&0x3F)|0x80);
			resUTF8.push_back(curChar);
		}
	}
	return resUTF8;
}

std::vector<unsigned int> UTF82Unicode(const std::string& utf8)
{
	std::vector<unsigned int> resUnicode;
	int length = utf8.length();
	for(size_t i=0;i<length;i++){
		if (utf8[i] & 0x80)	//1XXX XXXX
		{
			if ((utf8[i] & 0xE0) == 0xC0){	//110X XXXX
				if (i+1 >= length){
					std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
					return resUnicode;
				}
				resUnicode.push_back((((unsigned int)(utf8[i]&0x1F))<<6)
									|(utf8[++i]&0x3F));
			}
			else if ((utf8[i] & 0xF0) == 0xE0){	//1110 XXXX
				if (i+2 >= length){
					std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
					return resUnicode;
				}
				resUnicode.push_back((((unsigned int)(utf8[i]&0x0F))<<12)
			                        |(((unsigned int)(utf8[++i]&0x3F))<<6)
            			            |(utf8[++i]&0x3F));
			}
			else if ((utf8[i] & 0xF8) == 0xF0){	//1111 0XXX
				if (i+3 >= length){
					std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
					return resUnicode;
				}
				resUnicode.push_back((((unsigned int)(utf8[i]&0x07)) << 18)
                        			| (((unsigned int)(utf8[++i]&0x3F)) << 12)
			                        | (((unsigned int)(utf8[++i]&0x3F)) << 6)
            			            | (utf8[++i]&0x3F));
			}
			else if ((utf8[i] & 0xFC) == 0xF8){	//1111 10XX
				if (i+4 >= length){
					std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
					return resUnicode;
				}
				resUnicode.push_back((((unsigned int)(utf8[i]&0x03)) << 24)
                        			| (((unsigned int)(utf8[++i]&0x3F)) << 18)
			                        | (((unsigned int)(utf8[++i]&0x3F)) << 12)
            		            	| (((unsigned int)(utf8[++i]&0x3F)) << 6)
                    			    | (utf8[++i]&0x3F));
			}
			else if ((utf8[i] & 0xFE) == 0xFC){	//1111 110X
				if (i+5 >= length){
					std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
					return resUnicode;
				}
				resUnicode.push_back((((unsigned int)(utf8[i]&0x01)) << 30)
			                        | (((unsigned int)(utf8[++i]&0x3F)) << 24)
            			            | (((unsigned int)(utf8[++i]&0x3F)) << 18)
                        			| (((unsigned int)(utf8[++i]&0x3F)) << 12)
			                        | (((unsigned int)(utf8[++i]&0x3F)) << 6)
            			            | (utf8[++i]&0x3F));
			}
			else{
				std::cerr<<"[Error::UTF82Unicode()]:"<<utf8<<std::endl;
				return resUnicode;
			}
		}else{	//0XXX XXXX
			resUnicode.push_back((unsigned int)utf8[i]);
		}
	}
	return resUnicode;
}



int getUTF8CharLength(const char curChar){
	if (curChar & 0x80)	//1XXX XXXX
	{
		if ((curChar & 0xE0) == 0xC0)	//110X XXXX
			return 2;
		else if ((curChar & 0xF0) == 0xE0)	//1110 XXXX
			return 3;
		else if ((curChar & 0xF8) == 0xF0)	//1111 0XXX
			return 4;
		else if ((curChar & 0xFC) == 0xF8)	//1111 10XX
			return 5;
		else if ((curChar & 0xFE) == 0xFC)	//1111 110X
			return 6;
		else{
			return 1;
		}
	}
	else	//0XXX XXXX
		return 1;
}

std::vector<std::string> extractAlphaNumberString(const std::string& in){
	std::vector<std::string> res;
	std::string curStr = "";
	for(size_t i=0;i<in.length();i++){
		bool isfind = false;
		while (i<in.length() && (('A' <= in[i] && in[i] <= 'Z') || ('a' <= in[i] && in[i] <= 'z') || ('0' <= in[i] && in[i] <= '9')
			|| in[i] == '#' || in[i] == '*')){
				isfind = true;
				curStr += in[i++];
		}
		if(isfind){
			res.push_back(curStr);
			curStr = "";
		}
	}
	return res;
}

std::string Half2Full4GBK(const char *src)
{
	char dest[strlen(src) * 2+1];
	int  k = 0 ; 
	for (int i = 0; src[i] != '\0'; i++) {
		//assert(src[i] >= 32);//小于32的ACIIA都是控制符，暂不处理此类情况
		if (src[i] == 32)//半角空格
		{
			dest[k++]   = (char)0xA1; 
			dest[k++] = (char)0xA1;
		}
		else if ((unsigned char)src[i] <= 127 && (unsigned char)src[i] > 32) {//半角
			dest[k++]   = (char)0xA3; 
			dest[k++] = (char)(src[i] + 0x80); 
		}
		else {//全角
			dest[k++] = src[i++]; 
			dest[k++] = src[i]; 
		}
	}
	dest[k] = '\0';
	
	return (std::string)(dest); 
}


std::string Full2Half4GBK(const char *src)
{
	char dest[strlen(src)+1];
	int  k = 0 ; 
	const unsigned char* _src = (const unsigned char*)src;
	for (int i = 0; _src[i] != '\0'; i++) 
	{ 
		if (_src[i] <= 127 && _src[i] >= 0) {//半角
			dest[k++] = src[i]; 
		}
		else if (_src[i] == 0xA1 && _src[i+1] == 0xA1)//全角空格
		{
			dest[k++] = 32;//半角空格
			i++;
		}//全角 全角的数字或字母及符号
		else if (_src[i] == 0xA3 && _src[i+1] >= 0xA1 && _src[i+1] <= 0xFD && _src[i+1] != 0xA4){
			dest[k++] = _src[++i] - 0x80;
		}
		else if (_src[i] == 0xA1 && _src[i+1] == 0xAB){
			dest[k++] = 0x7E;
			i++;
		}
		else if (_src[i] == 0xA1 && _src[i+1] == 0xE7){
			dest[k++] = 0x24;
			i++;
		}
		else{
			dest[k++] = _src[i++]; 
			dest[k++] = _src[i]; 
		}
	}
	dest[k] = '\0';
	
	return (std::string)dest;
}

std::string extractChars4GBK(const char *src,const std::string& gap){
	std::string res = "";
	for(int i=0;src[i]!='\0';i++){
		if (src[i] <= 127 && src[i] >= 0) {//半角
			res+=src[i];
		}
		else{
			res+=src[i];
			res+=src[++i];
		}
		res+=gap;
	}
	return res;
}

std::string removeVarIndex(const std::string& str){
	std::string res;
	int pos = 3;
	int lastPos = 0;
	while((pos = str.find("]",pos))!=std::string::npos){
		if (str[pos-1]>='0' && str[pos-1]<='9'){
			res += str.substr(lastPos,pos-1-lastPos);
			res += "]";
		}else{
			res += str.substr(lastPos,pos+1-lastPos);
		}
		pos++;
		lastPos = pos;
	}
	if(lastPos<str.length()){
		res += str.substr(lastPos);
	}
	return res;
}

//双字节编码字符串的find
int find2Byte(const std::string& str,const std::string& tar,int pos){
	while((pos=str.find(tar,pos))!=string::npos){
		if (pos%2==0)
			return pos;
		pos += 1;
	}
	return pos;
}

//双字节编码字符串的rfind
int rfind2Byte(const std::string& str,const std::string& tar,int pos){
	while((pos=str.rfind(tar,pos))!=string::npos){
		if (pos%2==0)
			return pos;
		pos += 1;
	}
	return pos;
}

//字符串查找算法SUNDAY
size_t SHIFT_ARRAY[256];
int find_sunday(const char* t,const char* p,const int& t_size,const int& p_size){
	int i;
	for( i=0; i < 256; i++ ) 
		SHIFT_ARRAY[i] = p_size+1;
	for( i=0; i < p_size; i++ )  
		SHIFT_ARRAY[(unsigned char)(*(p+i))] = p_size-i;
	int  limit = t_size-p_size+1;
	for( i=0; i < limit; i += SHIFT_ARRAY[(unsigned char)t[i+p_size]]){
		if( t[i] == *p )
        { 
            const char *match_text = t+i+1; 
            int  match_size = 1; 
            do{
                if( match_size == p_size )
                	return i; 
            }while( (*match_text++) == p[match_size++] ); 
        }
    }
    return std::string::npos;
}

size_t SHIFT_ARRAY_R[256];
int rfind_sunday(const char* t,const char* p,const int& t_size,const int& p_size){
	int i;
	for( i=0; i < 256; i++ ) 
		SHIFT_ARRAY_R[i] = p_size+1;
	for( i=0; i < p_size; i++ )  
		SHIFT_ARRAY_R[(unsigned char)(*(p+i))] = i+1;
	int  limit = p_size-2;
	for( i=t_size-1; i > limit; i -= SHIFT_ARRAY_R[(unsigned char)(t[i-p_size])]){
		if( t[i] == *(p+p_size-1) )
        { 
            const char *match_text = t+i-1; 
            int  match_size = 1; 
            do{
                if( match_size == p_size )
                	return i-p_size+1; 
            }while( (*match_text--) == p[p_size-1-match_size++] ); 
        }
    }
    return std::string::npos;
}

//从排序好的vector中查找是否包含一个元素
bool isfind_vec(const int& val,const vector<int>& vec){
	if (val>vec[vec.size()-1]
		||val<vec[0])
		return false;
	int i,b,e;
	b = 0;
	e = vec.size()-1;
	for (i=(b+e)/2;b<=e;i=(b+e)/2){
		if (val==vec[i])
			return true;
		else if (val>vec[i])
			b = i+1;
		else
			e = i-1;
	}
	return false;
}

//删除全角GBK编码中的标点符号
std::string removePunctuation4GBK_Full(const std::string& str){
	unsigned char c1,c2;
	std::string ret="";
	for (int i=0;i<str.length();i+=2){
		c1 = str[i];
		c2 = str[i+1];

		if (c1>=0xA1 && c1<=0xA2 && c2>=0xA1 && c2<=0xFE){
			if (c1==0xA1 && c2==0xA1){
				ret += c1;
				ret += c2;
			}
			continue;
		}else if (c1==0xA3 && ((c2>=0xA1 && c2<=0xAF)||(c2>=0xBA && c2<=0xC0)||(c2>=0xDB && c2<=0xE0)||c2>=0xFB)){
			continue;
		}
		ret += c1;
		ret += c2;
	}
	return ret;
}


int gbk_to_utf8(const char * in, size_t inlen,char * out, size_t* outlen) {
        if ((out == NULL) || (outlen == NULL))
                return -1;
        if (in == NULL) {
                *outlen = 0;
                return 0;
        }
        char * outbuf = (char *)out;
        char * inbuf = (char *)in;
        size_t outlenbuf = *outlen;
        size_t inlenbuf = inlen;
        iconv_t m_utf162gbk_ = iconv_open("GBK","utf-8");
        size_t ret = iconv(m_utf162gbk_, &inbuf, &inlenbuf, &outbuf, &outlenbuf);
        iconv_close(m_utf162gbk_ );
        if(ret == size_t(-1))
        {
                *outlen = outbuf - out;
				printf("[Http_Server]gbk2utf8 error(-1),input:%s,inlen:%d",in,inbuf - in);
                return -2;
        }
        else {
                *outlen = outbuf - out;
                if(ret == size_t(-1))
                {
                        printf("[Http_Server]gbk2utf8 error(-1),input:%s,inlen:%d",in,inbuf - in);
                        return -1;
                }
                else if (ret == size_t(-1)) {
                        printf("[Http_Server]gbk2utf8 error(-3),input:%s,inlen:%d",in,inbuf - in);
                        return -3;
                }
                else {
                        return *outlen;
                }
        }
}


int code_convert(char *from_charset,char *to_charset,const char *inbuf, size_t inlen,char *outbuf, size_t& outlen)
{
		iconv_t cd;
		char *inbuf_tmp = (char*)inbuf;
		char **pin = &inbuf_tmp;
		char **pout = &outbuf;
 
		cd = iconv_open(to_charset,from_charset);
		if (cd==(iconv_t)-1) {
			iconv_close(cd);
			cerr<<"[ICONV OPEN ERROR]"<<endl;
			return -1;
		}
		memset(outbuf,0,outlen);
		int ts = iconv(cd, pin, &inlen,pout, &outlen);
		if (ts==-1){
			iconv_close(cd);
			cerr<<"[ICONV ERROR]:"<<ts<<endl;
			return -1;
		}
		iconv_close(cd);
		return 0;
}
 
/* UTF-8 to GBK  */
int u2g(const char *inbuf, size_t inlen, char *outbuf, size_t& outlen)
{
         return code_convert("UTF-8//IGNORE","GB18030//IGNORE",inbuf,inlen,outbuf,outlen);
}
 
/* GBK to UTF-8 */
int g2u(const char *inbuf, size_t inlen, char *outbuf, size_t& outlen)
{
         return code_convert("GB18030//IGNORE", "UTF-8//IGNORE", inbuf, inlen, outbuf, outlen);
}

/*URL ENCODE*/
std::string url_encode(const string& src){
        char tmp_buf[20];
        std::string str="";
        for (int x = 0; x <src.length(); x++) {
                if (isalnum(src[x]) || (char)src[x] == '.' || (char)src[x] == '-' || (char)src[x] == '_') {
                        sprintf(tmp_buf, "%c", src[x]);
			str += tmp_buf;
		}
		else if (isspace(src[x])) {
			str += "+";
		}
		else {
			sprintf(tmp_buf, "%%%02X", (unsigned char)src[x]);
			str += tmp_buf;
		}
	}
	return str;
}

//10:10进制表示 2:二进制表示 8:八进制
void printString(const string& str,int type){
	unsigned short c;
	for (int i=0;i<str.length();i++){
		c = (unsigned short)(str[i]);
		cerr<<i<<":";
		if (type == 10)
			cerr<<dec<<c<<" ";
		else if (type==8)
			cerr<<oct<<c<<" ";
		else if (type==16)
			cerr<<hex<<c<<" ";
		else
			cerr<<dec<<c<<" ";
	}
	cerr<<endl;
}
/*
int xml_parse(const char *data, size_t data_len, char *val, size_t &val_len)
{
	int len = val_len;
	//data[data_len]='\0';
	xmlDocPtr xmldoc = xmlParseMemory(data, data_len);
	if(xmldoc == NULL){
		cerr<<"ERROR:xml parse failed"<<endl;
		val_len = 0;
		val[0] = '\0';
		return 0;
	}
	xmlChar *xml;
	xmlDocDumpMemory(xmldoc,&xml,&len);
	val_len = len * sizeof(xmlChar);
	memcpy(val,xml,val_len);
	val[val_len] = '\0';
	xmlFree(xml);
	free(xmldoc);
	return 1;
}
*/

void SBC2DBC_UNICODE(const char* from,char* to,int& from_len,int& to_len){
	int i;
	for (i=0;i<from_len-1;i+=2){
		unsigned char cur_q = (unsigned char)from[i];
		unsigned char cur_h = (unsigned char)from[i+1];
		if (cur_q==0xFF && cur_h<=0x5E){
			unsigned int val = cur_q*256 + cur_h;
			val -= 65248;
			to[i] = (char)(val>>8);
			to[i+1] = (char)(val&0x00FF);
		}else if (cur_q==0x30 && cur_h==0x00){
			to[i] = 0;
			to[i] = 32;
		}else if (cur_q==0x00 && cur_h==0x00){
			break;
		}else{
			to[i] = from[i];
			to[i+1] = from[i+1];
		}
	}
	from_len = i;
	to_len = i;
	to[i]='\0';
	to[i+1]='\0';
	return;
}

template<class T>
bool ContainVector(const std::vector<T>& ori,const std::vector<T>& dest){
	int i,j;
	i = j = 0;
	while(i<ori.size() && j<dest.size()){
		if (ori[i]==dest[j]){
			i++;
			j++;
		}else{
			i++;
		}
	}
	if (j<dest.size())
		return false;
	else
		return true;
}

template<class T>
void RemoveVector(std::vector<T>& from,const std::vector<T>& remove){
	int i,j;
	i = j = 0;
	while(i<from.size() && j<remove.size()){
		if (from[i]==remove[j]){
			from.erase(from.begin()+i);
			j++;
		}else if (from[i]<remove[j]){
			i++;
		}else{
			j++;
		}
	}
	return;
}

//字符串删除前面的和后面的内容
std::string rmHeadTail(const std::string& str,const std::string& head,const std::string& tail){
	std::string ret="";
	size_t h = str.find(head);
	if (h!=std::string::npos){
		h += head.length();
		size_t t = str.find(tail,h);
		if (t != std::string::npos){
			ret = str.substr(h,t-h);
		}
	}
	return ret;
}


}//namespace SOGOUCHAT


