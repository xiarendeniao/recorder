recorder
========

http://blog.csdn.net/xiarendeniao/article/details/26393261

功能

    运行在tcp连接的client和server之间的代理服，主要用于数据记录和回放

    通过console控制: 开启代理、开启数据记录、显示数据文件、数据回放..

    可通过数据回放，还原服务器的状态(复现并发连接下MMOserver的bug场景，如果server逻辑层有包序号检测就行不通了)

    可分析数据文件来统计MMOserver的网络IO，根据在线数可计算客户端流量消耗等数据

    模拟网络延迟(TcpDelay)

Usage

    [root@test-22 recorder]# python main.py 
    2016-09-07 15:26:14,361 INFO [Console.py:98]listening 8765 for console..
    2016-09-07 15:26:18,733 INFO [Console.py:27]console client connected
    2016-09-07 15:26:32,286 INFO [Console.py:36]you selected option 1
    2016-09-07 15:26:32,286 INFO [DataProxy.py:143]listening 1111 for game client..
    2016-09-07 15:27:22,303 INFO [DataProxy.py:56]recorder relay data to 10.4.4.22:5630
    2016-09-07 15:27:22,303 INFO [DataProxy.py:34]started to connect to server..
    2016-09-07 15:27:22,304 INFO [DataProxy.py:73]game client connected.
    2016-09-07 15:27:22,304 INFO [DataProxy.py:37]connected to server.
    2016-09-07 15:27:22,328 INFO [DataProxy.py:67]transported 0.034 KB c2s
    2016-09-07 15:27:22,352 INFO [DataProxy.py:28]transported 0.027 KB s2c
    2016-09-07 15:27:22,363 INFO [DataProxy.py:67]transported 0.008 KB c2s
    2016-09-07 15:27:22,653 INFO [DataProxy.py:28]transported 0.034 KB s2c
    2016-09-07 15:27:39,543 INFO [Console.py:36]you selected option 3
    2016-09-07 15:27:58,825 INFO [DataProxy.py:67]transported 0.016 KB c2s
    2016-09-07 15:27:58,826 INFO [DataProxy.py:28]transported 0.012 KB s2c 

    [root@test-22 recorder]# telnet 127.1 8765
    Trying 127.0.0.1...
    Connected to 127.1.
    Escape character is '^]'.

            welcome to use recorder:
            1.start proxy. proxyPort serverIP serverPort
            2.stop proxy
            3.start record
            4.stop record
            5.show records
            6.replay filename,filename,..
            h.help
    1 1111 10.4.4.22 5630
    3
    4
    5
    Wed Sep  7 15:29:04 2016        0.640KB 160907152758-160907152904
    2

    [root@test-22 recorder]# python TcpDelay.py -L15631 -H127.1 -P15630 -D0.5 -D0.8
    2017-05-31 11:11:09,496 INFO [TcpDelay.py:18]toServer connected
    2017-05-31 11:11:09,505 INFO [TcpDelay.py:18]toServer connected
    2017-05-31 11:11:10,060 INFO [TcpDelay.py:66]IPv4Address(TCP, '10.6.10.140', 11942) > IPv4Address(TCP, '127.0.0.1', 15630) c2s 0.035 KB
    2017-05-31 11:11:10,158 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11942) s2c 0.035 KB
    2017-05-31 11:11:10,314 INFO [TcpDelay.py:66]IPv4Address(TCP, '10.6.10.140', 11943) > IPv4Address(TCP, '127.0.0.1', 15630) c2s 0.039 KB
    2017-05-31 11:11:10,334 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11943) s2c 0.035 KB
    2017-05-31 11:11:10,808 INFO [TcpDelay.py:66]IPv4Address(TCP, '10.6.10.140', 11942) > IPv4Address(TCP, '127.0.0.1', 15630) c2s 0.049 KB
    2017-05-31 11:11:10,987 INFO [TcpDelay.py:66]IPv4Address(TCP, '10.6.10.140', 11943) > IPv4Address(TCP, '127.0.0.1', 15630) c2s 0.049 KB
    2017-05-31 11:11:11,368 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11942) s2c 0.052 KB
    2017-05-31 11:11:11,400 INFO [TcpDelay.py:75]IPv4Address(TCP, '10.6.10.140', 11942) fromClient closed
    2017-05-31 11:11:11,400 INFO [TcpDelay.py:41]IPv4Address(TCP, '127.0.0.1', 15630) toServer closed
    2017-05-31 11:11:11,411 INFO [TcpDelay.py:18]toServer connected
    2017-05-31 11:11:11,544 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11943) s2c 0.052 KB
    2017-05-31 11:11:11,562 INFO [TcpDelay.py:75]IPv4Address(TCP, '10.6.10.140', 11943) fromClient closed
    2017-05-31 11:11:11,562 INFO [TcpDelay.py:41]IPv4Address(TCP, '127.0.0.1', 15630) toServer closed
    2017-05-31 11:11:11,574 INFO [TcpDelay.py:18]toServer connected
    2017-05-31 11:11:11,997 INFO [TcpDelay.py:66]IPv4Address(TCP, '10.6.10.140', 11944) > IPv4Address(TCP, '127.0.0.1', 15630) c2s 0.106 KB
    2017-05-31 11:11:12,045 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11944) s2c 0.014 KB
    2017-05-31 11:11:12,046 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11944) s2c 0.030 KB
    2017-05-31 11:11:12,067 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11944) s2c 0.025 KB
    2017-05-31 11:11:12,068 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11944) s2c 0.611 KB
    2017-05-31 11:11:12,068 INFO [TcpDelay.py:30]IPv4Address(TCP, '127.0.0.1', 15630) > IPv4Address(TCP, '10.6.10.140', 11944) s2c 0.119 KB
