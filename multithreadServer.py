import socket, thread, time
import sys

#The optional argument port number is the port on which the proxy server is listening to a connection from a client
# If the port number is not entered, the default port 8080 is used.
if len(sys.argv) == 2:
    print 'Usage : "python ProxyServer.py port"\n[server_ip : It is the Port number Of Proxy Server'
    port = int(sys.argv[1])

else:
    port = 8080


def main():
    try:
        #creating server socket
        tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Socket creation successful!!!'
    except socket.error as e:
        print 'socket creation unsuccessful with error %s' % (e)
    #reference: https://docs.python.org/2/howto/sockets.html, http://pythontips.com/2013/08/06/python-socket-network-programming/
    # binding server socket
    tcpSerSock.bind(('', port))
    # listening queue up as many as 5 connect requests
    tcpSerSock.listen(5)
    #logging

    logFile = open("log.txt","a")
    logFile.write("Host name is : " + socket.gethostname()+ " Host Address is : "+socket.gethostbyname(socket.gethostname())+" \n")
    logFile.close()
    print 'socket is listening'
    while 1:
        print 'Ready to Serve'
        # start listening data from client
        tcpCliSock, addr = tcpSerSock.accept()
        #logging
        logFile = open("log.txt", "a")
        logFile.write("Received connection from "+ str(addr) +"\n")
        logFile.close()
        #start thread
        thread.start_new_thread(proxyThread, (tcpCliSock, addr))
    #close server socket
    tcpSerSock.close()
#proxy thread
#reference: http://luugiathuy.com/2011/03/simple-web-proxy-python/
def proxyThread(tcpCliSock, addr):
    #reference: http://stackoverflow.com/questions/1557571/how-to-get-time-of-a-python-program-execution
    startTime = time.time()
    fileExist = "false"
    #receiving request from client
    # reference: http://stackoverflow.com/questions/289035/receiving-data-over-a-python-socket
    response = tcpCliSock.recv(4096)
    #fetching the length
    responseLen = len(response)
    #logging the length
    logFile = open("log.txt", "a")
    logFile.write("Length of user request: "+ str(responseLen)+" bytes \n")
    logFile.close()
    print "response: ", response
    #logging the response
    logFile = open("log.txt", "a")
    logFile.write("Response message received: "+ response +" \n")
    logFile.close()
    # fetching the URL from response
    removedHttp = response.split()[1].partition("/")[2]
    print "removed http : ", removedHttp
    print "connect to:", removedHttp, port
    # logging the requested url
    logFile = open("log.txt", "a")
    logFile.write("Requested url is : "+ removedHttp +"\n port is: "+ str(port)+"\n ")
    logFile.close()
    try:
        #check whether file exists in cache
        f = open(removedHttp[0:], "r")
        print " f: ",f
        outputdata = f.readlines()
        fileExist = "true"
        print "reading from cache"

        #logging the cache hit
        logFile = open("log.txt", "a")
        logFile.write("File exist in Cache \n")
        logFile.write("HTTP/1.0 200 OK\n")
        logFile.write("Content-Type:text/html\n")
        logFile.close()
        # ProxyServer finds a cache hit and generates a response message
        msg = "HTTP/1.0 200 OK\r\n"
        tcpCliSock.send(msg)
        tcpCliSock.send("Content-Type:text/html\r\n")
        #generating response message
        response = ""
        for data in outputdata:
            response += data
        print "response: ",response
        #reference: http://stackoverflow.com/questions/289035/receiving-data-over-a-python-socket
        tcpCliSock.send(response)
        #fetching the length of response
        responseSentBytes = len(response)
        logFile = open("log.txt", "a")
        logFile.write("Bytes sent from proxy to client: "+str(responseSentBytes)+"bytes \n")
        logFile.close()
        print "Read from cache!!!"
        #reference: http://stackoverflow.com/questions/1557571/how-to-get-time-of-a-python-program-execution
        endTime = time.time()
        finalTime = endTime - startTime
        print "Time elapsed: ",finalTime
        #logging the time
        logFile = open("log.txt", "a")
        logFile.write("Time elapsed: "+ str(finalTime) +"\n")
        logFile.close()
    #Error handling for file not found
    except IOError:
        #logging for file not found in cache
        if (fileExist == "false"):
            logFile = open("log.txt", "a")
            logFile.write("File NOT found in cache!!! \n")
            logFile.close()
            # create a socket on proxy server
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                print ("connecting to proxy server: ")
                # fetching the request
                hostn = response.split()[1].partition("/")[2]
                print "host: ", hostn
                # connecting to port 80
                c.connect((hostn, 80))
                print "connect to:", hostn, port
                #reference for generating request : http://stackoverflow.com/questions/27342385/cache-a-http-get-request-in-python-sockets
                request = b"GET / HTTP/1.1\nHost: " + hostn + "\n\n"
                # sending request to server
                c.send(request)
                logFile = open("log.txt", "a")
                # fetch length of request
                proxyrequestbytes = len(request)
                # logging length of request
                logFile.write("Bytes sent from proxy to server: " + str(proxyrequestbytes) + "bytes \n")
                logFile.close()
                # receiving response from server
                response = c.recv(4096)
                # sending response to client
                tcpCliSock.send(response)
                ptosBytes = len(response)
                #logging the request lengths
                logFile = open("log.txt", "a")
                logFile.write("Bytes sent from server to proxy: " + str(ptosBytes) + "bytes \n")
                logFile.write("Bytes sent from proxy to client: " + str(ptosBytes) + "bytes \n")
                logFile.close()
                # creating temporary file
                tmpFile = open(hostn, "wb")
                # writting the response in file for cache
                for i in range(len(response)):
                    tmpFile.write(response)
                    response = c.recv(4096)
                tmpFile.close()
                # closing the sockets
                c.close()
                tcpCliSock.close()
                endTime = time.time()
                finalTime = endTime - startTime
                print "time elapsed: ", finalTime
                # logging the time
                logFile = open("log.txt", "a")
                logFile.write("time elapsed: " + str(finalTime)  + "\n")
                logFile.close()
            # handling exception
            except socket.error as err:
                print "illegal request"
                # sending 404 not found
                # reference: http://stackoverflow.com/questions/19485166/exception-not-handled-ioerror
                tcpCliSock.send('HTTP/1.1 404 not found\r\n')
                # logging the message
                logFile = open("log.txt", "a")
                logFile.write("HTTP/1.1 404 not found\n")
                logFile.close()
                endTime = time.time()
                finalTime = endTime - startTime
                print "time elapsed: ", finalTime
                #logging the time
                logFile = open("log.txt", "a")
                logFile.write("time elapsed: " + str(finalTime)  + "\n")
                logFile.close()

                sys.exit(1)
        else:
            # HTTP response message for file not found
            # reference: http://stackoverflow.com/questions/19485166/exception-not-handled-ioerror
            tcpCliSock.send('HTTP/1.1 404 not found\r\n')
            # logging the message
            logFile = open("log.txt", "a")
            logFile.write("HTTP/1.1 404 not found\n")
            logFile.close()
            endTime = time.time()
            finalTime = endTime - startTime
            # logging the time
            print "time elapsed: ", finalTime
            logFile = open("log.txt", "a")
            logFile.write("time elapsed: " + str(finalTime) + "\n")
            logFile.close()

    logFile = open("log.txt", "a")
    logFile.write("-------------------------------------------------------------- \n --------------------------------------------\n\n")
    logFile.close()
    #closing client socket
    tcpCliSock.close()


if __name__ == '__main__':
    main()
