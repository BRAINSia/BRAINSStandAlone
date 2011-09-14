#!/bin/bash
#
# Set the library paths such that all locally built shared 
# libraries are found and used
# ahead of system libs
package=BRAINSStandAlone

#
# when run by cron, the path variable is only /bin:/usr/bin
export PATH="/opt/cmake/bin:/usr/local/bin:/usr/sbin:$PATH"

#
# make the testing directory, based on current user name
#user=`who -m | sed -e 's/ .*$//'`
user=${LOGNAME}

ThisComputer=`hostname`

OS=$(uname -s)
if [ "${OS}" = "Linux" ] ; then
    NPROCS=$(grep -c ^processor /proc/cpuinfo)
    export CFLAGS="${CFLAGS:-} -fpic"
    export CXXFLAGS="${CXXFLAGS:-} -fpic"
else
    NPROCS=$(system_profiler | awk '/Number Of Cores/{print $5}{next;}')
fi

#
# the default is to use /brainsdev/kent -- which is
# appropriate on the b2dev VMs.
if [ $# = 0 ] ; then
    startdir=/brainsdev/kent/Testing
else
    startdir=$1
    shift
fi

#
# needed for ssl authentication for git
export GIT_SSL_NO_VERIFY=true

# turn on coverage at command line
if [ $# = 0 ] ; then
    coverage=0
else
    if [ $1 = "coverage" ] ; then
	coverage=1
    fi
fi

# create the testing directory if necessary
mkdir -p ${startdir}
if [ ! -d ${startdir} ] ; then
    echo ${startdir} cannot be created, exiting
    exit 1
fi

cd ${startdir}

echo checking out test data in `pwd`

mkdir -p ${startdir}/${ThisComputer}

cd ${startdir}/${ThisComputer}

top=`pwd`
echo WORKING IN $top

# check out BRAINSStandAlone in a directory unique to each host -- this is unfortunately necessary
# because svn can't update a directory  checked out by a newer version of svn, so
# every host has their own copy of BRAINS3 so that it's compatible with the local svn version.
if [ -d BRAINSStandAlone ] ; then
    cd BRAINSStandAlone
    git pull
else
    git clone git@github.com:BRAINSia/BRAINSStandAlone.git
fi
if [ $? != 0 ]
then
    echo BRAINSStandAlone checkout failed, continuing with old version
fi


OsName=`uname`
which gcc > /dev/null 2>&1
if [ $? == 0 ] ; then
    Compiler=gcc-`gcc -dumpversion`-`gcc -dumpmachine`
else
    Compiler=unknown
fi

for BUILD_TYPE in Debug Release
do
    B3Build=${top}/${BUILD_TYPE}

    mkdir -p ${B3Build}
    cd ${B3Build}

    #
    # unset base CFlags -- use just flags specified by
    # the Build type
    cmake -DSITE:STRING=${ThisComputer} \
	-DBUILDNAME:STRING="${OsName}-${Compiler}-${BUILD_TYPE}" \
        -DBUILD_SHARED_LIBS:BOOL=Off \
	-DCMAKE_BUILD_TYPE:STRING=${BUILD_TYPE} \
        ${top}/BRAINSStandAlone
    echo "Building in `pwd`"
    scriptname=`basename $0`
    make -j ${NPROCS}
    cd BRAINSTools-build
    if [ $scriptname = "nightly.sh" ] ; then
	ctest -j ${NPROCS} -D Nightly
    else
	ctest -j ${NPROCS} -D Experimental
    fi
    cd ..
done

cd ${top}
