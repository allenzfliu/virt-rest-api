# Endpoints Documentation

*Additional note*: I don't know where everything comes from. If I say see the libvirt library, I mean the libvirt Python library which I used to build this API.

# **NOTE**: Please read README.md first.

### GET /
The HTTP root returns a single JSON object with only a single parameter: the name of the hypervisor host.

Output:
    
    {"host":
        The name of the hypervisor host.
    }

### GET /host
`/host` returns data about the host hypervisor. This is taken directly from QEMU.

Output:

    {"host_data":
        A listing of host data. See documentation for host.getInfo() in libvirt for more information.
    }

### GET /vms
`/vms` returns a listing of VMs. It requires a single parameter passed through the url, `type`.

Parameters:

    ?type=
        'active' for active virtual machines.
        'inactive' for inactive virtual machines.
        'all' for all virtual machines.

Output:

    {"vms":
        Array of VM listings. Taken directly from QEMU.
        [
            See documentation for .listAllDomains() in libvirt for output information.
        ]
    }

### GET /vm_info
Returns a listing of some basic information about a virtual machine. I haven't figured out what all the numbers mean, but I believe I've figured out some of them.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    {"info":
        Info listing. See documentation for vm.info() in libvirt for more information.
        [
            Index 0: integer
                VM status integer. 5 means inactive, 1 means active.
            Index 1: integer
                I'm still not sure, but I think it means Max memory.
            Index 2: integer
                I'm still not sure, but I think it means min memory.
            Index 3: integer
                I'm fairly sure this is vcpus used.
            Index 4: integer
                I still have no idea what this one means.
        ]
    }

### GET /vm_ip

Retrieves the IP addresses of a virtual machine.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    {"ips":
        IP addresses in CIDR notation.
        [
            Index *:
                IP address in CIDR notation.
        ]
    }

### GET /vm_xmldesc
Retrieves the raw XMLdesc of a virtual machine.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    <domain type>
        Domain raw XML.
    </domain type>

### GET /vm_viewer
Retrieves the IP address and viewport of the VM.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    {
        "ip":
            Listen IP. This will probably be 0.0.0.0 or 127.0.0.1.
        "port":
            UDP Spice port.
    }

### POST /vm_start
Starts a named VM.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    {"status":
        True, if the status is now equal to active, or false otherwise.
    }

### POST /vm_stop
Same as `/vm_start`, but stops instead of starts.

Parameters:

    ?name=
        Name of virtual machine.

Output:

    {"status":
        True, if the status is now equal to inactive, or false otherwise.
    }