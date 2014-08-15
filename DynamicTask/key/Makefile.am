include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libkey.la
libkey_la_SOURCES=KeyGenerator.cpp
libkey_la_LIBADD=../common/libcommon.la -L/usr/lib64/mysql/ -lmysqlclient

bin_PROGRAMS+=test
test_SOURCES=test.cpp
test_LDADD=-lkey libkey.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
