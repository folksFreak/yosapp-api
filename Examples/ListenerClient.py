'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import datetime, sys

if sys.version_info >= (3, 0):
	raw_input = input

from Yowsup.connectionmanager import YowsupConnectionManager

class WhatsappListenerClient:	

	def __init__(self, keepAlive = False, sendReceipts = False):
		self.messages = ''
		self.hold_call = True
		self.connect_Status = ''
		self.sendReceipts = sendReceipts
		
		connectionManager = YowsupConnectionManager()
		connectionManager.setAutoPong(keepAlive)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		self.cm = connectionManager
	
	def disconnect(self, reason):
		self.cm.readerThread.sendDisconnected(reason)
		#print("Sent disconnnected")

	def getMessages(self):
		return self.messages

	def login(self, username, password):
		self.username = username
		self.methodsInterface.call("auth_login", (username, password))

		while self.hold_call:
			i=0

		return self.connect_Status

	def onAuthSuccess(self, username):
		self.connect_Status = "SUCCESS"
		self.methodsInterface.call("ready")
		self.hold_call = False
		#print("Authed %s" % username)		

	def onAuthFailed(self, username, err):
		self.connect_Status = "FAIL"
		self.hold_call = False		
		#print("Auth Failed!")

	def onDisconnected(self, reason):
		self.connect_Status = "FAIL"
		self.hold_call = False
		#print("Disconnected because %s" %reason)

	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		messageContent = messageContent.replace('\n', '%0A')
		self.messages = self.messages + jid + "," + formattedDate + "," + messageContent + "\n"
		#print("%s [%s]:%s"%(jid, formattedDate, messageContent))

		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))
	