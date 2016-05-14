import unittest

from nose2.tools.params import params
import json

from asyncio_docker.collections import DataMapping


class DataMappingTestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.data = DataMapping(json.loads(JSON))
    
    def test_init(self):
        DataMapping({})
        DataMapping([('a', 1), ('b', 2)])
        DataMapping([('a', 1), ('b', 2)], c=3)

    @params('HostConfig', 'host_config', 'hostConfig')
    def test_in(self, key):
        self.assertIn(key, self.data)

    @params('hostconfig', 'hoStConfig', 'HOSTCONFIG')
    def test_not_in(self, key):
        self.assertNotIn(key, self.data)

    def test_keys(self):
        self.assertIn('HostConfig', self.data.keys())
        self.assertNotIn('host_config', self.data.keys())

    def test_values(self):
        self.assertIn('devicemapper', self.data.values())

    def test_items(self):
        self.assertIn(('Driver', 'devicemapper'), self.data.items())

    def test_getitem(self):
        self.assertEqual(self.data['Driver'], 'devicemapper')
        self.assertEqual(self.data['driver'], 'devicemapper')
        with self.assertRaises(KeyError):
            self.data['NotFound']

    def test_getattr(self):
        self.assertEqual(self.data.Driver, 'devicemapper')
        self.assertEqual(self.data.driver, 'devicemapper')
        with self.assertRaises(AttributeError):
            self.data.NotFound

    def test_get(self):
        self.assertEqual(self.data.get('Driver'), 'devicemapper')
        self.assertEqual(self.data.get('driver'), 'devicemapper')
        self.assertEqual(self.data.get('NotFound'), None)
        self.assertEqual(self.data.get('NotFound', 1), 1)

    def test_nested(self):
        self.assertIsInstance(self.data['HostConfig'], DataMapping)
        self.assertIsInstance(self.data['HostConfig']['RestartPolicy'], DataMapping)
        self.assertIsInstance(self.data['Mounts'][0], DataMapping)

    def test_equal(self):
        a = DataMapping([('a', 1), ('b', 2)], c=3)
        b = DataMapping([('a', 1), ('c', 3)], b=2)
        c = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(a, b)
        self.assertEqual(a, c)

    def test_raw(self):
        self.assertEqual(self.data.raw, json.loads(JSON))

    def test_raw_loss(self):
        o = {'UpperCase': 1, 'upper_case': 1}
        self.assertNotEqual(DataMapping(o), o)


