#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EC2 reserved instances applied simulator
"""

import boto3
import pprint

pp = pprint.PrettyPrinter(indent=1, width=120, compact=True)
ec2 = boto3.client('ec2')


class EC2ReservedInstanceSimulator:
    """
    Applied Simulator

    1. set_ec2
    2. set_ri
    3. simulate
    4. list_(un)match_ec2 or ri
    """
    def __init__(self):
        self.ec2_instances = []
        self.reserved_instances = []
        self.match_ec2 = []
        self.unmatch_ec2 = []
        self.unmatch_ri = []

    def set_ec2(self, ec2_instances):
        """
        set ec2 instances
        """
        lst = ec2_instances
        # Set Name attribute from "Name" tag value
        # if Platform is empty set as Linux/UNIX
        for r in lst:
            if 'Tags' in r and 'Name' in r['Tags']:
                name_tag = [x['Value'] for x in r['Tags'] if x['Key'] == 'Name']
                name = name_tag[0] if len(name_tag) else ''
                r['Name'] = name

            # if "Platform" is empty set "Linux/UNIX"
            # else convert "windows" to "Windows"
            r['Platform'] = r['Platform'].capitalize() or 'Linux/UNIX'

        lst = sorted(lst, key=lambda k: k['State']['Code']+k['LaunchTime'].timestamp())
        self.ec2_instances = lst

    def set_ri(self, reserved_instances):
        """
        set ec2 reserved instances
        """
        self.reserved_instances = reserved_instances

    def apply_ri(self, match_ri):
        """
        Subtract RI count
        When ri count to be 0 then delete the instance item.
        """
        for i, ri in enumerate(self.reserved_instances):
            if ri == match_ri:
                ri['InstanceCount'] -= 1
                if ri['InstanceCount'] == 0:
                    del self.reserved_instances[i]

    def simulate(self):
        """
        Simulate instance applied

        applied when
        - EC2 instance is running
        - Same instance type
        - Same platform
        """
        while len(self.ec2_instances) > 0:
            i = self.ec2_instances.pop(0)

            ri = self.match_by_instance_state(i, self.reserved_instances)
            ri = self.match_by_instance_type(i, ri)
            ri = self.match_by_platform(i, ri)
            if ri:
                self.match_ec2.append(i)
                self.apply_ri(ri)
            else:
                self.unmatch_ec2.append(i)

        self.unmatch_ri = self.reserved_instances

    def match_by_instance_state(self, instance, ri_instances):
        """
        return ri instances when target ec2 state is runnning
        """
        if instance['State']['Name'] == 'running':
            return ri_instances

    def match_by_instance_type(self, instance, ri_instances):
        """
        return ri instance that instance type is same for target ec2
        """
        if type(ri_instances) is not list:
            ri_instances = [ri_instances]

        for r in ri_instances:
            if r is None:
                break
            if r['InstanceType'] == instance['InstanceType']:
                return r

    def match_by_platform(self, instance, ri_instances):
        """
        return ri instance that platform is same for target ec2
        """
        if type(ri_instances) != 'array':
            ri_instances = [ri_instances]

        for r in ri_instances:
            if r is None:
                break
            if r['ProductDescription'].upper() == instance['Platform'].upper():
                return r

    def list_match_ec2(self):
        """
        return matched ec2 instances.
        CALL after "simulate"
        """
        return sorted(self.match_ec2, key=lambda k: k['Platform']+k['InstanceType']+k['Name'])

    def list_unmatch_ec2(self):
        """
        return not matched ec2 instances.
        CALL after "simulate"
        """
        return sorted(self.unmatch_ec2, key=lambda k: k['Platform']+k['InstanceType']+k['Name'])

    def list_unmatch_ri(self):
        """
        return not matched but purchased reserved instances.
        CALL after "simulate"
        """
        return self.unmatch_ri
