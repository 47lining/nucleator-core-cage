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
import subprocess

from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        result = super(ActionModule, self).run(tmp, task_vars)

        args = {}
        if complex_args:
            args.update(complex_args)
        args.update(parse_kv(module_args))

        hostname = args.get("hostname", "null")
        key_path = args.get("key_path", "null")
        failed = True

        command = 'ssh -i %s -q -o "StrictHostKeyChecking=no" -o "BatchMode=yes" ec2-user@%s "echo 2>&1" && echo "UP" || echo "DOWN"' % (key_path, hostname)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        failed = False
        if output.find("UP") < 0:
            failed = True

        message = "Successfully tested SSH connectivity to %s" % hostname
        if failed:
            message = "Failed to successfully connect via SSH to %s. Please check your SSH configuration." % hostname

        result['failed']=failed
        result['changed']=False
        result['msg']=message
        return result
