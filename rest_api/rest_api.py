#external imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import xml.etree.ElementTree as ET
import libvirt
import sys
from libvirt import virDomain
from sympy import Domain

# my imports
from lib import internal_functions;

# env constants
from config import QEMU_URI,FRONTEND_BASE_URL

app = FastAPI()

origins=["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

def connection():
	return libvirt.open(QEMU_URI)

def retrieve_vm(name:str) -> virDomain: # type: ignore
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
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

def vm_list(list):
	if (list == None):
		return None;
	out = [];
	for vm in list:
		elem = {"name": vm.name(), "state": internal_functions.status_lookup(vm.state()[0]), "id": vm.ID()}
		out.append(elem)
	return out;

@app.get("/")
# @check_config(ROOT_ENABLE)
def root():
	try:
		with connection() as qemu:
			return {"host": qemu.getHostname()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.get("/host")
# @check_config(HOST_ENABLE)
def host():
	try:
		with connection() as qemu:
			return {"host_data": qemu.getInfo()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.get("/vms")
# @check_config(VMS_ENABLE)
def vms(type: str | int):
	try:
		with connection() as qemu:
			print(type)
			if (type in ('all', '0', 0)):
				return {"vms": vm_list(qemu.listAllDomains(0))}
			elif (type in ('active', '1', 1)):
				return {"vms": vm_list(qemu.listAllDomains(1))}
			elif (type in ('inactive', '2', 2)):
				return {"vms": vm_list(qemu.listAllDomains(2))}
			else:
				raise HTTPException(status_code=404, detail=f"No such type {type}")
	except HTTPException as e:
		raise e;
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500)

@app.get("/vm_info")
# @check_config(VM_DATA_ENABLE)
def vm_info(name: str):
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
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

# @app.get("/vm_net")
# # @check_config(VM_NET_ENABLE)
# def root(name: str):
# 	try:
# 		with connection() as qemu:
# 			vm = qemu.lookupByName(name)
# 			return {"info": vm.info()}

@app.get("/vm_xmldesc")
# @check_config(VM_XMLDESC_ENABLE)
def vm_xmldesc(name: str):
	try:
		domain = retrieve_vm(name)
		return {"xml": domain.XMLDesc()}
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

# @app.get("/vm_ip")
# # @check_config(VM_XMLDESC_ENABLE)
# def vm_ip(name: str):
# 	try:
# 		with connection() as qemu:
# 			try:
# 				domain = qemu.lookupByName(name)
# 				return {"xml": domain.XMLDesc()}
# 			except:
# 				raise HTTPException(status_code=400,detail=f"No VM named {name}")
# 	except HTTPException as e:
# 		raise e
# 	except Exception as e:
# 		print(e);
# 		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.get("/vm_viewer")
# @check_config(VM_XMLDESC_ENABLE)
def vm_viewer(name: str):
	try:
		with connection() as qemu:
			try:
				# there's not a good option besides just hunting up the XML description.
				# so that is what i do
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
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.get("/vm_state")
def vm_state(name:str):
	try:
		vm = retrieve_vm(name)
		return {"state": vm.state()}
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.get("/vm_status_lookup")
def vm_status_lookup(state:int|None):
	try:
		if (state != None):
			return {"vm_status": internal_functions.status_lookup(state), 
		   		"is_running": internal_functions.status_lookup(state) == "running"}
		raise HTTPException(status_code=422)
	except HTTPException as e:
		raise e
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.post("/vm_start")
# @check_config(VM_START_ENABLE)
def vm_start(name: str):
	try:
		with connection() as qemu:
			try:
				domain = qemu.lookupByName(name)
				if (domain.isActive() == 1):
					# domain already started, no need to start again
					raise HTTPException(status_code=403, detail=f"VM {name} already started!")
				
				# create starts domain
				domain.create()
				return RedirectResponse(FRONTEND_BASE_URL + "vm.html?name=" + name, status_code=301)
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
	except HTTPException as e:
		raise(e)
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

@app.post("/vm_stop")
# @check_config(VM_STOP_ENABLE)
def vm_stop(name: str):
	try:
		with connection() as qemu:
			try:
				domain = qemu.lookupByName(name)
				domain.destroy()
			except:
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
			return RedirectResponse(FRONTEND_BASE_URL + "vm.html?name=" + name, status_code=301)
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")

# mostly generated by chatgpt, but with a lot of work attached
@app.get("/vm_screenshot")
def vm_screenshot(name: str):
	try:
		with connection() as qemu:
			try:
				def receive_stream(stream):
					def receiver(stream, in_buffer, out_buffer):
						out_buffer.extend(buffer)
						return 0;
					buffer = bytearray();
					stream.recvAll(receiver, buffer)
					return buffer;
				vm = qemu.lookupByName(name)
				stream = qemu.newStream()
				mime_type = vm.screenshot(stream, 0, 0);
				data = bytearray()
				receive_stream(stream)
				stream.finish();
				return Response(content=bytes(data), media_type=mime_type)
			except Exception as e:
				print(e);
				raise HTTPException(status_code=400, detail=f"No VM named {name}")
	except HTTPException as e:
		raise(e)
	except Exception as e:
		print("Exception caught: " + str(e));
		raise HTTPException(status_code=500, detail=f"Internyal Server Error")
