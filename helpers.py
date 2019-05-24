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
from fabric import Connection

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
