from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import libvirt

# env constants
from config import URI,FRONTEND_BASE_URL
# from config import ROOT_ENABLE,VMS_ENABLE,HOST_ENABLE,VM_DATA_ENABLE,VM_NET_ENABLE,VM_XMLDESC_ENABLE,VM_START_ENABLE,VM_STOP_ENABLE
# print(URI)

# from lib.config_manager import check_config

app = FastAPI()

origins=["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )



def connection():
	return libvirt.open(URI)

def vm_stats(vm):
	if (vm == None):
		return None;
	out = {"name": vm.name(), "state": vm.state(), "id": vm.ID(), "status": "uninitialized"}
	match vm.state()[0]:
		case 1:
			out["status"] = "active"
		case 5:
			out["status"] = "inactive"
		case _:
			out["status"] = "unknown"
	return out;

def vm_list(list):
	if (list == None):
		return None;
	out = [];
	for vm in list:
		out.append(vm_stats(vm))
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
def root(type: str):
	try:
		with connection() as qemu:
			match type:
				case 'all':
					return {"vms": vm_list(qemu.listAllDomains(0))}
				case 'active':
					return {"vms": vm_list(qemu.listAllDomains(1))}
				case 'inactive':
					return {"vms": vm_list(qemu.listAllDomains(2))}
				case _:
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
		with connection() as qemu:
			try:
				vm = qemu.lookupByName(name)
				return {"info": vm.info()}
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
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