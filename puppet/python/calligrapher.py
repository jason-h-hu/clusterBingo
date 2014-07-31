
pageWidth = 50
padding = 10
gutter = 5
lcolumnWidth = 10
def prompt():
	return "> "

def banner(char, width=pageWidth):
	return char*(width/len(char))+"\n"

def showHelp():
	helpMenu = [["COMMAND", "DESCRIPTION"],
				["-i, ip [username username RSAkey]", "add an IP address to the list of machines to check. "]]
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
