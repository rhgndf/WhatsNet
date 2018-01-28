import sys, logging, os, time, queue

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.stacks import YowStackBuilder
#from yowsup.layers.axolotl.layer import YowAxolotlLayer
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback

from threading import Thread
import threading

credentials = dict(
    phone = 'PHONE NUMBER HERE',
    password = 'PASSWORD OBTAINED FROM YOWSUP',
)


CREDENTIALS = (credentials['phone'], credentials['password']) # replace with your phone and password
encryption = True
recvqueue = queue.Queue()

mainlayer = 0

class MsgLayer(YowInterfaceLayer):
    
    def __init__(self):
        super(MsgLayer, self).__init__()
        self.lock = threading.Condition()
    
    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        global mainlayer
        
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        if messageProtocolEntity.getType() == 'text':
            
            #print (messageProtocolEntity.getBody())
            #if messageProtocolEntity.getFrom() == "6597265606@s.whatsapp.net":
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
            self.toLower(receipt)
            
            recvqueue.put({"from": messageProtocolEntity.getFrom(), "data": messageProtocolEntity.getBody()})
            #    outgoingMessageProtocolEntity = TextMessageProtocolEntity(
            #        os.popen(messageProtocolEntity.getBody()).read(),
            #        to = messageProtocolEntity.getFrom())
            #self.toLower(outgoingMessageProtocolEntity)
            
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    @ProtocolEntityCallback("send_message")
    def sendMessage(self, msg, to):
        pass
        #print (msg, to)
        #outgoingMessageProtocolEntity = TextMessageProtocolEntity(msg, to = to)
        #self.toLower(outgoingMessageProtocolEntity)
        
    def onEvent(self, yowLayerEvent):
        if yowLayerEvent.getName() == 'send_message':

            message = yowLayerEvent.getArg('message')
            phone = yowLayerEvent.getArg('phone')
            
            self.lock.acquire()
            messageEntity = TextMessageProtocolEntity(message,to=phone)
            #self.ackQueue.append(messageEntity.getId())
            self.toLower(messageEntity)
            self.lock.release()

class YowsupEchoStack(Thread):
    def __init__(self, credentials, encryptionEnabled = True):
        
        Thread.__init__(self)
        stackBuilder = YowStackBuilder()
        
        
        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(MsgLayer)\
            .build()
        self.stack.setProp("org.openwhatsapp.yowsup.prop.axolotl.INDENTITY_AUTOTRUST", True)
        
        self.stack.setCredentials(credentials)

    def run(self):
        try:

            self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
            self.stack.loop()
        except AuthError as e:
            print("Authentication Error: %s" % e.message)
    
    def send_message(self, message, phone):
        self.stack.broadcastEvent(YowLayerEvent('send_message', message=message, phone=phone))
        

class WhatsAppMessageTunnel():
    def __init__(self):
        self.transport = YowsupEchoStack(CREDENTIALS, encryption)
        self.transport.start()
        
    def send(self, recipient, msg):
        self.transport.send_message(msg, recipient)
        
    def recv(self):
        try:
            return recvqueue.get(False)
        except:
            return None
    
    
