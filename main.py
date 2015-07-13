#!/usr/bin/python
# coding: UTF-8

import socket
from btSppManager import setRecvHandler,setWriteHandler
import time
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

TCP_IP = '127.0.0.1'
TCP_PORT = 3000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print("Arduino connection address(%s:%d)" % (TCP_IP, TCP_PORT))

def onReciveData(data):
	print("recved data : %s" % data)
	s.send(data)

def writeData():
	msg = "send massage"
	return msg

if __name__ == '__main__':
	
	setRecvHandler( onReciveData )
	setWriteHandler( writeData )

	mainloop = GObject.MainLoop()
	mainloop.run()