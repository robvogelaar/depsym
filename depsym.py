#!/usr/bin/env python

import re
import os
import string
import sys
from stat import *
from optparse import OptionParser


def is_symlink(fpath):
    stdout = os.popen("file %s"%fpath).readline()
    ret = stdout.find('symbolic link to')
    return (ret > 0) 

def is_exe(fpath):
    stdout = os.popen("file %s"%fpath).readline()
    #print stdout
    ret = stdout.find('ELF 32-bit LSB  executable, MIPS')
    return (ret > 0) 
                 
def is_lib(fpath):
    stdout = os.popen("file %s"%fpath).readline()
    ret = stdout.find('ELF 32-bit LSB  shared object, MIPS')
    return (ret > 0) 



def has_dependency(fpath, dependency):

    if dependency == "":
        return 1

    all_libs = ""

    linux_cmd = "/usr/bin/mklibs-readelf --print-needed %s"%fpath

    try:
        stdout = os.popen(linux_cmd)

        for foundlib in stdout:
        
            all_libs = "%s;%s"%(all_libs, foundlib[:-1])

    except:
        print "Unexpected error:", sys.exc_info()[0]

    ret = all_libs.lower().find(dependency.lower())
    return (ret > 0)


##def matching_symbols(fpath, match):
##
##    all_symbols = "\t"
##
##    linux_cmd = "/usr/bin/mklibs-readelf --print-symbols-undefined %s"%fpath
##
##    try:
##        stdout = os.popen(linux_cmd)
##
##        for foundsymbol in stdout:
##
##            if foundsymbol.lower().find(match.lower()) > -1 :
##
##                all_symbols = "%s%s\n\t"%(all_symbols, demangle(foundsymbol[0:foundsymbol.find(' ')]))
##
##    except:
##        print "Unexpected error:", sys.exc_info()[0]
##
##    return all_symbols



def matching_symbols(fpath, match):

    all_symbols = []

    linux_cmd = "/usr/bin/mklibs-readelf --print-symbols-undefined %s"%fpath

    try:
        stdout = os.popen(linux_cmd)

        for foundsymbol in stdout:

            if foundsymbol.lower().find(match.lower()) > -1 :

                all_symbols.append(demangle(foundsymbol[0:foundsymbol.find(' ')]))

    except:
        print "Unexpected error:", sys.exc_info()[0]

    return sorted(all_symbols)



def demangle(names):

    linux_cmd = "/usr/bin/c++filt %s"%names

    try:
        stdout = os.popen(linux_cmd)

        for x in stdout:
            pass

    except:
        print "Unexpected error:", sys.exc_info()[0]

    return x[:-1]



def dofile(dir, file, options, dependency, symbol):

    if is_symlink(os.path.join(dir,file)):
        pass
        # print 'sym:' + os.path.join(dir, file)

    else:
        if options.exe:
            if is_exe(os.path.join(dir,file)):

                if not has_dependency(os.path.join(dir, file), dependency):
                    pass
                else:
                    print 'exe:(%s)(%s)'%(dependency, symbol) + os.path.join(dir, file)

                    for item in matching_symbols(os.path.join(dir, file), symbol):
                        print "\t", item



        if options.so:
            if is_lib(os.path.join(dir,file)):

                if not has_dependency(os.path.join(dir, file), dependency):
                    pass
                else:
                    print '.so:(%s)(%s)'%(dependency, symbol) + os.path.join(dir, file)
                    for item in matching_symbols(os.path.join(dir, file), symbol):
                        print "\t", item



def main():

    parser = OptionParser()

    parser.add_option("-r", "--rootfs", dest = "rootfs",
                      action = "store", type = "string",
                      help = "rootfs directory")

    parser.add_option("-d", "--dependency", dest = "dependency",
                      action = "store", type = "string",
                      help = "dependency to check")

    parser.add_option("-s", "--symbol", dest = "symbol",
                      action = "store", type = "string",
                      help = "symbol to check")


    parser.add_option("--exe",
                              dest = "exe", action = "store_true",
                              help = "manage the networking ")

    parser.add_option("--so",
                              dest = "so", action = "store_true",
                              help = "manage the networking ")



    (options, args) = parser.parse_args()

    if not options.rootfs:
        parser.error('rootfs not given')


    if not options.dependency:
        dependency = ""
    else:
        dependency = options.dependency


    if not options.symbol:
        symbol = ""
    else:
        symbol = options.symbol

    print 'dependency =',
    print dependency

    print 'symbol =',
    print symbol


    if os.path.isdir(options.rootfs):
        for dir, dirs, files in os.walk(options.rootfs):
            for file in files:
                dofile(dir, file, options, dependency, symbol)

    else:
        dofile([], options.rootfs, options, dependency, symbol)


if __name__ == "__main__":
    main()
