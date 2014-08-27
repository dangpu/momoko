include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libvalidation.la
libvalidation_la_SOURCES=validation.cpp CommonFuc.cpp
libvalidation_la_LIBADD= -lpthread ../common/libcommon.la ../Client/libclient.la -L/usr/lib64/mysql/ -lmysqlclient 


bin_PROGRAMS+=test
test_SOURCES=main.cpp
test_LDADD=-lvalidation libvalidation.la

AM_CPPFLAGS+=-DSS_DOCID_BITS=256
