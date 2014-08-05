#!/bin/sh
#
# pacman -S boost
# Change the following in setup.py (around line 71):
#    "-DBOOST_FILESYSTEM_VERSION=2",
#    "-DBOOST_FILESYSTEM_VERSION=3",
#
ROOT_DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" )"
VENDOR_DIR="$ROOT_DIR/vendor"
DELUGE_DIR="$VENDOR_DIR/deluge"
GIT_URL="git://deluge-torrent.org/deluge.git"
GIT_BRANCH="1.3-stable"


echo "Using project root for installation: $ROOT_DIR"
source $ROOT_DIR/virtenv/bin/activate


echo "Updating python dependencies... please wait"
pip install -r $ROOT_DIR/requirements-deluge-local.txt --upgrade -q
if [ ! -d "$VENDOR_DIR" ]; then
    mkdir "$VENDOR_DIR"
fi

echo "Setting up deluge installation"
cd ${VENDOR_DIR}
if [ ! -d "$DELUGE_DIR" ]; then
    echo "Cloning initial source tree"
    git clone "$GIT_URL" deluge
    cd "$DELUGE_DIR"
    git checkout -b "$GIT_BRANCH" origin/"$GIT_BRANCH"
else
    echo "Updating existing sources"
    cd "$DELUGE_DIR"
    git pull
fi
cd "$VENDOR_DIR"
wget http://colocrossing.dl.sourceforge.net/project/boost/boost/1.49.0/boost_1_49_0.tar.gz
tar xfz boost_1_49_0.tar.gz

python setup.py clean -a
