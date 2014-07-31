#! /usr/bin/python
	
import backend
import frontend
import terminalFrontEnd

back = backend.Backend()
front = terminalFrontEnd.TerminalFrontEnd()
back.setFrontend(front)
front.setBackend(back)

back.initializeSelf()
front.start()