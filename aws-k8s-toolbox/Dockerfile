FROM python:slim-bullseye
LABEL REFRESHED_AT=20230613
# image used inside Gitlab CICD Pipelines

# Application list
ARG KUBECTL_VERSION=1.25.9
ARG HELM_VERSION=v3.9.0
ARG KUBECONFORM_VERSION=0.4.14
# env
ENV BIN_DIR /opt/builder/bin
ENV USER builder

# OS depenencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
       curl \
       wget \
       git \
       apt-transport-https \
       ca-certificates \
       gnupg \
       jq \
       unzip \
       make \
       uuid-runtime \
    && rm -rf /var/lib/apt/lists/*

# workdir
RUN useradd -ms /bin/bash ${USER} -d /opt/${USER}
WORKDIR ${BIN_DIR}

# kubectl
RUN curl -o ${BIN_DIR}/kubectl -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && KUBECTL_BIN="${BIN_DIR}/kubectl" \
    && chmod +x ${KUBECTL_BIN} \
    && curl -o ${BIN_DIR}/kubectl.sha256 -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" \
    && echo "$(cat ${KUBECTL_BIN}.sha256) ${KUBECTL_BIN}" | sha256sum --check \
    && echo "INFO - kubectl version: " \
    && ${KUBECTL_BIN} version --client \
    && rm ${BIN_DIR}/kubectl.sha256 \
    && chown ${USER}. ${KUBECTL_BIN}
    
# helm
ENV HELM3_DOWNLOAD_URL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
RUN curl -fsSL -o ${BIN_DIR}/get_helm.sh ${HELM3_DOWNLOAD_URL} \
    && chmod 700 ${BIN_DIR}/get_helm.sh \
    && DESIRED_VERSION=${HELM_VERSION} ${BIN_DIR}/get_helm.sh \
    # test it
    && HELM_BIN_TEMP=$(which helm) \
    && HELM_BIN=${BIN_DIR}/helm \
    && mv ${HELM_BIN_TEMP} ${HELM_BIN} \
    && ${HELM_BIN} version \
    && rm ${BIN_DIR}/get_helm.sh \
    && chown ${USER}. ${HELM_BIN}

# eskctl
RUN ARCH=amd64 \
    ; PLATFORM=$(uname -s)_$ARCH \
    ; curl -sLO "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz" \
    && curl -sL "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_checksums.txt" | grep $PLATFORM | sha256sum --check \
    && tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz \
    && mv /tmp/eksctl ${BIN_DIR}/

# kubeconform install
RUN curl -fsSL -o /tmp/kubeconform.tar.gz https://github.com/yannh/kubeconform/releases/download/v${KUBECONFORM_VERSION}/kubeconform-linux-amd64.tar.gz \
    && tar -xzf /tmp/kubeconform.tar.gz -C ${BIN_DIR} \
    && rm /tmp/kubeconform.tar.gz

# awscli install
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && aws --version

#USER ${USER}
ENV PATH="${BIN_DIR}:${PATH}"
