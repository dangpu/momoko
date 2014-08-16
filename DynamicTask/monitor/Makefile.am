include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libmonitor.la
libmonitor_la_SOURCES=TaskMonitor.cpp
libmonitor_la_LIBADD=../key/libkey.la ../json/libjson.la ../common/libcommon.la -L/usr/lib64/mysql/ -lmysqlclient

bin_PROGRAMS+=test
test_SOURCES=test.cpp
test_LDADD=-lmonitor libmonitor.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
