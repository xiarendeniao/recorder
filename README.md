recorder
========

http://blog.csdn.net/xiarendeniao/article/details/26393261

功能

    运行在tcp连接的client和server之间的代理服，主要用于数据记录和回放

    通过console控制: 开启代理、开启数据记录、显示数据文件、数据回放..

    可通过数据回放，还原服务器的状态(复现并发连接下MMOserver的bug场景，如果server逻辑层有包序号检测就行不通了)

    可分析数据文件来统计MMOserver的网络IO，根据在线数可计算客户端流量消耗等数据

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
