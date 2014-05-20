#encoding=utf-8
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import logging
import DataProxy

class ConsoleFactory(Factory):
    '''
       listen console connect & accept console command. 
    '''
    class MyProtocol(LineReceiver):
        Commands = """
        welcome to use recorder:
        1.start proxy
        2.stop proxy
        3.start record
        4.stop record
        5.show records
        6.replay filename,filename,..
        h.help\n"""
    
        def __init__(self, factory):
            self.factory = factory
    
        def connectionMade(self):
            logging.info("console client connected")
            self.transport.write(self.Commands)
    
        def connectionLost(self, reason):
            logging.info("console client closed")
    
        def lineReceived(self, line):
            line = line.strip()
            if not line: return
            logging.info("you selected option %s", line[0])
            if line[0] == '1':
                if self.factory.proxy:
                    logging.error("proxy already exists")
                else:
                    listenPort = 5631
                    serverIp = "localhost"
                    #serverIp = "10.6.10.140"
                    serverPort = 5630
                    args = line.split(" ")
                    if len(args) >= 2 and args[1].isdigit(): listenPort = int(args[1])
                    if len(args) >= 3:
                        import socket
                        try: socket.inet_aton(args[2])
                        except socket.error: pass
                        else: serverIp = args[2]
                    if len(args) >= 4 and args[3].isdigit(): serverPort = int(args[3])
                    self.factory.proxy = DataProxy.Proxy(listenPort, serverIp, serverPort)
                    self.factory.proxy.Start()
    
            elif line[0] == '2':
                self.factory.proxy.Stop()
                self.factory.proxy = None
    
            elif line[0] == '3':
                if not self.factory.proxy:
                    logging.error("proxy not exists, cant record")
                else:
                    self.factory.proxy.StartRecord()
    
            elif line[0] == '4':
                if not self.factory.proxy or not self.factory.proxy.IsRecording():
                    logging.error("recording not exists, cant stop")
                else:
                    self.factory.proxy.StopRecord()
    
            elif line[0] == '5':
                DataProxy.ShowRecords(self.transport)
                
            elif line[0] == '6':
                if not self.factory.proxy: self.transport.write("proxy not exists, cant replay\n")
                else:
                    filenames = line.split(" ")[1:]
                    if not filenames: self.transport.write("invalid command\n")
                    else: self.factory.proxy.Replay(filenames)
                
            elif line[0] in ('h','?'):
                self.transport.write(self.Commands)
    
            else:
                logging.error("unrecognized command: %s" % line)
                  
    def __init__(self):
        self.proxy = None

    def buildProtocol(self, addr):
        return self.MyProtocol(self)

def start(port):
    '''
    listen console port
    '''
    logging.info("listening %d for console.." % port)
    reactor.listenTCP(port, ConsoleFactory())
    reactor.run()
