from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import libvirt
import os

# env constants
from config import URI,FRONTEND_BASE_URL

app = FastAPI()

origins=["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )



def connection():
	return libvirt.open(URI)

def vm_stats(vm):
	if (vm == None):
		return None;
	out = {"name": vm.name(), "state": vm.state(), "id": vm.ID(), "status": "unitiialized"}
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
def root():
	try:
		with connection() as qemu:
			return {"host": qemu.getHostname()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/host")
def root():
	try:
		with connection() as qemu:
			return {"hostname": qemu.getInfo()}
	except Exception as e:
		print(e);
		raise HTTPException(status_code=500, detail=f"Internal Server Error")

@app.get("/vms")
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

@app.post("/vm_start")
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