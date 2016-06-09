#!/bin/bash
# set -e

# Add third-party ppas
sudo apt-add-repository -y ppa:webupd8team/java
sudo add-apt-repository -y ppa:webupd8team/sublime-text-3

# update yum repo
sudo apt-get update

# basics
sudo apt-get install -y tmux vim zsh bash-completion emacs tree wget curl sshpass nano mlocate virtualbox gparted exfat-utils sublime-text-installer openvpn indicator-multiload openssh-server openssh-client

# system
sudo apt-get install -y ntp lvm2 lshw usbutils pciutils denyhosts autofs mdadm iperf lshw sysstat fio iotop iftop htop iptraf tcpdump mtr tcpdump clusterssh pdsh nmap

# development
sudo apt-get install -y build-essential subversion r-base r-base-dev r-base-core gnuplot git git-svn git-cvs ant libcurl3 libcurl4-openssl-dev openssl libxml2-dev libxslt-dev maven oracle-java7-installer libssl-dev exuberant-ctags

sudo pip install dbgp vim-debug pep8 flake8 pyflakes isort

# TMUX
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
curl https://raw.githubusercontent.com/caesar0301/omnilab-misc/master/Scripts/dotfiles/.tmux.conf -o ~/.tmux.conf

# R DEV
curl https://raw.githubusercontent.com/caesar0301/omnilab-misc/master/Scripts/dotfiles/.Rprofile -o ~/.Rprofile

# SPACEMACS
git clone https://github.com/syl20bnr/spacemacs ~/.emacs.d

# VIM
curl https://raw.githubusercontent.com/fisadev/fisa-vim-config/master/.vimrc -o ~/.vimrc

exit 0;
