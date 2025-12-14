Hello! This is a small repo for my libvirt REST API. It features some incredibly barebones monitoring. For now, all it can really do is list running VMs and their statuses, as well as turn them on or off.

If you're trying to run this app, please use `uvicorn`. The command I use is `uvicorn main:app --reload --host 0.0.0.0 --env-file .env"`.