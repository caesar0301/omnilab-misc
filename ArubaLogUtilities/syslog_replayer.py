#!/usr/bin/env python
import socket
import argparse

# Global variables
rcvhost = None
rcvport = None
maxcnt = None
cnt_msg = 0
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def _do_send(msg, addr):
    """@msg: msg in plain
    @addr: receiver address tupple: (host, port)
    """
    global cnt_msg
    sender_socket.sendto(msg, addr)
    cnt_msg += 1
    print "Message #%d sent successfully" % cnt_msg

def sender(fname):
    f = open(fname, 'rb')
    receiver_address = (rcvhost, rcvport)
    print "Sending log to %s on port %d" % (rcvhost, rcvport)
    
    global maxcnt
    for line in f:
        line = line.rstrip('\r\n')
        if maxcnt is None:
            _do_send(line, receiver_address)
        else:
            if maxcnt > 0:
               _do_send(line, receiver_address)
               maxcnt -= 1
        

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Program to replay syslog over UDP.")
    parser.add_argument('--host', type=str, default="localhost", help="Receiver host name or IP address. Default: localhost")
    parser.add_argument('--port', type=int, default=54321, help="Receiver port. Default: 54321")
    parser.add_argument('--maxc', type=int, default=None, help="Maximum number of logs to be sent. Default: no limitation")
    parser.add_argument('--log', type=str, default=None, help="Log file name to reply")
    args = parser.parse_args()
    rcvhost = args.host
    rcvport = args.port
    maxcnt = args.maxc
    logname = args.log
    
    if logname is None:
        print "Option --log can't be empty. -h for more help."
        exit(-1)
    if maxcnt != None and maxcnt <= 0:
        print "Option --maxc should be empty or a number > 0"
        exit (-1)
        
    sender(logname)
    print "Sending finished."
    
    
    