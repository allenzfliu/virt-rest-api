#external imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import libvirt
import sys
from libvirt import virDomain
from sympy import Domain

# my imports
from lib.consts import STATE_TRANSLATION_DICT

# env constants
from config import QEMU_URI,FRONTEND_BASE_URL

app = FastAPI()

origins=["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

def connection():
	return libvirt.open(QEMU_URI)

def retrieve_vm(name:str) -> virDomain:
	try:
		with connection() as qemu:
			try:
				vm = qemu.lookupByName(name)
				if (vm != None):
					# it shouldn't be, but just a final sanity check
					return vm
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
	except HTTPException as e:
		raise(e)	
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

def status_lookup(state:int):
	if (state in STATE_TRANSLATION_DICT):
		return STATE_TRANSLATION_DICT[state]
	return "unknown"

def vm_list(list):
	if (list == None):
		return None;
	out = [];
	for vm in list:
		elem = {"name": vm.name(), "state": status_lookup(vm.state()), "id": vm.ID()}
	return out;

@app.get("/")
# @check_config(ROOT_ENABLE)
def root():
	try:
		with connection() as qemu:
			return {"host": qemu.getHostname()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/host")
# @check_config(HOST_ENABLE)
def root():
	try:
		with connection() as qemu:
			return {"host_data": qemu.getInfo()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vms")
# @check_config(VMS_ENABLE)
def root(type: str | int):
	try:
		with connection() as qemu:
			if (type in ('all', -1)):
				return {"vms": vm_list(qemu.listAllDomains(0))}
			elif (type in ('active', 1)):
				return {"vms": vm_list(qemu.listAllDomains(1))}
			elif (type in ('inactive', 2)):
				return {"vms": vm_list(qemu.listAllDomains(2))}
			else:
				raise HTTPException(status_code=404, detail=f"No such type {type}")
	except HTTPException as e:
		raise e;
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vm_info")
# @check_config(VM_DATA_ENABLE)
def root(name: str):
	try:
		vm = retrieve_vm(name)
		info = vm.info()
		return {"state": info[0],
		  "max_mem": info[1],
		  "cur_mem": info[2],
		  "vcpu": info[3],
		  "cputime": info[4]}
	except HTTPException as e:
		raise(e)	
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

# @app.get("/vm_net")
# # @check_config(VM_NET_ENABLE)
# def root(name: str):
# 	try:
# 		with connection() as qemu:
# 			vm = qemu.lookupByName(name)
# 			return {"info": vm.info()}

@app.get("/vm_xmldesc")
# @check_config(VM_XMLDESC_ENABLE)
def root(name: str):
	try:
		domain = retrieve_vm(name)
		return domain.XMLDesc()
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vm_ip")
# @check_config(VM_XMLDESC_ENABLE)
def root(name: str):
	try:
		with connection() as qemu:
			try:
				domain = qemu.lookupByName(name)
				return {"xml": domain.XMLDesc()}
			except:
				raise HTTPException(status_code=400,detail=f"No VM named {name}")
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vm_viewer")
# @check_config(VM_XMLDESC_ENABLE)
def root(name: str):
	try:
		with connection() as qemu:
			try:
				xml:str = qemu.lookupByName(name).XMLDesc()
				xml_root = ET.fromstring(xml)
				devices = xml_root.find("devices")
				if (devices != None):
					graphics = devices.find("graphics")
					if (graphics != None):
						attribs = graphics.attrib
						if ('type' in attribs and attribs['type'] == 'spice'):
							if ('listen' in attribs and 'port' in attribs):
								return {
									"ip": attribs['listen'],
									"port": attribs['port']}
				# if any of these fail, fallback
				return {"ip":None, "port": None}
			except:
				raise HTTPException(status_code=400,detail=f"No VM named {name}")
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vm_state")
def root(name:str):
	try:
		vm = retrieve_vm(name)
		return {"state": vm.state()}
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vm_status")
def root(name:str|None, state:int|None):
	try:
		if (name != None and state == None):
			vm = retrieve_vm(name)
			return {"status": status_lookup(vm.state())}
		if (state != None and name == None):
			return {"status": status_lookup(state)}
		raise HTTPException(status_code=422)
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.post("/vm_start")
# @check_config(VM_START_ENABLE)
def root(name: str):
	try:
		with connection() as qemu:
			try:
				domain = qemu.lookupByName(name)
				if (domain.isActive() == 1):
					# domain already started, no need to start again
					raise HTTPException(status_code=403, detail=f"VM {name} already started!")
				
				# create starts domain
				domain.create()
				return RedirectResponse(FRONTEND_BASE_URL + "/vm.html?name=" + name, status_code=301)
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
	except HTTPException as e:
		raise(e)
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.post("/vm_stop")
# @check_config(VM_STOP_ENABLE)
def root(name: str):
	try:
		with connection() as qemu:
			try:
				domain = qemu.lookupByName(name)
				domain.destroy()
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
			return RedirectResponse(FRONTEND_BASE_URL + "/vm.html?name=" + name, status_code=301)
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")