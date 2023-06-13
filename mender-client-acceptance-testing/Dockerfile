FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# prepare NFS cache for yocto
RUN mkdir -p /mnt/sstate-cache

# install pyyaml via pip to workardound a later conflict if installed via OS package (awscli depends on python3-yaml)
RUN apt-get update -qq && apt-get install -yyq python3-pip && pip3 install --upgrade pip && pip3 install pyyaml

# Get OS requirements from master
# linux-modules-$(uname -r | sed 's/gcp/gke/') is a workaround for https://northerntech.atlassian.net/browse/QA-597
RUN apt-get install -yyq wget && \
    wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_deb.txt && \
    apt-get install -yyq $(cat requirements_deb.txt) && apt-get install -yq linux-modules-$(uname -r | sed 's/gcp/gke/') && \
    apt-get remove -yyq docker docker.io containerd runc && apt-get install -yyq ca-certificates curl gnupg lsb-release && \
    mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update -qq && apt-get install -yyq docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Locales
RUN locale-gen --purge en_US.UTF-8
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8

# Python 3 requirements from master
RUN wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_py3.txt && \
    pip3 install -r requirements_py3.txt && \
    rm requirements_py3.txt

# mender user dir
RUN useradd -m -u 1010 mender && usermod -a -G kvm mender && usermod -a -G docker mender

# Prepare mender user
RUN mkdir -p /home/mender/.ssh && echo "mender ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && sed -i -e 's/^\( *Defaults *requiretty *\)$/# \1/' /etc/sudoers && chown -R mender:mender /home/mender

# debugfs
RUN cp /sbin/debugfs /usr/bin/ || echo "debugfs not in /sbin/"

# enable sysstat monitoring suite for Debian/Ubuntu
RUN sed -i 's/false/true/g' /etc/default/sysstat
