import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import shutil
import unittest
from app import EC2ReservedInstanceSimulator

class TestApp(unittest.TestCase):
    def setUp(self):
        pass

    def test_set_ec2(self):
        simulator = EC2ReservedInstanceSimulator()
        self.assertListEqual(simulator.ec2_instances, [])
        simulator.set_ec2([])
        self.assertIsNotNone(simulator.ec2_instances)

    def test_set_ri(self):
        simulator = EC2ReservedInstanceSimulator()
        self.assertListEqual([], simulator.reserved_instances)
        simulator.set_ri([])
        self.assertIsNotNone(simulator.reserved_instances)

    def test_instancecount_is_1_after_apply_ri(self):
        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        ri['InstanceCount'] = 2

        simulator = EC2ReservedInstanceSimulator()
        simulator.set_ri([ri])
        simulator.apply_ri(ri)

        result = simulator.reserved_instances[0]
        self.assertEqual(1, result['InstanceCount'])

    def test_instances_is_empty_after_apply_ri(self):
        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        ri['InstanceCount'] = 1

        simulator = EC2ReservedInstanceSimulator()
        simulator.set_ri([ri])
        simulator.apply_ri(ri)

        self.assertListEqual([], simulator.reserved_instances)

    def test_instances_not_change_after_apply_ri(self):
        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        ri['InstanceCount'] = 1

        another_ri = {'InstanceType': 'm1.large', 'ProductDescription': 'Linux/UNIX'}
        another_ri['InstanceCount'] = 1

        simulator = EC2ReservedInstanceSimulator()
        simulator.set_ri([ri])
        simulator.apply_ri(another_ri)

        result = simulator.reserved_instances[0]
        self.assertEqual(1, result['InstanceCount'])
        self.assertEqual('t1.micro', result['InstanceType'])

class TestSimulator(unittest.TestCase):
    def setUp(self):
        pass

    def test_match_by_instance_state(self):
        ec2 = {'State': {'Name': 'running'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_instance_state(ec2, ri)
        self.assertEqual(ri, result)

    def test_match_by_instance_is_stopped(self):
        ec2 = {'State': {'Name': 'stopped'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_instance_state(ec2, ri)
        self.assertIsNone(result)

    def test_match_by_instance_type(self):
        ec2 = {'InstanceType': 't1.micro', 'State': {'Name': 'running'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_instance_type(ec2, ri)
        self.assertEqual(ri, result)

    def test_match_by_instance_type_not_match(self):
        ec2 = {'InstanceType': 'm1.large', 'State': {'Name': 'running'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_instance_type(ec2, ri)
        self.assertIsNone(result)

    def test_match_by_platform(self):
        ec2 = {'InstanceType': 't1.micro', 'Platform': 'Linux/UNIX', 'State': {'Name': 'running'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_platform(ec2, ri)
        self.assertEqual(ri, result)

    def test_match_by_platform_not_match(self):
        ec2 = {'InstanceType': 't1.micro', 'Platform': 'Windows', 'State': {'Name': 'running'}}

        ri = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX'}
        simulator = EC2ReservedInstanceSimulator()

        result = simulator.match_by_platform(ec2, ri)
        self.assertIsNone(result)

    def test_list_match_ec2(self):
        simulator = EC2ReservedInstanceSimulator()
        result = simulator.list_match_ec2()
        self.assertListEqual([], result)

    def test_list_unmatch_ec2(self):
        simulator = EC2ReservedInstanceSimulator()
        result = simulator.list_unmatch_ec2()
        self.assertListEqual([], result)

    def test_list_unmatch_ri(self):
        simulator = EC2ReservedInstanceSimulator()
        result = simulator.list_unmatch_ri()
        self.assertListEqual([], result)

    def test_simulate(self):
        ec2_1 = {'Name': 'Srv1', 'InstanceType': 't1.micro', 'Platform': 'Linux/UNIX', 'State': {'Name': 'running'}}
        ec2_2 = {'Name': 'Srv2', 'InstanceType': 'r3.large', 'Platform': 'Linux/UNIX', 'State': {'Name': 'running'}}

        ri1 = {'InstanceType': 't1.micro', 'ProductDescription': 'Linux/UNIX', 'InstanceCount': 2}

        simulator = EC2ReservedInstanceSimulator()
        simulator.set_ec2([ec2_1, ec2_2])
        simulator.set_ri([ri1])
        simulator.simulate()

        match_ec2 = simulator.list_match_ec2()
        self.assertEquals('t1.micro', match_ec2[0]['InstanceType'])
        self.assertEquals('Linux/UNIX', match_ec2[0]['Platform'])

        unmatch_ec2 = simulator.list_unmatch_ec2()
        self.assertEquals('r3.large', unmatch_ec2[0]['InstanceType'])
        self.assertEquals('Linux/UNIX', unmatch_ec2[0]['Platform'])

        unmatch_ri = simulator.list_unmatch_ri()
        self.assertEquals('t1.micro', unmatch_ri[0]['InstanceType'])
        self.assertEquals('Linux/UNIX', unmatch_ri[0]['ProductDescription'])
        self.assertEquals(1, unmatch_ri[0]['InstanceCount'])


if __name__ == '__main__':
    unittest.main()
