import socket
from binascii import unhexlify

#buffer size for receiving packets.
BUFFER_SIZE = 256

#seconds for timeout
DEFAULT_TIMEOUT = 3

#the data to send
DEFAULT_PACKET=unhexlify("056e7365d9ffc46e488d7ca192313472950000015028006b0c0000103f120000002000000000000000513944004a020c1700000000000000003301000012000000")

'''
arguments:
    ip, port, 
    timeout: socket recv timeout
    send_data: data to send. so far only DEFAULT_PACKET
return:
    received data or empty bytes if timeout. bytes type.
'''
def send(ip, port, timeout=DEFAULT_TIMEOUT, send_data=DEFAULT_PACKET):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(send_data, (ip, port))
    try:
        recv_data = sock.recv(BUFFER_SIZE)
    except socket.timeout:
        recv_data = b''
    sock.close()
    return recv_data

'''
arguments: 
    ip, port, 
    timeout: socket recv timeout
return:
    tuple of boolean representing:
        is hosting, is matching, is watchable
            0701...: hosting, not matching, watchable
            0700...: hosting, not matching, not watchable
            0801...: hosting, matching, unknown
            else: timeout, assume not hosting
'''
def host_status(ip, port, timeout):
    data = send(ip, port, timeout)[:2]
    if data == b'\x07\x01':
        return True, False, True
    elif data == b'\x07\x00':
        return True, False, False
    elif data == b'\x08\x01':
        '''
        TODO: checking watchable
        clientPort = int.from_bytes(recvData[7:9], 'big')
        clientIp = socket.inet_ntoa(recvData[9:13])
        '''
        return True, True, False #unknown, leave false.
    else:
        return False, False, False

#for testing
if __name__ == "__main__":
    import sys
    host_status(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
