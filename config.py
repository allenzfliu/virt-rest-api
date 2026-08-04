import os

# adding config vars
# these don't currently do anything! except make it compile properly
# because i gave up :<
ROOT_ENABLE = True
VMS_ENABLE = False
HOST_ENABLE = 404
VM_DATA_ENABLE = True
VM_NET_ENABLE = True
VM_XMLDESC_ENABLE = 418
VM_START_ENABLE = True
VM_STOP_ENABLE = True


# QEMU_URI:str = str(os.getenv("QEMU_URI"))
QEMU_URI:str = "qemu+ssh://chen@192.168.9.1/system"
FRONTEND_BASE_URL:str = str(os.getenv("FRONTEND_BASE_URL"))