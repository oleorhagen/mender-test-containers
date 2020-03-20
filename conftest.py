#!/usr/bin/python3
# Copyright 2019 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pytest
import re
import requests
import subprocess
import time
import os.path
import logging

from fabric import Connection

from .helpers import *

@pytest.fixture(scope="class")
def setup_test_container(request, setup_test_container_props, mender_version):
    # This should be parametrized in the mother project.
    image = setup_test_container_props.image_name

    if setup_test_container_props.append_mender_version:
        image = "%s:%s" % (image, mender_version)

    cmd = "docker run --rm --network host --privileged -tid %s" % image
    logging.debug("setup_test_container: %s", cmd)
    output = subprocess.check_output(cmd, shell=True)

    global docker_container_id
    docker_container_id = output.decode("utf-8").split("\n")[0]
    setup_test_container_props.container_id = docker_container_id

    def finalizer():
        cmd = "docker stop {}".format(docker_container_id)
        logging.debug("setup_test_container: %s", cmd)
        subprocess.check_output(cmd, shell=True)
    request.addfinalizer(finalizer)

    ready = wait_for_container_boot(docker_container_id)

    assert ready, "Image did not boot. Aborting"
    return setup_test_container_props

@pytest.fixture(scope="class")
def setup_tester_ssh_connection(setup_test_container):
    yield new_tester_ssh_connection(setup_test_container)

@pytest.fixture(scope="class")
def setup_mender_configured(setup_test_container, setup_tester_ssh_connection, mender_deb_version):
    if setup_tester_ssh_connection.run("test -x /usr/bin/mender", warn=True).exited == 0:
        # If mender is already present, do nothing.
        return

    url = ("https://d1b0l86ne08fsf.cloudfront.net/%s/dist-packages/debian/armhf/mender-client_%s-1_armhf.deb"
           % (mender_deb_version, mender_deb_version))
    filename = os.path.basename(url)
    c = requests.get(url, stream=True)
    with open(filename, "wb") as fd:
        fd.write(c.raw.read())

    try:
        put(setup_tester_ssh_connection, filename, key_filename=setup_test_container.key_filename)
        setup_tester_ssh_connection.sudo("DEBIAN_FRONTEND=noninteractive dpkg -i %s" % filename)
    finally:
        os.remove(filename)

    output = setup_tester_ssh_connection.run("uname -m").stdout.strip()
    if output == "x86_64":
        device_type = "generic-x86_64"
    elif output.startswith("arm"):
        device_type = "generic-armv6"
    else:
        raise KeyError("%s is not a recognized machine type" % output)

    setup_tester_ssh_connection.sudo("mkdir -p /var/lib/mender")
    setup_tester_ssh_connection.run("echo device_type=%s | sudo tee /var/lib/mender/device_type" % device_type)
