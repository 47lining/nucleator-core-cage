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

from nucleator.cli.utils import ValidateCustomerAction
from nucleator.cli.command import Command
import argparse, os

class LimitStacksetInstanceAction(argparse.Action):
    def __call__(self,parser,namespace,values,option_string=None):
        limit_stackset = getattr(namespace,'limit_stackset', None)
        if (limit_stackset == None):
            parser.error( "limit-stackset-instance can only be used with prior specification of limit-stackset <stackset_name>")
        else:
            setattr(namespace,self.dest,values)

class Cage(Command):
    
    name = "cage"
    
    def parser_init(self, subparsers):
        """
        Initialize parsers for this command.
        """

        # add parser for cage command
        cage_parser = subparsers.add_parser('cage')
        cage_subparsers=cage_parser.add_subparsers(dest="subcommand")

        # provision subcommand
        cage_provision=cage_subparsers.add_parser('provision', help="provision a new cage")
        cage_provision.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        cage_provision.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        cage_provision.add_argument("--create-bucket", dest='create_bucket', required=False, action='store_true', help="Name of cage from nucleator config")
        cage_provision.add_argument("--no-create-bucket", dest='create_bucket', required=False, action='store_false', help="Name of cage from nucleator config")
        cage_provision.set_defaults(create_bucket=True)

        # configure subcommand
        cage_configure=cage_subparsers.add_parser('configure', help="configure a new cage")
        cage_configure.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        cage_configure.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        cage_configure.add_argument("--limit-stackset", required=False, help="Limit configuration to hosts associated with any instance of specified Stackset")
        cage_configure.add_argument("--limit-stackset-instance", required=False, action=LimitStacksetInstanceAction, help="Limit configuration to hosts associated with specified instance of specified Stackset.  Requires prior specification of --limit-stackset.")
        cage_configure.add_argument("--list-hosts", required=False, action='store_true', help="List entailed hosts and stop, do not configure hosts")
        cage_configure.add_argument("--restart-nat", required=False, action='store_true', help="Stop all NAT instances, then stat them again, prior to configuration")
        cage_configure.set_defaults(list_hosts=False)
        cage_configure.set_defaults(restart_nat=False)

        # delete subcommand
        cage_delete=cage_subparsers.add_parser('delete', help="delete a previously provisioned cage")
        cage_delete.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        cage_delete.add_argument("--cage", required=True, help="Name of cage to delete")

    def provision(self, **kwargs):
        """
        Provisions a Nucleator Cage within specified Account for specified Customer.
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        create_bucket = kwargs.get("create_bucket", None)
        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")
        if create_bucket is None:
            raise ValueError("Internal Error: create_bucket is None but should have been set by parser")
        extra_vars={
            "cage_name": cage,
            "customer_name": customer,
            "create_bucket": create_bucket,
            "verbosity": kwargs.get("verbosity", None),
        }

        extra_vars["cage_deleting"]=kwargs.get("cage_deleting", False)
        
        command_list = []
        command_list.append("account")
        command_list.append("cage")

        cli.obtain_credentials(commands = command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None))
        
        return cli.safe_playbook(self.get_command_playbook("cage_provision.yml"),
                                 is_static=True, # do not use dynamic inventory script, credentials may not be available
                                 **extra_vars
        )
        
    def configure(self, **kwargs):
        """
        Configure instances within a provisioned Cage, potentially including all of 
        its provisioned Stacksets.  Configure instances across all Stacksets, or 
        limit to to specified Stackset types 
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        restart_nat = kwargs.get("restart_nat", False)
        limit_stackset = kwargs.get("limit_stackset", None)
        limit_stackset_instance = kwargs.get("limit_stackset_instance", None)
        list_hosts = kwargs.get("list_hosts", None)
        verbosity = kwargs.get("verbosity", None)

        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")

        extra_vars={
            "cage_name": cage,
            "customer_name": customer,
            "limit_stackset": limit_stackset,
            "limit_stackset_instance": limit_stackset_instance,
            "list_hosts": list_hosts,
            "verbosity": verbosity,
            "restart_nat": restart_nat,
        }

        command_list = []
        command_list.append("cage")

        inventory_manager_rolename = "NucleatorCageInventoryManager"

        cli.obtain_credentials(commands = command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None)) # pushes credentials into environment

        return cli.safe_playbook(
            self.get_command_playbook("cage_configure.yml"),
            inventory_manager_rolename,
            **extra_vars
        )

    def delete(self, **kwargs):
        """
        This command deletes a previously provisioned Nucleator Cage.
        """
        kwargs["cage_deleting"]=True
        return self.provision(**kwargs)
        
# Create the singleton for auto-discovery
command = Cage()
