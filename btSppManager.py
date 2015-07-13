#!/usr/bin/python
# coding: UTF-8

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import os
import sys
import socket
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import time
import threading

class Profile(dbus.service.Object):

	fd = -1

	def setRecv(self,fnc):
		self.setCallbackRecv = fnc

	def setWrite(self,fnc):
		self.setCallbackWrite = fnc

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Release(self):
		print("Release")
		mainloop.quit()

	@dbus.service.method("org.bluez.Profile1",
					in_signature="", out_signature="")
	def Cancel(self):
		print("Cancel")

	@dbus.service.method("org.bluez.Profile1",
				in_signature="oha{sv}", out_signature="")
	def NewConnection(self, path, fd, properties):

		self.fd = fd.take()
		print("ConnectData(%s, %d)" % (path, self.fd))

		server_sock = socket.fromfd(self.fd, socket.AF_UNIX, socket.SOCK_STREAM)
		server_sock.setblocking(1)

		print ("enter_recv_loop")
		msg = None

		try:
			msg = self.setCallbackWrite()
		except:
			pass

		if msg is not None:
			server_sock.send(str(msg))
			print ("Write data : %s" % msg)
			msg = None

		try :
			while True:
				recvdata = server_sock.recv(1024)
				if recvdata is not None:

					try:
						self.setCallbackRecv(recvdata)
					except:
						pass

		except IOError:
			pass

		server_sock.close()
		print("all done")

	@dbus.service.method("org.bluez.Profile1",
				in_signature="o", out_signature="")
	def RequestDisconnection(self, path):
		print("RequestDisconnection(%s)" % (path))

		if (self.fd > 0):
			os.close(self.fd)
			self.fd = -1


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()

manager = dbus.Interface(bus.get_object("org.bluez",
			"/org/bluez"), "org.bluez.ProfileManager1")

option_list = [
		make_option("-C", "--channel", action="store",
				type="int", dest="channel",
				default=None),
		]

parser = OptionParser(option_list=option_list)

(options, args) = parser.parse_args()

options.uuid = "1101"
options.psm = "3"
options.role = "server"
options.name = "Edison SPP Loopback"
options.service = "spp char loopback"
options.path = "/foo/bar/profile"
options.auto_connect = False
options.record = ""

profile = Profile(bus, options.path)

def setRecvHandler(func):
	profile.setRecv(func)

def setWriteHandler(func):
	profile.setWrite(func)

opts = {
		"AutoConnect" :	options.auto_connect,
	}

if (options.name):
	opts["Name"] = options.name

if (options.role):
	opts["Role"] = options.role

if (options.psm is not None):
	opts["PSM"] = dbus.UInt16(options.psm)

if (options.channel is not None):
	opts["Channel"] = dbus.UInt16(options.channel)

if (options.record):
	opts["ServiceRecord"] = options.record

if (options.service):
	opts["Service"] = options.service

if not options.uuid:
	options.uuid = str(uuid.uuid4())

manager.RegisterProfile(options.path, options.uuid, opts)
