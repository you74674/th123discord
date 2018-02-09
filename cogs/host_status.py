import socket
import binascii
import time

'''
########
utilities
########
'''
#for transformation between bytes and address
def atob(address):
    return (address[1]).to_bytes(2, byteorder='big')+socket.inet_aton(address[0])
def btoa(_bytes):
    return (int.from_bytes(_bytes[0:2], 'big'), socket.inet_ntoa(_bytes[2:9]))

'''
########
constants
########
'''
#buffer size for receiving packets.
BUFFER_SIZE = 256
#seconds for timeout
DEFAULT_TIMEOUT = 3


'''
########
packets
########
'''
'''
[056e7365d9ffc46e488d7ca19231347295: 17 bytes][unknown for 4 bytes][28: 1 byte][unknown for 43 bytes *]
*: include flags for asking is_wachable or other unknown status (some start with 06, 05 or 04
'''
PACKET_TO_HOST=[
    binascii.unhexlify("056e7365d9ffc46e488d7ca19231347295000000002800000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    binascii.unhexlify("05647365d9ffc46e488d7ca19231347295000000002800000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
]
'''
for hole punch
same as above except a bit.
'''
PACKET_TO_CLIENT=[
    binascii.unhexlify("056e7365d9ffc46e488d7ca19231347295000000002800000001000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    binascii.unhexlify("05647365d9ffc46e488d7ca19231347295000000002800000001000000000000000000000000000000000000000000000000000000000000000000000000000000")
]
'''
[010200][address: 6 bytes][00000000000000000200][address: 6 bytes][0000000000000000000077bc]
77bc: for hole punching
'''
REQUEST_PACKET_PARTS=["010200", "00000000000000000200", "0000000000000000000077bc"]
REQUEST_PACKET_PARTS=[binascii.unhexlify(p) for p in REQUEST_PACKET_PARTS]
def get_request_packet(address1, address2, parts=REQUEST_PACKET_PARTS):
    return parts[0]+atob(address1)+parts[1]+atob(address2)+parts[2]

'''
########
main functions
########
'''
'''
TODO: This function is not complete yet.
argument:
    host: (host_ip, host_port)
    client: (client_ip, client_port)
    timeout: timeout time for hole punching.
return:
    packet from client
    
1. bind host_port (maybe to imitate this is host sending packet)
2. send get_request_packet(client, client) to client.
3. send get_request_packet(host, client) to host.
4.  if timeout:
        back to 2
    else: 
        receive a packet from client
5. send PACKET_TO_CLIENT to client and receive the status of client
'''
def hole_punch(host, client, timeout=DEFAULT_TIMEOUT, is_sokuroll=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packets=[
        get_request_packet(client, client),#to client
        get_request_packet(host, client)#to host
    ]
    
    sock.bind(('', host[1]))
    for _ in range(3):
        sock.sendto(packets[0], client)
        #TODO: find out what the order should be
        for __ in range(3):
            sock.sendto(packets[1], host)
            recv_data = sock.recv(BUFFER_SIZE)
        if(recv_data!=b''):#got response
            time.sleep(0.1)
            sock.sendto(PACKET_TO_CLIENT[is_sokuroll], client)
            sock.recv(BUFFER_SIZE)
            recv_data = sock.recv(BUFFER_SIZE)
            break
    return recv_data

'''
arguments:
    address: (ip, port)
    timeout: socket recv timeout
    send_data: data to send. default is PACKET_TO_HOST
return:
    packet from address or empty bytes if timeout. bytes type.
'''
def send(address, timeout=DEFAULT_TIMEOUT, send_data=PACKET_TO_HOST[0]):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(send_data, address)
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
    is_sokuroll
return:
    tuple of boolean representing:
        is hosting, is matching, is watchable
            0701...: hosting, not matching, watchable
            0700...: hosting, not matching, not watchable
            0801...: hosting, matching, unknown(since hole_punch is not complete yet, assume not watchable)
                hole_punch return:
                    0701 or 0700, same as above.
            else: timeout, assume not hosting
note:
    receiving from host:
        waiting:
            watchable:
                0701000000: 5bytes
            not watchable:
                0700000000: 5bytes
        matching:
            [08010000000200: 7 bytes][client_port: 2 bytes][client_ip: 4bytes][8 bytes][1p profile name(first 8 bytes overwritten): 16 bytes][8 bytes][2p profile name: 24 bytes]
    hold_punch:
        waiting:
            same as above
        matching:
            [08010000000200: 7 bytes][client_port: 2 bytes][client_ip: 4bytes][1p profile name: 24 bytes][8 bytes][2p profile name: 24 bytes]
'''
def host_status(ip, port, timeout=DEFAULT_TIMEOUT, is_sokuroll=False):
    packet = send((ip, port), timeout, PACKET_TO_HOST[is_sokuroll])
    if packet.startswith(b'\x07\x01'):
        return True, False, True
    elif packet.startswith(b'\x07\x00'):
        return True, False, False
    elif packet.startswith(b'\x08\x01'):
        #recv_data = hole_punch((ip, port), btoa(packet[7:13]), timeout, is_sokuroll)
        #print(recv_data)
        #return True, True, (recv_data[1]==b'\x01')
        return True, True, False
    else:
        return False, False, False

#for testing
if __name__ == "__main__":
    import sys
    print(host_status(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
