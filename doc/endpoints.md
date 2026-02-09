# Endpoints Documentation

*Additional note*: I don't know where everything comes from. If I say "see the libvirt library", I mean the libvirt Python library which I used to build this API. That library will probably reference the main libvirt library.

# **NOTE**: Please read README.md first.

### GET /
The HTTP root returns a single JSON object with only a single parameter: the name of the hypervisor host.

Output:
```python
{"host": str
    The name of the hypervisor host.
}
```

### GET /host
`/host` returns data about the host hypervisor. This is taken directly from QEMU.

Output:
```json
{"host_data":
    A listing of host data. See documentation for host.getInfo() in libvirt for more information.
}
```

### GET /vms
`/vms` returns a listing of VMs. It requires a single parameter passed through the url, `type`.
There's a bunch of other flags. Flags from 0-65535 inclusive are passed through directly to QEMU. See https://libvirt.org/html/libvirt-libvirt-domain.html#virConnectListAllDomainsFlags for how the rest are handled. Basically it's just a binary addition.

Parameters:
```python
?type= str | int
    1 | 'active' for active virtual machines.
    2 | 'inactive' for inactive virtual machines.
    -1 | 'all' for all virtual machines.
    Ints 0-65535 are passed to QEMU directly.
    Ints <0 or >65535 will raise a 404 error.
    Strings will raise a 404 other than these.
```

Output:
```json
{"vms":
    Array of VM listings.
    [
        Index *:
            {"name": str
                VM Domain Name.
            , "state": str
                VM State. See 
            , "id": int
                VM ID number
            }
    ]
}
```

### GET /vm_info
Returns a listing of some basic information about a virtual machine. Uses https://libvirt.org/html/libvirt-libvirt-domain.html#virDomainInfo.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```json
{"state": int
    State of VMs.
, "max_mem": int
    Maximum memory allocated to this VM in KB.
, "cur_mem: int
    Currrent allocated memory to this VM in KB.
, "vcpu": int
    Number of vCPUs used.
, "cputime": int
    CPU time in ns.
}
```

### GET /vm_ip

Retrieves the IP addresses of a virtual machine.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```json
{"ips": str
    [
        Index *:
            IP address in CIDR notation.
    ]
}
```

### GET /vm_xmldesc
Retrieves the raw XMLdesc of a virtual machine.

***NOTE***: This does not return a json wrapper. The raw XML is returned instead.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```xml
<domain type>
    Domain raw XML.
</domain>
```

### GET /vm_viewer
Retrieves the IP address and viewport of the VM.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```json
{"ip": str
    Listen IP. This will probably be 0.0.0.0 or 127.0.0.1, or null if graphics is not enabled.
, "port": int
    UDP Spice port, or null if graphics is not enabled.
}
```

### GET /vm_state
Retrieves the state of a VM. Uses virDomainState.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```json
{"state": int
    State of VM. Between 0 and 8.
}
```

### GET /vm_status
Retrieves the state of a VM in English. Uses virDomainState. Alternatively, converts a domain state number into English.

Parameters:
```python
    ?name= str | None
        Name of virtual machine.
    ?state= int | None
        VM state number between 0 and 8.
```

Output:
```json
{"state": str
    State of VM. In this list: ["no state", "running", "blocked", "paused", "shutdown", "shutoff", "crashed", "guest suspended", "other"]
}
```

### POST /vm_start
Starts a named VM.

Parameters:
```python
    ?name= str
        Name of virtual machine.
```

Output:
```json
{"status":
    True, if the status is now equal to active, or false otherwise.
}
```

### POST /vm_stop
Same as `/vm_start`, but stops instead of starts.

Parameters:
```python
?name= str
    Name of virtual machine.
```

Output:
```json
{"status":
    True, if the status is now equal to inactive, or false otherwise.
}
```