swig -python -c++ LumiFilter.i
c++ -fpic -shared -I/usr/include/python2.7 LumiFilter_wrap.cxx -o _LumiFilter.so