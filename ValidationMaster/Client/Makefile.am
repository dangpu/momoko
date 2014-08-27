include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libclient.la
libclient_la_SOURCES=SocketClient.cpp CommonFuc.cpp
libclient_la_LIBADD= -lpthread

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
