include $(top_srcdir)/common.mk

nobase_include_HEADERS= \
	Server/worker.hpp \
Server/wait_list.hpp	\
Server/task_base.hpp	\
Server/socket_handle.hpp	\
Server/service_log.hpp	\
Server/linked_list.hpp	\
Server/config_map.hpp	\
Server/configuration.hpp	\
Server/http_server.hpp	\
Server/query_processor.hpp	

SUBDIRS=@PACKAGE_DEPENDENCIES@ Client validation Server
export @MODULE_ROOT_VARS@ BUILD_DEPENDENCIES
