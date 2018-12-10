#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EC2 reserved instances applied simulator
"""

import boto3
import pprint
from simulator import EC2ReservedInstanceSimulator

pp = pprint.PrettyPrinter(indent=1, width=120, compact=True)
ec2 = boto3.client('ec2')


def __dump_list(l):
    pp.pprint(l)


def list_ri():
    """
    gather reserved instances.
    """
    filters = [{'Name': 'state', 'Values': ['active']}]
    response = ec2.describe_reserved_instances(Filters=filters)

    # if ProductDescription is empty set as Linux/UNIX
    lst = response['ReservedInstances']
    return lst


def list_ec2():
    """
    gather ec2 instances.
    """
    filters = []
    response = ec2.describe_instances(Filters=filters)

    lst = []
    for r in response['Reservations']:
        lst += r['Instances']

    return lst


def handler(event, context):
    """
    lambda handler function
    """
    ri_instances = list_ri()
    ec2_instances = list_ec2()

    simulator = EC2ReservedInstanceSimulator()
    simulator.set_ec2(ec2_instances)
    simulator.set_ri(ri_instances)
    simulator.simulate()

    print("=== RI covered instances ===")
    for i in simulator.list_match_ec2():
        print("{Name:20s} {InstanceType:12s} {Platform:10s} {InstanceId:20s} {State}".format(
            InstanceId=i['InstanceId'],
            InstanceType=i['InstanceType'],
            Platform=i['Platform'],
            Name=i['Name'],
            State=i['State']['Name'] if i['State']['Name'] != 'running' else '',
        ))

    print("=== RI *NOT* covered instances ===")
    for i in simulator.list_unmatch_ec2():
        print("{Name:20s} {InstanceType:12s} {Platform:10s} {InstanceId:20s} {State}".format(
            InstanceId=i['InstanceId'],
            InstanceType=i['InstanceType'],
            Platform=i['Platform'],
            Name=i['Name'],
            State=i['State']['Name'] if i['State']['Name'] != 'running' else '',
        ))

    print("=== Purchased but not applied RI ===")
    for i in simulator.list_unmatch_ri():
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
