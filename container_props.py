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

class ContainerProps:
    image_name = None
    append_mender_version = None

    device_type = None
    key_filename = None
    user = None
    port = None
    qemu_ip = None

    # Will be set once the container is running
    container_id = None

    def __init__(self, image_name, append_mender_version=False, device_type=None, key_filename=None,
                 user="root", port=8822, qemu_ip="10.0.2.15"):
        self.image_name = image_name
        self.append_mender_version = append_mender_version
        self.device_type = device_type
        self.key_filename = key_filename
        self.user = user
        self.port = port
        self.qemu_ip = qemu_ip

MenderTestRaspbian = ContainerProps(image_name="mendersoftware/mender-test-containers:raspbian_latest",
                                    device_type="raspberrypi3",
                                    key_filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "docker/ssh-keys/key"),
                                    user="pi")
MenderTestQemux86_64 = ContainerProps(image_name="mendersoftware/mender-client-qemu",
                                      append_mender_version=True,
                                      key_filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "docker/ssh-keys/key"))
