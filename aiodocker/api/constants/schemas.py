from collections import OrderedDict
from .statuses import (
    CREATED,
    RUNNING,
    EXITED,
    PAUSED,
    RESTARTING
)


PORT = '^'

PORT_MAP = {
    'type': 'object',
    'patternProperties': {
        PORT: {
            'type': 'string'
        }
    }
}

STRING_MAP = {
    'type': 'object',
    'patternProperties': {
        '^': {
            'type': 'string'
        }
    }
}

HOST_CONFIG = {
    'type': 'object',
    'properties': {
        'NetworkMode': {
            'type': 'string',
            'default': 'default'
        },
        'Binds': {
            'type': 'array',
            'items': {
                'type': 'string'
            },
        }
    },
    'additionalProperties': False
}


IPAM_CONFIG = {
    'type': 'object',
    'properties': {
        'Subnet': {
            'type': 'string'
        },
        'IPRange': {
            'type': 'string'
        },
        'Gateway': {
            'type': 'string'
        },
        'AuxAddress': {
            'type': 'object',
            'patternProperties': {
                '^': {
                    'type': 'string'
                }
            }
        },
    }
}


CREATE_CONTAINER = {
    'type': 'object',
    'properties': OrderedDict(
        Hostname={
            'type': 'string'
        },
        Domainname={
            'type': 'string'
        },
        User={
            'type': 'string',
            'description': "User that will run the command(s) inside the container",
        },
        AttachStdin={
            'type': 'boolean',
            'description': "Attach the standard input, makes possible user interaction",
        },
        AttachStdout={
            'type': 'boolean',
            'description': "Attach the standard output",
        },
        AttachStderr={
            'type': 'boolean',
            'description': "Attach the standard error",
        },
        ExposedPorts={
            'type': 'object',
            'patternProperties': {
                PORT: {
                    'type': 'object'
                }
            }
        },
        PublishService={
            'type': 'string',
            'description': "Name of the network service exposed by the container",
        },
        Tty={
            'type': 'boolean',
            'description': "Attach standard streams to a tty, including stdin if it is not closed.",
        },
        OpenStdin={
            'type': 'boolean',
            'description': "Open stdin"
        },
        StdinOnce={
            'type': 'boolean',
            'description': "If true, close stdin after the 1 attached client disconnects."
        },
        Env={
            'type': 'array',
            'items': {
                'type': 'string'
            },
            'description': "List of environment variable to set in the container"
        },
        Cmd={
            'type': ['string', 'array'],
            'items': {
                'type': 'string'
            },
            'description': "Command to run when starting the container"
        },
        ArgsEscaped={
            'type': 'boolean',
            'description': "True if command is already escaped (Windows specific)"
        },
        Image={
            'type': 'string',
            'description': "Name of the image as it was passed by the operator (eg. could be symbolic)"
        },
        Volumes={
            'type': 'object',
            'patternProperties': {
                '^': {
                    'type': 'object'
                }
            }
        },
        WorkingDir={
            'type': 'string',
            'description': "Current directory (PWD) in the command will be launched"
        },
        Entrypoint={
            'type': ['string', 'array'],
            'items': {
                'type': 'string'
            },
            'description': "Entrypoint to run when starting the container"
        },
        NetworkDisabled={
            'type': 'boolean',
            'description': "Is network disabled"
        },
        MacAddress={
            'type': 'string',
            'description': "Mac Address of the container"
        },
        OnBuild={
            'type': 'array',
            'items': {
                'type': 'string'
            },
            'description': "ONBUILD metadata that were defined on the image Dockerfile"
        },
        StopSignal={
            'type': 'string',
            'description': "Signal to stop a container"
        },
        Labels=STRING_MAP,
        HostConfig=HOST_CONFIG
    ),
    'additionalProperties': False,
    'required': [
        'Image'
    ]
}


CREATE_NETWORK = {
    'type': 'object',
    'properties': {
        'Name': {
            'type': 'string'
        },
        'Driver': {
            'type': 'string'
        },
        'IPAM': IPAM_CONFIG,
        'Internal': {
            'type': 'boolean'
        },
        'CheckDuplicate': {
            'type': 'boolean'
        },
        'Labels': STRING_MAP,
        'Options': STRING_MAP
    },
    'additionalProperties': False,
    'required': [
        'Name'
    ]
}


CREATE_VOLUME = {
    'type': 'object',
    'properties': {
        'Name': {
            'type': 'string'
        },
        'Driver': {
            'type': 'string'
        },
        'DriverOpts': {
            'type': 'object'
        },
        'Labels': STRING_MAP
    },
    'additionalProperties': False
}
