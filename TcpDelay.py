#encoding=utf-8
import logging, random, time, os, uuid, struct, argparse, pprint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet import reactor

#log config
g_logLevel = logging.DEBUG  
g_logFormat = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]%(message)s"  
CONF = None

class ToServerProtocol(Protocol):
    def __init__(self, fromClient):
        self.fromClient =  fromClient
        self.fromClient.toServer = self
        logging.info("toServer connected")

    def getId(self): return self.transport.getPeer()
    
    def dataReceived(self, data):
        if not self.fromClient:
            logging.error("%s fromClient not found, drop s2c %.3f KB" % (self.getId(), len(data)/1024.0))
        else:
            self.fromClient.transport.write(data)
            logging.info("%s > %s s2c %.3f KB" % (self.getId(), self.fromClient.getId(), len(data)/1024.0))

    def connectionLost(self, reason):
        logging.info("%s toServer closed", self.getId())
        self.fromClient.toServer = None
        self.fromClient.transport.loseConnection()

class ToServerFactory(ClientFactory):
    protocol = ToServerProtocol
    def __init__(self, fromClient):
        self.fromClient = fromClient

    def buildProtocol(self, addr):
        return self.protocol(self.fromClient)

class FromClientProtocol(Protocol):
    def __init__(self):
        self.toServer = None
        self.dataQueue = ''
        reactor.connectTCP(CONF.host, CONF.port, ToServerFactory(self))

    def getId(self): return self.transport.getPeer()

    def dataReceived(self, data):
        def func():
            if self.toServer:
                tdata = self.dataQueue
                self.dataQueue = ''
                logging.info("%s > %s c2s %.3f KB" % (self.getId(), self.toServer.getId(), len(tdata)/1024.0))
                self.toServer.transport.write(tdata)
        if not self.dataQueue:
            self.dataQueue += data
            reactor.callLater(CONF.delay[0]+(CONF.delay[1]-CONF.delay[0])*random.random(), func)
        else:
            self.dataQueue += data

    def connectionLost(self, reason):
        logging.info("%s fromClient closed", self.getId())
        if self.toServer:
            self.toServer.transport.loseConnection()
            self.toServer = None

class FromClientFactory(Factory):
    protocol = FromClientProtocol

if __name__ == "__main__":
    logging.basicConfig(level=g_logLevel,format=g_logFormat,stream=None)
    parser = argparse.ArgumentParser(description='************* network delay **************')
    parser.add_argument('-L', dest='listen', type=int, required=True, help='监听PORT')
    parser.add_argument('-H', dest='host', type=str, required=True, help='服务器IP')
    parser.add_argument('-P', dest='port', type=int, required=True, help='服务器PORT')
    parser.add_argument('-D', dest='delay', action='append', type=float, required=True, help='延迟时间sec,range[min,max]')

    CONF = parser.parse_args()

    CONF.delay = (min(CONF.delay),max(CONF.delay))
    logging.info("%s listening for game client" % pprint.pformat(CONF)) 
    listenObj = reactor.listenTCP(CONF.listen, FromClientFactory())
    reactor.run()