JSON = """
{
    "AppArmorProfile": "",
    "Args": [
        "-c",
        "exit 9"
    ],
    "Config": {
        "AttachStderr": true,
        "AttachStdin": false,
        "AttachStdout": true,
        "Cmd": [
            "/bin/sh",
            "-c",
            "exit 9"
        ],
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "ExposedPorts": null,
        "Hostname": "ba033ac44011",
        "Image": "ubuntu",
        "Labels": {
            "com.example.vendor": "Acme",
            "com.example.license": "GPL",
            "com.example.version": "1.0"
        },
        "MacAddress": "",
        "NetworkDisabled": false,
        "OnBuild": null,
        "OpenStdin": false,
        "StdinOnce": false,
        "Tty": false,
        "User": "",
        "Volumes": {
            "/volumes/data": {}
        },
        "WorkingDir": "",
        "StopSignal": "SIGTERM"
    },
    "Created": "2015-01-06T15:47:31.485331387Z",
    "Driver": "devicemapper",
    "ExecDriver": "native-0.2",
    "ExecIDs": null,
    "HostConfig": {
        "Binds": null,
        "BlkioWeight": 0,
        "BlkioWeightDevice": [{}],
        "BlkioDeviceReadBps": [{}],
        "BlkioDeviceWriteBps": [{}],
        "BlkioDeviceReadIOps": [{}],
        "BlkioDeviceWriteIOps": [{}],
        "CapAdd": null,
        "CapDrop": null,
        "ContainerIDFile": "",
        "CpusetCpus": "",
        "CpusetMems": "",
        "CpuShares": 0,
        "CpuPeriod": 100000,
        "Devices": [],
        "Dns": null,
        "DnsOptions": null,
        "DnsSearch": null,
        "ExtraHosts": null,
        "IpcMode": "",
        "Links": null,
        "LxcConf": [],
        "Memory": 0,
        "MemorySwap": 0,
        "MemoryReservation": 0,
        "KernelMemory": 0,
        "OomKillDisable": false,
        "OomScoreAdj": 500,
        "NetworkMode": "bridge",
        "PortBindings": {},
        "Privileged": false,
        "ReadonlyRootfs": false,
        "PublishAllPorts": false,
        "RestartPolicy": {
            "MaximumRetryCount": 2,
            "Name": "on-failure"
        },
        "LogConfig": {
            "Config": null,
            "Type": "json-file"
        },
        "SecurityOpt": null,
        "VolumesFrom": null,
        "Ulimits": [{}],
        "VolumeDriver": "",
        "ShmSize": 67108864
    },
    "HostnamePath": "/var/lib/docker/containers/ba033ac4401106a3b513bc9d639eee123ad78ca3616b921167cd74b20e25ed39/hostname",
    "HostsPath": "/var/lib/docker/containers/ba033ac4401106a3b513bc9d639eee123ad78ca3616b921167cd74b20e25ed39/hosts",
    "LogPath": "/var/lib/docker/containers/1eb5fabf5a03807136561b3c00adcd2992b535d624d5e18b6cdc6a6844d9767b/1eb5fabf5a03807136561b3c00adcd2992b535d624d5e18b6cdc6a6844d9767b-json.log",
    "Id": "ba033ac4401106a3b513bc9d639eee123ad78ca3616b921167cd74b20e25ed39",
    "Image": "04c5d3b7b0656168630d3ba35d8889bd0e9caafcaeb3004d2bfbc47e7c5d35d2",
    "MountLabel": "",
    "Name": "/boring_euclid",
    "NetworkSettings": {
        "Bridge": "",
        "SandboxID": "",
        "HairpinMode": false,
        "LinkLocalIPv6Address": "",
        "LinkLocalIPv6PrefixLen": 0,
        "Ports": null,
        "SandboxKey": "",
        "SecondaryIPAddresses": null,
        "SecondaryIPv6Addresses": null,
        "EndpointID": "",
        "Gateway": "",
        "GlobalIPv6Address": "",
        "GlobalIPv6PrefixLen": 0,
        "IPAddress": "",
        "IPPrefixLen": 0,
        "IPv6Gateway": "",
        "MacAddress": "",
        "Networks": {
            "bridge": {
                "NetworkID": "7ea29fc1412292a2d7bba362f9253545fecdfa8ce9a6e37dd10ba8bee7129812",
                "EndpointID": "7587b82f0dada3656fda26588aee72630c6fab1536d36e394b2bfbcf898c971d",
                "Gateway": "172.17.0.1",
                "IPAddress": "172.17.0.2",
                "IPPrefixLen": 16,
                "IPv6Gateway": "",
                "GlobalIPv6Address": "",
                "GlobalIPv6PrefixLen": 0,
                "MacAddress": "02:42:ac:12:00:02"
            }
        }
    },
    "Path": "/bin/sh",
    "ProcessLabel": "",
    "ResolvConfPath": "/var/lib/docker/containers/ba033ac4401106a3b513bc9d639eee123ad78ca3616b921167cd74b20e25ed39/resolv.conf",
    "RestartCount": 1,
    "State": {
        "Error": "",
        "ExitCode": 9,
        "FinishedAt": "2015-01-06T15:47:32.080254511Z",
        "OOMKilled": false,
        "Dead": false,
        "Paused": false,
        "Pid": 0,
        "Restarting": false,
        "Running": true,
        "StartedAt": "2015-01-06T15:47:32.072697474Z",
        "Status": "running"
    },
    "Mounts": [
        {
            "Name": "fac362...80535",
            "Source": "/data",
            "Destination": "/data",
            "Driver": "local",
            "Mode": "ro,Z",
            "RW": false,
            "Propagation": ""
        }
    ]
}
"""
