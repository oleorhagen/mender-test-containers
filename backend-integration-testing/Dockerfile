FROM python:3.10-bullseye

RUN apt-get -y -qq update && apt-get -qq -y install docker.io libzbar0 apt-transport-https gnupg2 && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y awscli kubectl=1.23.7-00 && \
    curl -o /usr/bin/aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.17.9/2020-08-04/bin/linux/amd64/aws-iam-authenticator && \
    chmod 755 /usr/bin/aws-iam-authenticator && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-py3.txt .

RUN pip3 install -r requirements-py3.txt

ENTRYPOINT ["bash", "/tests/run.sh"]
