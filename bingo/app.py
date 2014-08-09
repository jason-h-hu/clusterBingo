#! /usr/bin/python

# The topmost class. This just initializes the frontend and backend. 
from bingo.backend import master
from bingo.frontend import terminalFrontEnd

def main():
	back = master.Backend()
	front = terminalFrontEnd.TerminalFrontEnd()
	back.setFrontend(front)
	front.setBackend(back)

	back.initializeSelf()
	front.start()

if __name__ == '__main__':
	main()