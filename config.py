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


URI:str = str(os.getenv("URI"))
FRONTEND_BASE_URL:str = str(os.getenv("FRONTEND_BASE_URL"))