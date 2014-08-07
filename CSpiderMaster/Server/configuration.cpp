#include "configuration.hpp"
#include <netdb.h>
#include "config_map.hpp"
#include "service_log.hpp"
#include <cstring>

int Configuration::open(const char *filename, const char *key)
{
	if (readParameter(filename, key))
		return -1;
	if (readThreadNumber(filename, key))
		return -1;
	if (readDataPath(filename, key))
		return -1;
    
	return 0;
}

int Configuration::SeparateIP(const char * value,char * ip, int * port)
{
	const char * pos = strchr(value,':');
	if(!pos)
	{
		_ERROR("error ip address.%s",value);
		return -1;
	}
	//*port = htons(atoi(pos+1));
	*port = atoi(pos+1);
	int len = pos - value;
	memcpy(ip,value,len);
	ip[len] = '\0';
	return 0;
}

int Configuration::readParameter(const char *filename, const char * key)
{
	config_map config;
	if (config.import(filename))
		_ERROR_RETURN(-1, "[config_map::import(%s)]", filename);

	std::string full_key(std::string(key) + "/Parameter");
	_INFO("[readParameter]key:%s",full_key.c_str());
	config.set_section(full_key.c_str());
	const char *value;

	if (config.get_value("ListenPort", value))
	{
		_ERROR("no config ListenPort");
		return -1;
	}
	//listen_port = htons(atoi(value));
	listen_port = atoi(value);

	if (config.get_value("ThreadStackSize", value))
	{
		_ERROR("no config ThreadStackSize,use default (256k)");
		thread_stack_size = 256 * (1 << 10);
	}
	else
		thread_stack_size = atoi(value) * (1 << 10);

	if(config.get_value("CommandLengthWarning",value))
	{
		_ERROR("no config CommandLengthWarning");
		return -1;
	}
	commandlengthwarning = atoi(value);
 
    return 0;
}

int Configuration::readThreadNumber(const char *filename, const char * key)
{
	config_map config;
	if (config.import(filename))
		_ERROR_RETURN(-1, "[config_map::import(%s)]", filename);
    
	std::string full_key(std::string(key) + "/ThreadNumber");
	_INFO("[readThreadNumber]key:%s",full_key.c_str());
	config.set_section(full_key.c_str());
	const char *value;

	if (config.get_value("ReceiverThread", value))
	{
		_ERROR("no config ReceiverThread, use default(3) ");
		receiver_num = 3;
	}
	else
		receiver_num = atoi(value);

	if (config.get_value("ProcessorThread", value))
	{
		_ERROR("no config ProcessorThread,use default(20)");
		processor_num = 20;
	}
	else 
		processor_num = atoi(value);

	return 0;
}

int Configuration::readDataPath(const char *filename, const char * key)
{
	config_map config;
	if (config.import(filename))
		_ERROR_RETURN(-1, "[config_map::import(%s)]", filename);
    
	std::string full_key(std::string(key) + "/DataPath");
	_INFO("[readDataPath]key:%s",full_key.c_str());
	config.set_section(full_key.c_str());
	const char *value;

	if (config.get_value("DataPath", value))
	{
		_ERROR("no config DataPath, use default('/data/') ");
		data_path = "/data/";
	}
	else
		data_path = std::string(value);

	return 0;
}

std::string Configuration::readString(char const * filename, char const * path, char const * name)
{
	config_map config;
	std::string ret = "";
	const char * value;

	if (config.import(filename))
		return ret;

	config.set_section(path);
	if (config.get_value(name, value))
		return ret;

	ret = value;
	return ret;
}

