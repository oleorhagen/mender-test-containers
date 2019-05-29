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

import os
import re
import signal
import stat
import subprocess
import time
from fabric import Config
from fabric import Connection
from paramiko import SSHException

def _prepare_key_arg(key_filename):
    if key_filename:
        # Git doesn't track rw permissions, but the keyfile needs to be 600 for
        # scp to accept it, so fix that here.
        os.chmod(key_filename, stat.S_IRUSR | stat.S_IWUSR)
        return "-i %s" % key_filename
    else:
        return ""

def put(conn, file, key_filename=None, local_path=".", remote_path="."):
    key_arg = _prepare_key_arg(key_filename)
    conn.local("scp %s -C -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P %s %s %s@%s:%s" %
          (key_arg, conn.port, os.path.join(local_path, file), conn.user, conn.host, remote_path))

class PortForward:
    user = None
    host = None
    port = None
    key_filename = None
    local_port = None
    remote_port = None

    args = None
    proc = None

    def __init__(self, conn, key_filename, local_port, remote_port):
        self.user = conn.user
        self.host = conn.host
        self.port = conn.port
        self.key_filename = key_filename
        self.local_port = local_port
        self.remote_port = remote_port

    def __enter__(self):
        try:
            key_arg = _prepare_key_arg(self.key_filename).split()
            self.args = ["ssh", "-N", "-f"] + key_arg + [
                "-L", "%d:localhost:%d" % (self.local_port, self.remote_port),
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-p", "%d" % self.port,
                "%s@%s" % (self.user, self.host)]
            self.proc = subprocess.Popen(self.args)
            # '-f' flag causes SSH to background itself. We wait until it does so.
            self.proc.wait()
            if self.proc.returncode != 0:
                raise subprocess.CalledProcessError(self.proc.returncode, self.args)
        except subprocess.CalledProcessError:
            self.proc = None
            raise

    def __exit__(self, arg1, arg2, arg3):
        if self.proc:
            subprocess.check_call(["pkill", "-xf", re.escape(" ".join(self.args))])

def new_tester_ssh_connection(setup_test_container):
    config_hide = Config()
    config_hide.run.hide = True
    with Connection(host="localhost",
                user=setup_test_container.user,
                port=setup_test_container.port,
                config=config_hide,
                connect_kwargs={
                    "key_filename": setup_test_container.key_filename,
                    "password": "",
                    "timeout": 60,
                    "banner_timeout": 60,
                    "auth_timeout": 60,
                } ) as conn:

        ready = _probe_ssh_connection(conn)

        assert ready, "SSH connection can not be established. Aborting"
        return conn

def wait_for_container_boot(docker_container_id):
    assert docker_container_id is not None
    ready = False
    timeout = time.time() + 60*3
    while not ready and time.time() < timeout:
        time.sleep(5)
        output = subprocess.check_output("docker logs {} 2>&1".format(docker_container_id), shell=True)

        # Check on the last 100 chars only, so that we can detect reboots
        if re.search("(Poky|GNU/Linux).* tty", output.decode("utf-8")[-100:], flags=re.MULTILINE):
            ready = True

    return ready

def _probe_ssh_connection(conn):
    ready = False
    timeout = time.time() + 60
    while not ready and time.time() < timeout:
        try:
            result = conn.run('true', hide=True)
            if result.exited == 0:
                ready = True

        except SSHException as e:
            if not (str(e).endswith("Connection reset by peer") or str(e).endswith("Error reading SSH protocol banner")):
                raise e
            time.sleep(5)

    return ready
