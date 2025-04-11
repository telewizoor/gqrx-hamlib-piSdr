import socket
import sys, getopt
import time
fldigi_option_set = 0

if len(sys.argv) > 0:
    try:
        opts, args = getopt.getopt(sys.argv, 'f',)
    except getopt.GetoptError:
        print('gqrx-hamlib.py [-f]')
        sys.exit(2)
    for index in range(len(args)):
        if args[index] == '-f':
           fldigi_option_set = 1

if fldigi_option_set == 1:
   import xmlrpc.client

TCP_IP = "localhost"
RIG_PORT = 4532
DUMMY_RIG_PORT = 4534
GQRX_PORT = 7356
FLDIGI_PORT = 7362

MESSAGE = ""

forever = 1
rig_freq = 0
gqrx_freq = 0
old_rig_freq = 0
old_gqrx_freq = 0

rig_mode = ''
gqrx_mode = ''
set_mode = ''
old_rig_mode = ''
old_gqrx_mode = ''

rig_vfo = ''
old_rig_vfo = ''

def getfreq(PORT):
    sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'f\n')
    # Look for the response
    amount_received = 0
    amount_expected = 8 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    return data

def setfreq(PORT, freq):
    sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    build_msg = 'F ' + str(freq) + '\n'
    MESSAGE = bytes(build_msg, 'utf-8')
    sock.sendall(MESSAGE)
    # Look for the response
    amount_received = 0
    amount_expected = 7 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    return data

def getmode(PORT):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'm\n')
    # Look for the response
    amount_received = 0
    amount_expected = 4 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    #print(data)
    return data

def setmode(PORT, mode):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    mode = mode.decode('utf-8')
    build_msg = 'M ' + str(mode) + '\n'
    build_msg = build_msg.encode('utf-8')
    #print(build_msg)
    sock.sendall(build_msg)
    # Look for the response
    amount_received = 0
    amount_expected = 7 #len(message)
    data = ''
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    return data

def getvfo(PORT):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'v\n')
    # Look for the response
    amount_received = 0
    amount_expected = 5 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    #print(data)
    return data

def setvfo(PORT, mode):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    mode = mode.decode('utf-8')
    build_msg = 'V ' + str(mode) + '\n'
    build_msg = build_msg.encode('utf-8')
    #print(build_msg)
    sock.sendall(build_msg)
    # Look for the response
    amount_received = 0
    amount_expected = 7 #len(message)
    data = ''
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    sock.close()
    return data

if fldigi_option_set == 1:
    server = xmlrpc.client.ServerProxy('http://{}:{}/'.format(TCP_IP, FLDIGI_PORT))

while forever:
    time.sleep(0.1)

    # FREQ
    rig_freq = getfreq(RIG_PORT)
    if rig_freq != old_rig_freq:
        # set gqrx to Hamlib frequency
        rc = setfreq(DUMMY_RIG_PORT, float(rig_freq))
        rc = setfreq(GQRX_PORT, float(rig_freq))
        #print('Return Code from GQRX: {0}'.format(rc))
        old_rig_freq = rig_freq
        old_gqrx_freq = rig_freq
        
    gqrx_freq = getfreq(GQRX_PORT)
    if gqrx_freq != old_gqrx_freq:
        # set Hamlib to gqrx frequency
        rc = setfreq(DUMMY_RIG_PORT, float(gqrx_freq))
        rc = setfreq(RIG_PORT, float(gqrx_freq))
        #print('Return Code from Hamlib: {0}'.format(rc))
        # Set fldigi to gqrx frequency
        if fldigi_option_set == 1:
            server.main.set_frequency(float(gqrx_freq))
        old_gqrx_freq = gqrx_freq
        old_rig_freq = gqrx_freq

    # MODE
    try:
        rig_mode = getmode(RIG_PORT)
    except:
        print('Error :)')
    if rig_mode != old_rig_mode:
        # set gqrx to Hamlib mode
        rc = setmode(DUMMY_RIG_PORT, (rig_mode))
        rc = setmode(GQRX_PORT, (rig_mode))
        #print('Return Code from GQRX: {0}'.format(rc))
        old_rig_mode = rig_mode
        old_gqrx_mode = rig_mode

    gqrx_mode = getmode(GQRX_PORT)
    if gqrx_mode != old_gqrx_mode:
        # set Hamlib to gqrx mode
        #rc = setmode(RIG_PORT, (gqrx_mode))
        #print('Return Code from Hamlib: {0}'.format(rc))
        # # Set fldigi to gqrx frequency
        # if fldigi_option_set == 1:
        #     server.main.set_frequency((gqrx_mode))
        old_gqrx_mode = gqrx_mode
        old_rig_mode = gqrx_mode

    # VFO
    try:
        rig_vfo = getvfo(RIG_PORT)
    except:
        print('Error :)')
    if rig_vfo != old_rig_vfo:
        # set gqrx to Hamlib vfo
        rc = setvfo(DUMMY_RIG_PORT, (rig_vfo))
        rc = setvfo(GQRX_PORT, rig_vfo)
        old_rig_vfo = rig_vfo


