#!/bin/bash
# Configurations for .profile, .bash_profile, or .bashrc

export LC_CTYPE=zh_CN.UTF-8
export EDITOR='vim'
export DEVROOT=/home/chenxm/workspace/tw

# Java
export JAVA_OPTIONS="-Xmx8191m -XX:MaxPermSize=2048m"
export JAVA_HOME=/usr/lib/jvm/default
export JRE_HOME=$JAVA_HOME/jre
export CLASSPATH=.:$CLASSPATH:$JAVA_HOME/lib:$JRE_HOME/lib
export PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin
export MAVEN_OPTS="-Xmx8191m -XX:MaxPermSize=2048m"

# Texlive
export PATH=$PATH:/usr/local/texlive/2015/bin/x86_64-linux/:$PATH
export MANPATH=/usr/local/texlive/2015/texmf-dist/doc/man:$MANPATH
export INFOPATH=/usr/local/texlive/2015/texmf-dist/doc/info:$INFOPATH
