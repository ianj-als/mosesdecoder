#!/bin/bash

BRANCH="master"
declare -i NO_MOVE=0

function usage() {
  echo "`basename $0` -r [Moses Git repo] -b [Moses Git branch: default ${BRANCH}] -v [RPM version]"
  exit 1
}

if [ $# -lt 4 ]; then
  usage
fi

while getopts r:b:v:nh OPTION
do
  case "$OPTION" in
      r) REPO="${OPTARG}";;
      b) BRANCH="${OPTARG}";;
      v) VERSION="${OPTARG}";;
      n) NO_MOVE=1;;
      [h\?]) usage;;
  esac
done

if [ ! -d ./rpmbuild ]; then
  echo "RPM build directory not in current working direcotry"
  exit 1
fi

declare -r MOSES_DIR="moses-${VERSION}"
git clone ${REPO} ${MOSES_DIR}
if [ $? -ne 0 ]; then
  echo "Failed to clone Git repository ${REPO}"
  exit 3
fi

cd ${MOSES_DIR}

git checkout ${BRANCH}
if [ $? -ne 0 ]; then
  echo "Failed to checkout branch ${BRANCH}"
  exit 3
fi

cd ..

tar -cf moses-${VERSION}.tar ${MOSES_DIR}
gzip -f9 moses-${VERSION}.tar

if [ ${NO_MOVE} -eq 0 ]; then
  cp -R ./rpmbuild ${HOME}
  if [ ! -d ${HOME}/rpmbuild/SOURCES ]; then
    mkdir ${HOME}/rpmbuild/SOURCES
  fi
  mv moses-${VERSION}.tar.gz ${HOME}/rpmbuild/SOURCES
fi

rm -Rf ${MOSES_DIR}
