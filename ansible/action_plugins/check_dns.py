# Copyright 2015 47Lining LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.runner.return_data import ReturnData
from ansible.utils import parse_kv
import socket


class ActionModule(object):
    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

        args = {}
        if complex_args:
            args.update(complex_args)
        args.update(parse_kv(module_args))
        
        hostname = args.get("hostname")
        failed = True
        try:
            r = socket.gethostbyname(hostname)
            failed = False
        except socket.error, ex:
            pass

        message = "Succesfully resolved bastion host: %s" % hostname
        if failed:
            message = "Failed to resolve bastion hostname: %s. Please check your DNS server and ensure "  % hostname + \
                      "that records exist for the domains in the hosted zones that were created with the " + \
                      "nucleator cage provision command."

        return ReturnData(conn=conn,
                          comm_ok=True,
                          result=dict(failed=failed, changed=False, msg=message))
