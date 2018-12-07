#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import json
import pprint

pp = pprint.PrettyPrinter(indent=1, width=120, compact=True)
ec2 = boto3.client('ec2')

class EC2ReservedInstanceMatcher:
    def __init__(self):
        self.ec2_instances = []
        self.reserved_instances = []
        self.match_ec2 = []
        self.unmatch_ec2 = []
        self.unmatch_ri = []

    def set_ec2(self, ec2_instances):
        self.ec2_instances = ec2_instances

    def set_ri(self, reserved_instances):
        self.reserved_instances = reserved_instances

    def apply_ri(self, match_ri):
        i = 0
        while True:
            ri = self.reserved_instances[i]
            if ri is None:
                return
            if ri == match_ri:
                ri['InstanceCount'] -= 1
                if ri['InstanceCount'] == 0:
                    del self.reserved_instances[i]
                break
            i += 1

    def match(self):
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
        if type(ri_instances) is not list:
            ri_instances = [ri_instances]

        if instance['State']['Name'] == 'running':
            return ri_instances

    def match_by_instance_type(self, instance, ri_instances):
        if type(ri_instances) is not list:
            ri_instances = [ri_instances]

        for r in ri_instances:
            if r is None:
                break
            if r['InstanceType'] == instance['InstanceType']:
                return r

    def match_by_platform(self, instance, ri_instances):
        if type(ri_instances) != 'array':
            ri_instances = [ri_instances]

        for r in ri_instances:
            if r is None:
                break
            if r['ProductDescription'].upper() == instance['Platform'].upper():
                return r

    def list_match_ec2(self):
        return sorted(self.match_ec2,
                key=lambda k: k['Platform']+k['InstanceType']+k['Name'])

    def list_unmatch_ec2(self):
        return sorted(self.unmatch_ec2,
                key=lambda k: k['Platform']+k['InstanceType']+k['Name'])

    def list_unmatch_ri(self):
        return self.unmatch_ri

def __dump_list(l):
    pp.pprint(l)

def list_ri():
    filters = [{ 'Name': 'state', 'Values': ['active'] }]
    response = ec2.describe_reserved_instances(Filters = filters)

    l = response['ReservedInstances']
    for r in l:
        r['ProductDescription'] = r.get('ProductDescription', 'Linux/UNIX')
    return l


def list_ec2():
    filters = [] #[{ 'Name': 'instance-state-name', 'Values': ['running']}]
    response = ec2.describe_instances(Filters = filters)

    l = []
    for r in response['Reservations']:
        l += r['Instances']

    for r in l:
        name_tag = [x['Value'] for x in r['Tags'] if x['Key'] == 'Name']
        name = name_tag[0] if len(name_tag) else ''
        r['Name'] = name

        r['Platform'] = r.get('Platform', 'Linux/UNIX').capitalize()

    l = sorted(l, key=lambda k: k['State']['Code']+k['LaunchTime'].timestamp())
    return l

def handler(event, context):
    ri_instances = list_ri()
    ec2_instances = list_ec2()

    matcher = EC2ReservedInstanceMatcher()
    matcher.set_ec2(ec2_instances)
    matcher.set_ri(ri_instances)
    matcher.match()

    print("=== RI適用済インスタンス ===")
    for i in matcher.list_match_ec2():
        print("{Name:20s} {InstanceType:12s} {Platform:10s} {InstanceId:20s} {State}".format(
            InstanceId=i['InstanceId'],
            InstanceType=i['InstanceType'],
            Platform=i['Platform'],
            Name=i['Name'],
            State=i['State']['Name'] if i['State']['Name'] != 'running' else '',
        ))

    print("=== RI未適用インスタンス ===")
    for i in matcher.list_unmatch_ec2():
        print("{Name:20s} {InstanceType:12s} {Platform:10s} {InstanceId:20s} {State}".format(
            InstanceId=i['InstanceId'],
            InstanceType=i['InstanceType'],
            Platform=i['Platform'],
            Name=i['Name'],
            State=i['State']['Name'] if i['State']['Name'] != 'running' else '',
        ))

    print("=== 余分RI ===")
    for i in matcher.list_unmatch_ri():
        #__dump_list(i)
        print("{Name:20s} {InstanceType:12s} {Platform:10s} {OfferingClass:12s} {Quantity:3d} {End}".format(
            Name='',
            InstanceType=i['InstanceType'],
            Platform=i['ProductDescription'],
            OfferingClass=i['OfferingClass'],
            Quantity=i['InstanceCount'],
            End=i['End'],
        ))

if __name__ == "__main__":
    handler({}, {})
