ARG DISTRO=debian
ARG VERSION=buster
FROM $DISTRO:$VERSION

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    dh-make \
    git \
    wget \
    curl \
    debhelper \
    devscripts \
    equivs

ARG ARCH=amd64
ARG DISTRO=debian
ARG VERSION=buster

RUN if [ "${DISTRO}" = "ubuntu" -a "${ARCH}" != "amd64" ]; then \
        sed -i 's/^deb/deb [arch=amd64]/' /etc/apt/sources.list && \
        touch /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $VERSION main restricted universe multiverse" > /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $VERSION-updates main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $VERSION-backports main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $VERSION-security main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list; \
    fi

RUN dpkg --add-architecture ${ARCH} && \
    apt-get update

RUN if ! [ "${DISTRO}" = "debian" -a "${ARCH}" = "armhf" ]; then \
        apt-get install -y \
        pkg-config \
        liblzma-dev:${ARCH} \
        libssl-dev:${ARCH} \
        libglib2.0-dev:${ARCH} \
        libmount-dev:${ARCH} \
        libc-dev:${ARCH} \
        libc6-dev:${ARCH} \
        linux-libc-dev:${ARCH} \
        ; \
    fi


RUN if [ "${ARCH}" = "arm64" ]; then \
        apt-get install -y gcc-aarch64-linux-gnu; \
    fi

RUN if [ "${ARCH}" = "armhf" -a "${DISTRO}" != "debian" ]; then \
        apt-get install -y gcc-arm-linux-gnueabihf; \
    fi

# TODO: Figure out why these packages are required
RUN if [ "${DISTRO}" = "debian" -a "${ARCH}" = "armhf" ]; then \
        apt-get install -y libmount1:armhf zlib1g:armhf; \
    fi

COPY install-armv6-cross-toolchain /bin
RUN if [ "${DISTRO}" = "debian" -a "${ARCH}" = "armhf" ]; then \
        RASPBIAN_VERSION=${VERSION} /bin/install-armv6-cross-toolchain; \
    fi
