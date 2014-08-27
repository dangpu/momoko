include $(top_srcdir)/common.mk
INCLUDES += -I/usr/include/openssl/

bin_PROGRAMS=HttpServer
HttpServer_SOURCES=config_map.hpp linked_list.hpp service_log.hpp socket_handle.hpp wait_list.hpp worker.hpp http_server.hpp http_server.cpp query_processor.hpp query_processor.cpp configuration.hpp configuration.cpp task_base.hpp task_base.cpp main.cpp
#LYRoute_LDADD=-lpthread ../json/libjson.la ../Route/libroute.la
HttpServer_LDADD=-lpthread ../json/libjson.la ../validation/libvalidation.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256

