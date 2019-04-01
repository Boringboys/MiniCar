#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import socket
import string
import threading

code=0
v=0

stmp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
stmp.connect(("8.8.8.8",80))
HOST = stmp.getsockname()[0]# Symbolic name meaning all available interfaces
stmp.close()
PORT = 6666 # Arbitrary non-privileged port
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
            

GPIO.setmode(GPIO.BCM)

#GPIO set
GPIO.setup(7,GPIO.OUT)#v of left
GPIO.setup(1,GPIO.OUT)#v of right

GPIO.setup(12,GPIO.OUT)#left
GPIO.setup(16,GPIO.OUT)

GPIO.setup(20,GPIO.OUT)#right
GPIO.setup(21,GPIO.OUT)

L=GPIO.PWM(7,100)#v betwen 0-100
R=GPIO.PWM(1,100)

#distance GPIO set
Trigf=14
Echof=15
GPIO.setup(Trigf,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Echof,GPIO.IN)
Triga=23
Echoa=24
GPIO.setup(Triga,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Echoa,GPIO.IN)

lock = threading.Lock()

class RecvThread(threading.Thread):
    def __init__(self,threadID,name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global code
        global v
        while True:
            databyte = conn.recv(1024)
            data = databyte.decode()
            if not databyte: break
            # print(type(data))
            getcode=int(data.split("#")[0])
            getv=int(data.split("#")[1])
            print(getcode,getv,type(getcode),type(getv))
            lock.acquire()
            if getcode!=code and getcode>=0 and getcode<=8:
                code = getcode
            if getv!=v and getv>=0 and getv <= 100:
                v = getv
            lock.release()
            #conn.sendall(databyte)



def goleft(s):
    L.start(0)
    R.start(s)
    GPIO.output(12,1)
    GPIO.output(16,0)
    GPIO.output(20,1)
    GPIO.output(21,0)
    
def goright(s):
    L.start(s)
    R.start(0)
    GPIO.output(12,1)
    GPIO.output(16,0)
    GPIO.output(20,1)
    GPIO.output(21,0)

def backleft(s):
    L.start(0)
    R.start(s)
    GPIO.output(12,0)
    GPIO.output(16,1)
    GPIO.output(20,0)
    GPIO.output(21,1)
    
def backright(s):
    L.start(s)
    R.start(0)
    GPIO.output(12,0)
    GPIO.output(16,1)
    GPIO.output(20,0)
    GPIO.output(21,1)
    
def go(s):
    L.start(s)
    R.start(s)
    GPIO.output(12,1)
    GPIO.output(16,0)
    GPIO.output(20,1)
    GPIO.output(21,0)
    
def back(s):
    L.start(s)
    R.start(s)
    GPIO.output(12,0)
    GPIO.output(16,1)
    GPIO.output(20,0)
    GPIO.output(21,1)
    
def stop():
    L.stop()
    R.stop()
    GPIO.output(12,0)
    GPIO.output(16,0)
    GPIO.output(20,0)
    GPIO.output(21,0)
    
def left(s):
    L.start(s)
    R.start(s)
    GPIO.output(12,0)
    GPIO.output(16,1)
    GPIO.output(20,1)
    GPIO.output(21,0)
    
def right(s):
    L.start(s)
    R.start(s)
    GPIO.output(12,1)
    GPIO.output(16,0)
    GPIO.output(20,0)
    GPIO.output(21,1)
    
#front distance
def checkfrontdist():
    GPIO.output(Trigf,1)
    time.sleep(0.00015)
    GPIO.output(Trigf,0)
    while not GPIO.input(Echof):
        pass
    t1=time.time()
    while GPIO.input(Echof):
        pass
    t2=time.time()
    return int((t2-t1)*340*100/2)

#after distance
def checkafterdist():
    GPIO.output(Triga,1)
    time.sleep(0.00015)
    GPIO.output(Triga,0)
    while not GPIO.input(Echoa):
        pass
    t1=time.time()
    while GPIO.input(Echoa):
        pass
    t2=time.time()
    return int((t2-t1)*340*100/2)


#init()
# code between 0-8
# v between 0-100

class ActionThread(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.threadID = ThreadID
        self.name = name
    def run(self):
        while True:
            # print(code,v)
            front = checkfrontdist()
            after = checkafterdist()
            print(front,after)
            sendstr = str(front)+"#"+str(after)
            conn.sendall(sendstr.encode(encoding="utf-8"))
            lock.acquire()
            gov = v
            howfront = 2
            if front <100:
                gov = v/2
            if front <50:
                gov = 0
            
            backv = v
            if after <100:
                backv = v/2
            if after <50:
                backv = 0 

            if code==1:
                go(gov)
            elif code==2:
                back(backv)
            elif code==0:
                stop()
            elif code==3:
                goleft(gov)
            elif code==4:
                goright(gov)
            elif code==5:
                backleft(backv)
            elif code==6:
                backright(backv)
            elif code==7:
                left(v)
            elif code==8:
                right(v)
            lock.release()
            time.sleep(0.1)

thread1 = RecvThread(1,"RecvT")
thread2 = ActionThread(1,"ActT")

thread1.start()
thread2.start()

thread1.join()
thread2.join()
