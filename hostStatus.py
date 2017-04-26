import socket
#import binascii#for debug
from binascii import unhexlify

#buffer size for receving packets.
BUFFER_SIZE = 256

#seconds for timeout
TIMEOUT = 3
#limit for timeout times
TIMEOUT_LIMIT = 3

'''
the data to send
receive:
    0701...: hosting, not matching, watchable
    0700...: hosting, not matching, not watchable
    0801...: hosting, matching, unknown
    
'''
DEFAULT_PACKET=unhexlify("056e7365d9ffc46e488d7ca192313472950000015028006b0c0000103f120000002000000000000000513944004a020c1700000000000000003301000012000000")


'''
arguments:
    ip, port
    sendData: data to send. so far only DEFAULT_PACKET
    timeout: socket recv timeout
    timeoutLimit: number of limit for timeout
return:
    recveied data, bytes type.
'''
def send(ip, port, bindPort=None, sendData=DEFAULT_PACKET, timeout=TIMEOUT, timeoutLimit=TIMEOUT_LIMIT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #for sending packet to client
    if bindPort is not None:
        sock.bind(('', bindPort))
        
    sock.settimeout(timeout)
    for timeoutCount in range(timeoutLimit):
        sock.sendto(sendData, (ip, port))
        try:
            recvData, addr = sock.recvfrom(BUFFER_SIZE)
            sock.close()
            return recvData
        except socket.timeout:
            print(('%s:%s'% (ip, port)),"timeout times:", timeoutCount+1)
            
    #if timeout too many times, return empty bytes which means there may be no packet coming at all.
    sock.close()
    return b''

'''
arguments: 
    ip, port
return:
    tuple of boolean representing:
    is hosting, is matching, is watchable
'''
def hostStatus(ip, port):
    recvData = send(ip, port, None)
    #print(binascii.hexlify(recvData))#for debug
    #hosting, not matching, watchable
    if bytes.startswith(recvData, b'\x07\x01'):
        return True, False, True
    #hosting, not matching, not watchable
    elif bytes.startswith(recvData, b'\x07\x00'):
        return True, False, False
    #hosting, matching, unknown
    elif bytes.startswith(recvData, b'\x08\x01'):
        '''
        TODO: code for check watchable: not implemented yet
        clientPort = int.from_bytes(recvData[7:9], 'big')
        clientIp = socket.inet_ntoa(recvData[9:13])
        print("test:", sendData)
        recvData = send(clientIp, clientPort, port, PACKETS[0])
        print(binascii.hexlify(recvData))
        '''
        return True, True, 'unknown'#maybe check in advance before the match start.
    #not hosting
    else:
        return False, False, False

#for testing
if __name__ == "__main__":
    import sys
    print(hostStatus(sys.argv[1], int(sys.argv[2])))
