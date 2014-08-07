include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libdata.la
libdata_la_SOURCES=data.cpp
libdata_la_LIBADD= -lpthread ../json/libjson.la ../common/libcommon.la

lib_LTLIBRARIES+=libmaster.la
libmaster_la_SOURCES=master.cpp
libmaster_la_LIBADD= -lpthread libdata.la ../common/libcommon.la

lib_LTLIBRARIES+=libworkload.la
libworkload_la_SOURCES=workload.cpp
libworkload_la_LIBADD= -lpthread libdata.la ../common/libcommon.la -L/usr/lib64/mysql/ -lmysqlclient

bin_PROGRAMS+=test
test_SOURCES=main.cpp CommonFuc.cpp
test_LDADD=-ldata libdata.la -lmaster libmaster.la -lworkload libworkload.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
