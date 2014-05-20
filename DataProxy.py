#encoding=utf-8
import logging
import time
import os
import uuid
import struct
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet import reactor

RECORD_DIR = "/tmp/records/"

class DataClientFactory(ClientFactory):
    '''
        send data to server
    '''
    class MyProtocol(Protocol):
        def __init__(self, dataProxy):
            self.dataProxy = dataProxy
            dataProxy.client = self

        def dataReceived(self, data):
            if not self.dataProxy.server:
                logging.error("connection from client not found, cant transport data to client")
            else:
                self.dataProxy.server.transport.write(data)
                logging.info("transported %.3f KB s2c" % (len(data)/1024.0))

    def __init__(self, dataProxy):
        self.dataProxy = dataProxy

    def startedConnecting(self, connector):
        logging.info("started to connect to server..")

    def buildProtocol(self, addr):
        logging.info("connected to server.")
        return self.MyProtocol(self.dataProxy)
    
    def clientConnectionLost(self, connector, reason):
        logging.error("Lost connect to server.Reason:%s" % reason)
        self.dataProxy.client = None
        #self.dataProxy.server.transport.loseConnection()
        #self.dataProxy.server = None

    def clientConnectionFailed(self, connector, reason):
        logging.error("Connect to server failed. Reason:%s" % reason)

class ServerFactory(Factory):
    '''
        receive data from game client
    '''
    class MyProtocol(Protocol):
        def __init__(self, dataProxy):
            self.dataProxy = dataProxy
            logging.info("recorder relay data to %s:%s" % (dataProxy.serverIp, dataProxy.serverPort))
            reactor.connectTCP(dataProxy.serverIp, dataProxy.serverPort, DataClientFactory(dataProxy))

        def dataReceived(self, data):
            for i in range(50):
                if not self.dataProxy.client: time.sleep(0.5)
                else: break
            if not self.dataProxy.client:
                logging.error("connecton to server not found, cant transport data to server")
            else:
                self.dataProxy.client.transport.write(data)
                logging.info("transported %.3f KB c2s" % (len(data)/1024.0))
                #record
                if self.dataProxy.IsRecording():
                    self.dataProxy.Recording(data)

        def connectionMade(self):
            logging.info("game client connected.")
            self.dataProxy.server = self
                    
        def connectionLost(self, reason):
            logging.info("game client closed.")
            if self.dataProxy.client:
                self.dataProxy.client.transport.loseConnection()
                self.dataProxy.client = None

    def __init__(self, dataProxy):
        self.dataProxy = dataProxy

    def buildProtocol(self, addr):
        if self.dataProxy.client:
            logging.error("duplicate connect from game client, ignored")
            return None
        return self.MyProtocol(self.dataProxy)

class Proxy(object):
    def __init__(self, listenPort, serverIp, serverPort):
        self.listenPort, self.serverIp, self.serverPort = listenPort, serverIp, serverPort
        self.listenObj = None
        self.client = None
        self.server = None
        self.recordFlag = False
        self.recordInfo = None
        
    def Recording(self, data):
        if not self.recordFlag: return
        global RECORD_DIR
        if not self.recordInfo:
            if not os.path.isdir(RECORD_DIR):
                try: os.makedirs(RECORD_DIR)
                except Exception,e: logging.error("create record dir %s failed: %r" % (RECORD_DIR, e)); return
            recordInfo = {}
            recordInfo['fd'] = file(os.path.join(RECORD_DIR,str(uuid.uuid1())), 'wb')
            recordInfo['start'] = time.time()
            recordInfo['lastsend'] = time.time()
            recordInfo['fd'].write(struct.pack('<H%ds'%len(data), len(data), data))
            self.recordInfo = recordInfo
        else:
            recordInfo = self.recordInfo
            interval = time.time() - recordInfo['lastsend']
            recordInfo['lastsend'] = time.time()
            recordInfo['fd'].write(struct.pack('<f', interval))
            recordInfo['fd'].write(struct.pack('<H%ds'%len(data), len(data), data))
        
    def IsRecording(self):
        return self.recordFlag
        
    def StartRecord(self):
        if not self.recordFlag:
            self.recordFlag = True
    
    def StopRecord(self):
        #change flag
        assert(self.recordFlag)
        if not self.recordInfo: self.recordFlag = False; return
        recordInfo = self.recordInfo
        self.recordInfo = None
        #close file and rename
        oldname = recordInfo['fd'].name
        recordInfo['fd'].close()
        filename = os.path.join(RECORD_DIR, "%s-%s" % (time.strftime("%y%m%d%H%M%S",time.localtime(recordInfo['start'])),
                                                       time.strftime("%y%m%d%H%M%S")))
        try: os.rename(oldname, filename)
        except Exception, e: logging.error('rename failed: %r' % e)
        else: logging.info("record saved to '%s'" % (filename))
        
    def Start(self):
        logging.info("listening %s for game client.." % self.listenPort) 
        self.listenObj = reactor.listenTCP(self.listenPort, ServerFactory(self))

    def Stop(self):
        if self.listenObj :
            logging.info("to stop client factory..") 
            self.listenObj.stopListening()
        if self.server : self.server.transport.loseConnection()
        
    def Replay(self, filenames):
        def ReplayFunc(filename):
            fullname = os.path.join(RECORD_DIR, filename)
            if not os.path.isfile(fullname): logging.error("record '%s' not found" % fullname); return None
            fileobj = file(fullname, "rb")
            def RealFunc():
                if not self.client: logging.error("connect to server not found, replay for '%s' stop" % fullname); return
                lenstr = fileobj.read(2)
                if not lenstr: logging.info("replay for '%s' complete" % fullname); return
                len, = struct.unpack('<H', lenstr)
                data = fileobj.read(len)
                self.client.transport.write(data)
                logging.info("replay %.3f KB c2s" % (len/1024.0))
                #sleep for interval
                intervalStr = fileobj.read(4)
                if not intervalStr: logging.info("replay for '%s' complete" % fullname); return
                interval, = struct.unpack('<f', intervalStr)
                interval = 0
                reactor.callLater(interval, RealFunc)
                #logging.info("next replay will happen after %.3f seconds" % interval)
            RealFunc()
        for filename in filenames:
            ReplayFunc(filename)
        
def ShowRecords(fd):
    '''
        show records to user
    '''
    from stat import S_ISREG, ST_CTIME, ST_MODE, ST_SIZE
    entries = (os.path.join(RECORD_DIR, fn) for fn in os.listdir(RECORD_DIR))
    entries = ((os.stat(path), path) for path in entries)
    entries = ((stat[ST_CTIME], stat, path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
    for cdate,stat,path in sorted(entries):
        fd.write("%s\t%.3fKB\t%s\n" % (time.ctime(cdate), stat[ST_SIZE]/1024.0, os.path.basename(path)))