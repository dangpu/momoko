include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libmonitor.la
libmonitor_la_SOURCES=TaskMonitor.cpp
libmonitor_la_LIBADD= -lpthread ../json/libjson.la ../common/libcommon.la

bin_PROGRAMS+=test
test_SOURCES=test.cpp
test_LDADD=-lkey ../key/libkey.la -lmonitor libmonitor.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
