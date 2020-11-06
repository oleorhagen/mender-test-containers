FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# prepare NFS cache for yocto
RUN mkdir -p /mnt/sstate-cache

# basic tools
COPY deb-requirements.txt .
RUN apt-get update -qq && apt-get install -yyq $(cat deb-requirements.txt) && apt-get install -yq linux-modules-`uname -r`

# Locales
RUN locale-gen --purge en_US.UTF-8
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8

COPY requirements-py3.txt .
RUN pip3 install -r requirements-py3.txt

# golang from upstream
RUN wget -q https://storage.googleapis.com/golang/go1.12.linux-amd64.tar.gz && gunzip -c go1.12.linux-amd64.tar.gz | (cd /usr/local && tar x) && ln -sf /usr/local/go/bin/go /usr/local/bin/go &&  ln -sf /usr/local/go/bin/godoc /usr/local/bin/godoc && ln -sf /usr/local/go/bin/gofmt /usr/local/bin/gofmt


# mender user dir
RUN useradd -m -u 1010 mender && usermod -a -G kvm mender && usermod -a -G docker mender

# Prepare mender user
RUN mkdir -p /home/mender/.ssh && echo "mender ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && sed -i -e 's/^\( *Defaults *requiretty *\)$/# \1/' /etc/sudoers && chown -R mender:mender /home/mender

# debugfs
RUN cp /sbin/debugfs /usr/bin/ || echo "debugfs not in /sbin/"

# enable sysstat monitoring suite for Debian/Ubuntu
RUN sed -i 's/false/true/g' /etc/default/sysstat
