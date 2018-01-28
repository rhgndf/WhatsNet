#!/usr/bin/env python

from pytun import TunTapDevice
import base64
import threading
import sys
import psutil
import os
import signal
import time
import socket
from Crypto.Cipher import ARC4
from transports.whatsapp import WhatsAppMessageTunnel
def recv_loop(tunnel, rec, password, tun):
    while True:
        msg = 1
        while msg:
            msg = tunnel.recv()
            if msg and msg['from'] == rec+"@s.whatsapp.net":
                rc4obj = ARC4.new(password)
                tun.write(rc4obj.decrypt(base64.b64decode(msg['data'])))
        time.sleep(1)

def ping_server(loc):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (loc, 8099)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        connection, client_address = sock.accept()
        connection.close()



def start_main(rec, loc, dst, passwd,ifname):
    tunnel = WhatsAppMessageTunnel()
    # Create TUN device for network capture and injections
    tun = TunTapDevice(name='socialtun')

    print(tun.name + ' has been created, information follows:')

    tun.addr = loc
    tun.dstaddr = dst
    tun.netmask = '255.255.255.0'
    tun.mtu = 40000
    password = passwd

    print('Address: ' + tun.addr)
    print('Dest.-Address: ' + tun.dstaddr)
    print('Netmask: ' + tun.netmask)
    print('MTU: ' + str(tun.mtu))


    # Start TUN device
    tun.up()
    up = True

    print('TUN is up')


    # Create the receive thread via our helper method
    # thread = threading.Thread(target=main_loop_starter)
    thread = threading.Thread(target=recv_loop, args=(tunnel, rec, password, tun))
    thread.start()
    thread = threading.Thread(target=ping_server, args=(loc,))
    thread.start()
    while True:
        # Continually read from the tunnel and write data in base64
        buf = tun.read(tun.mtu)
        rc4obj = ARC4.new(password)
        tunnel.send(rec+"@s.whatsapp.net", base64.b64encode(rc4obj.encrypt(buf)))
        #print (buf)

    # Cleanup and stop application
    up = False
    tun.down()
    receiver.stop()

def start_main_fake():
    while True:
        time.sleep(1)

# print('~~ Bye bye! ~~')

# # Literally Overkill

# current_process = psutil.Process()
# os.kill(current_process.pid, signal.SIGKILL)