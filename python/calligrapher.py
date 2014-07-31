import app
import math

pageWidth = 120
padding = 10
gutter = 5
lcolumnWidth = 10


def prompt():
	return "> "
def banner(char, width=pageWidth):
	return char*(width/len(char))+"\n"
def showHelp():
	helpMenu = [["COMMAND", "DESCRIPTION"],
				["-c, configuration [configuration file]", "set the configuration file, which should be a JSON file that can have the fields ssh, checks, or output"],
				["-i, ip [username ip RSAkey]", "add an IP address to the list of machines to check. This can either be in the format of the IP address, username, and RSA key, or to a json file with the fields 'username', 'ip', and 'rsa'"],
				["-s, settings", "show the current configuration settings"],
				["-ch, check [check1, check2, check3 ...]", "set a list of checks we want to perform. "],
				["-d, destination", "set the filename of the destination where we want to output. "]]
	lcolumnWidth = max(len(r[0]) for r in helpMenu)
	rcolumnWidth = pageWidth - lcolumnWidth - gutter - padding
	output = []
	for row in helpMenu:
		output.append((padding+lcolumnWidth - len(row[0]))*" ")
		output.append(row[0])
		output.append(" "*gutter)
		info = row[1]
		info = [info[i:i+rcolumnWidth] for i in range(0, len(info), rcolumnWidth)]
		output.append(info.pop(0)+"\n")
		for i in info:
			output.append((lcolumnWidth+padding+gutter)*" " + i + "\n")
	return "".join(output)

def printStruct(struct):
	println = ""
	if isinstance(struct, list):
		for e in struct:
			println += " " + printStruct(e)
	elif isinstance(struct, dict):
		for k, v in struct.items():
			println += " " + k + ": " + printStruct(v)
	else:
		println = struct
	return str(println)
def columnify(string, columns=1):
	columnWidth = (pageWidth-(columns-1)*gutter)/columns
	words = string.split(" ")
	curWidth = 0
	curFragment = ""
	partitionedString = []
	for word in words:
		if curWidth+len(word)+1 > columnWidth:
			partitionedString.append(str(curFragment))
			partitionedString.append("\n")
			curFragment = ""
			curWidth = 0
		curFragment += word + " " 
		curWidth += len(word) + 1
	partitionedString.append(curFragment)

	return ''.join(partitionedString)

def outputList(listName, listElements, columns = 1):
	listElements = list(listElements)
	lcolumnWidth = len(listName) + gutter
	formattedList = []
	formattedList.append(listName + " "*gutter)
	formattedList.append(str(listElements.pop(0)) + "\n")
	for element in listElements:
		formattedList.append(lcolumnWidth*" " + str(element) + "\n")

	return " ".join(formattedList)

def outputIP(ips):
	output = []
	ipLabel = "CURRENT MACHINES"
	output.append(" "*(lcolumnWidth + gutter - len(ipLabel)) + ipLabel + "\n")
	if len(ips):
		for ip in ips:
			for key, value in ip.items():
				output.append(str((lcolumnWidth + gutter - len(key))*" " + key + ": " + value + "\n"))	
			output.append("\n")
	else:
		output.append(str((lcolumnWidth + gutter - 2)*" " + "? : ? \n"))
	return "".join(output)

def outputDestination(outFile):
	output = []
	outputLabel = "CURRENT OUTPUT FILE"
	outFile = outFile if outFile != None else "?"	
	output.append(" "*(lcolumnWidth + gutter - len(outputLabel)) + outputLabel + ": " + outFile + "\n")
	output.append("\n")
	return "".join(output)

def outputChecks(checkList):
	output = []
	checkLabel = "CURRENT CHECKS"
	checkVal = printStruct(checkList) if len(checkList) > 0 else "?"
	output.append(" "*(lcolumnWidth + gutter - len(checkLabel)) + checkLabel + ": " + checkVal + "\n")
	output.append("\n")
	return "".join(output)

def outputDesiredSettings(settingsDict):
	output = []
	settingsLabel = "CURRENT SETTINGS CHECKS"
	output.append(" "*(lcolumnWidth + gutter - len(settingsLabel)) + settingsLabel + "\n")
	if len(settingsDict) > 0:
		for key, value in settingsDict.items():
			output.append(str((lcolumnWidth + gutter - len(key))*" " + key + ": " + printStruct(value) + "\n"))	
	else:
		output.append(str((lcolumnWidth + gutter - 2)*" " + "? : ? \n"))		
	return "".join(output)

def configuration(ips=[], output=None, checks = [], settings={}):
	intro = []
	intro.append(banner(". "))
	intro.append("\n")
	intro.append("CURRENT CONFIGURATION\n\n")

	intro.append(outputIP(ips))
	intro.append(outputDestination(output))
	intro.append(outputChecks(checks))
	intro.append(outputDesiredSettings(settings))

	intro.append("\n\n")
	intro.append("Type 'help' for more information. Type 'quit', 'exit', or a CTRL+D to quit.\n")
	intro.append(banner(". "))
	return "".join(intro)

