

import sys
import json
from KeyValueFileToVMFClass import KeyValueFileToVMFClass

if len(sys.argv) <= 1 or sys.argv[1] == None:
	print("usage: ./VMF2JSON.py <keyValueFileToImport> <VMFMapTranslationX Y Z> <VMFMapTranslationZaxis>")	
fileName = sys.argv[1]
VMFMapTranslationX = 0.0
VMFMapTranslationY = 0.0
VMFMapTranslationZ = 0.0
VMFMapTranslationZaxis = 0.0

if len(sys.argv) > 2:
	VMFMapTranslationX, VMFMapTranslationY, VMFMapTranslationZ, VMFMapTranslationZaxis = sys.argv[2:]
objTemplate = KeyValueFileToVMFClass(fileName, "importedElem", (
	0.0, 
	0.0, 
	0.0), 0.0)
print (json.dumps(objTemplate.__json__()))
