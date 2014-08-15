include $(top_srcdir)/common.mk

bin_PROGRAMS=
lib_LIBRARIES=
lib_LTLIBRARIES=

lib_LTLIBRARIES+=libcommon.la
libcommon_la_SOURCES=time/datetime.cpp string/algorithm.cpp string/string_number.cpp string/string_piece.cpp StringTools.cpp MyRedis.cpp
libcommon_la_LIBADD =-lhiredis

