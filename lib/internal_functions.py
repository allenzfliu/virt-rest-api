from lib.consts import STATE_TRANSLATION_DICT

# this file is pretty much for basic logic

def status_lookup(state:int):
	if (state in STATE_TRANSLATION_DICT):
		return STATE_TRANSLATION_DICT[state]
	return "unknown"