def promptChecks():
	prompt = []
	prompt.append(columnify("List which checks you'd like to run. Separate arguments with commas. Hit [ENTER] to query for all. Known checks are:\n"))
	maxCheckLen = max([len(check) for check in app.coreChecks])
	prompt.append("\t")
	for i in range(len(app.coreChecks)):
		check = app.coreChecks[i]
		prompt.append(check + " "*(maxCheckLen - len(check) + 5))
		if i%5 == 4:
			prompt.append("\n\t")
	prompt.append("\n"*2)
	return "".join(prompt)


def settingsOutput(settingsDict):
	maxIPChars = max([len(ip) for ip in conflicts])
	padding = 5
	labelWidth = 30
	checkWidth = len("found")
	labelWidth = (pageWidth - maxIPChars - 3*padding - checkWidth)/2
	output = []
	

	output.append("\n")			
	output.append("SETTING CONFLICTS\n")
	output.append(banner("-"))
	output.append(" " * (maxIPChars+padding) + "failed"+ padding*" " + "expected" + (labelWidth+padding-len("expected"))*" " + "observed\n")
	for ipAddress, conflictDict in conflicts.items():
		output.append(ipAddress + " "*(maxIPChars - len(ipAddress) + padding) + "\n")
		for conflictName, expectedAndObserved in conflictDict.items():
			println = (maxIPChars-len(conflictName))*" " + conflictName + padding*" "
			println += "X" if not expectedAndObserved["found"] else " "
			println += (checkWidth-1 + padding)*" "

			expectedString = printStruct(expectedAndObserved["expected"])
			expectedString = "ERROR" if len(expectedString) == 0 else expectedString
			expectedString = [expectedString[i:i+labelWidth] for i in range(0, len(expectedString), labelWidth)]
			observedString = printStruct(expectedAndObserved["observed"])
			observedString = "ERROR" if len(observedString) == 0  else observedString
			observedString = [observedString[i:i+labelWidth] for i in range(0, len(observedString), labelWidth)]

			while len(expectedString) > 0 or len(observedString) > 0:
				expStrFrag = expectedString.pop(0) if len(expectedString) > 0 else ""
				obsStrFrag = observedString.pop(0) if len(observedString) > 0 else ""
				println += expStrFrag + (labelWidth + padding - len(expStrFrag))* " " + obsStrFrag + "\n"
				if len(expectedString) > 0 or len(observedString) > 0:
					println += (maxIPChars + padding + checkWidth + padding)*" "

			output.append(str(println)) 
		output.append("\n")
	output.append(banner("-"))

	return "".join(output)

def conflictsOutput(conflicts):

	# FORMATTING YAY
	maxIPChars = max([len(ip) for ip in conflicts])
	padding = 5
	labelWidth = 30
	checkWidth = len("found")
	labelWidth = (pageWidth - maxIPChars - 3*padding - checkWidth)/2
	output = []
	

	output.append("\n")			
	output.append("SETTING CONFLICTS\n")
	output.append(banner("-"))
	output.append(" " * (maxIPChars+padding) + "failed"+ padding*" " + "expected" + (labelWidth+padding-len("expected"))*" " + "observed\n")
	for ipAddress, conflictDict in conflicts.items():
		output.append(ipAddress + " "*(maxIPChars - len(ipAddress) + padding) + "\n")
		for conflictName, expectedAndObserved in conflictDict.items():
			println = (maxIPChars-len(conflictName))*" " + conflictName + padding*" "
			println += "X" if not expectedAndObserved["found"] else " "
			println += (checkWidth-1 + padding)*" "

			expectedString = printStruct(expectedAndObserved["expected"])
			expectedString = "ERROR" if len(expectedString) == 0 else expectedString
			expectedString = [expectedString[i:i+labelWidth] for i in range(0, len(expectedString), labelWidth)]
			observedString = printStruct(expectedAndObserved["observed"])
			observedString = "ERROR" if len(observedString) == 0  else observedString
			observedString = [observedString[i:i+labelWidth] for i in range(0, len(observedString), labelWidth)]

			while len(expectedString) > 0 or len(observedString) > 0:
				expStrFrag = expectedString.pop(0) if len(expectedString) > 0 else ""
				obsStrFrag = observedString.pop(0) if len(observedString) > 0 else ""
				println += expStrFrag + (labelWidth + padding - len(expStrFrag))* " " + obsStrFrag + "\n"
				if len(expectedString) > 0 or len(observedString) > 0:
					println += (maxIPChars + padding + checkWidth + padding)*" "

			output.append(str(println)) 
		output.append("\n")
	output.append(banner("-"))

	return "".join(output)