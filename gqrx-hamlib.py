import socket
import os, sys, getopt
import time
import threading
import traceback
from datetime import datetime
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
REQUEST_PERIOD = 0.2
DEBUG = 0

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

print('START')

def log_error(e):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "error_log.txt")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # with open(log_path, "a", encoding="utf-8") as f:
        # print(f"[{now}] Error: {type(e).__name__}: {e}\n")
        # f.write(f"[{now}] Error: {type(e).__name__}: {e}\n")

def log(msg):
    if DEBUG:
        print(msg)

class DummyRigctldServer(threading.Thread):
    def __init__(self, host="localhost", port=4534):
        super().__init__()
        self.host = host
        self.port = port
        self.daemon = True  # Ensures it exits with the main thread
        self.running = True

        # Shared state
        self.dummy_rig_freq = 0
        self.dummy_rig_mode = 'USB'
        self.dummy_rig_vfo = 'VFOA'
        self.dummy_rig_request = 0

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((self.host, self.port))
                server_socket.listen(1)
                print(f"Dummy RIG server listening on {self.host}:{self.port}")

                while self.running:
                    conn, addr = server_socket.accept()
                    threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_error(f"Dummy RIG server error: {e}")

    def handle_client(self, conn, addr):
        print(f"Client connected: {addr}")
        with conn:
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    line = data.decode().strip()
                    if not line:
                        continue
                    if DEBUG:
                        print(f"Command received: {line}")
                    response = self.process_command(line)
                    if response:
                        conn.sendall((response + "\n").encode())
            except Exception as e:
                log_error(f"Error handling dummy rig client: {e}")

    def process_command(self, line):
        global rig_freq, rig_mode, rig_vfo
        parts = line.split()
        cmd = parts[0]

        if cmd == 'f':
            try:
                return str(int(float(rig_freq)))
            except:
                return 'RPRT 1'

        elif cmd == 'm':
            return rig_mode if rig_mode else 'USB'

        elif cmd == 'v':
            return rig_vfo if rig_vfo else 'VFOA'

        elif cmd == 'F':
            try:
                self.dummy_rig_freq = float(parts[-1])
                self.dummy_rig_request = 1
                return 'RPRT 0'
            except:
                return 'RPRT 1'

        elif cmd == 'M':
            try:
                self.dummy_rig_mode = parts[-1]
                return 'RPRT 0'
            except:
                return 'RPRT 1'

        elif cmd == 'V':
            try:
                self.dummy_rig_vfo = parts[-1]
                return 'RPRT 0'
            except:
                return 'RPRT 1'

        elif line == ';V ?':
            return 'VFOA\nVFOB'
        
        elif line.startswith('+\\get_vfo_info'):
            vfo_name = line.split()[-1].strip()
            if vfo_name in ['VFOA', 'VFOB']:
                # Rozdziel mode i width po linii (newline)
                mode_lines = rig_mode.strip().split('\n')
                mode_part = mode_lines[0] if len(mode_lines) > 0 else 'USB'
                width_part = mode_lines[1] if len(mode_lines) > 1 else '3000'

                freq = int(float(rig_freq)) if rig_freq else 0
                split = 0
                satmode = 0

                return (
                    f"get_vfo_info: {vfo_name}\n"
                    f"Freq: {freq}\n"
                    f"Mode: {mode_part}\n"
                    f"Width: {width_part}\n"
                    f"Split: {split}\n"
                    f"SatMode: {satmode}\n"
                    f"RPRT 0"
                )
            else:
                return 'RPRT 1'

        else:
            return 'RPRT 0'  # Default response

# Start Dummy RIG server
dummy_rig = DummyRigctldServer(host='0.0.0.0', port=DUMMY_RIG_PORT)
dummy_rig.start()

def recv_until_newline(sock):
    sock.settimeout(5.0)
    buffer = ''
    try:
        while '\n' not in buffer:
            data = sock.recv(32).decode('utf-8', errors='ignore')
            if not data:
                break
            buffer += data
    except socket.timeout:
        print("Timeout")

    line = buffer.split('\n', 1)[0]
    return line.strip()

def recv_until_last_newline(sock):
    sock.settimeout(5.0)
    buffer = ''
    try:
        while '\n' not in buffer:
            data = sock.recv(32).decode('utf-8', errors='ignore')
            if not data:
                break
            buffer += data
    except socket.timeout:
        print("Timeout")

    return buffer.strip()

def getfreq(PORT):
    sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'f\n')
    # Look for the response
    data = recv_until_newline(sock)
    sock.close()
    log('getfreq = ' + str(data))
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
    data = recv_until_newline(sock)
    sock.close()
    log('setfreq = ' + str(data))
    return data

def getmode(PORT):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'm\n')
    # Look for the response
    data = recv_until_last_newline(sock)
    sock.close()
    log('getmode = ' + str(data))
    return data

def setmode(PORT, mode):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    # mode = mode.decode('utf-8')
    build_msg = 'M ' + str(mode) + '\n'
    build_msg = build_msg.encode('utf-8')
    #print(build_msg)
    sock.sendall(build_msg)
    # Look for the response
    data = recv_until_last_newline(sock)
    sock.close()
    log('getmode = ' + str(data))
    return data

def getvfo(PORT):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall(b'v\n')
    # Look for the response
    data = recv_until_newline(sock)
    sock.close()
    log('getvfo = ' + str(data))
    return data

def setvfo(PORT, mode):
    sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    # mode = mode.decode('utf-8')
    build_msg = 'V ' + str(mode) + '\n'
    build_msg = build_msg.encode('utf-8')
    #print(build_msg)
    sock.sendall(build_msg)
    # Look for the response
    data = recv_until_newline(sock)
    sock.close()
    log('setvfo = ' + str(data))
    return data

if fldigi_option_set == 1:
    server = xmlrpc.client.ServerProxy('http://{}:{}/'.format(TCP_IP, FLDIGI_PORT))

while forever:
    # FREQ
    try:
        rig_freq = getfreq(RIG_PORT)
        log('old_rig_freq = ' + str(old_rig_freq) + ' rig_freq = ' + str(rig_freq))
        if rig_freq != old_rig_freq:
            # set gqrx to Hamlib frequency
            # rc = setfreq(DUMMY_RIG_PORT, float(rig_freq))
            rc = setfreq(GQRX_PORT, float(rig_freq))
            #print('Return Code from GQRX: {0}'.format(rc))
            old_rig_freq = rig_freq
            old_gqrx_freq = rig_freq
            
        gqrx_freq = getfreq(GQRX_PORT)
        log('old_gqrx_freq = ' + str(old_gqrx_freq) + ' gqrx_freq = ' + str(gqrx_freq))
        if gqrx_freq != old_gqrx_freq:
            # set Hamlib to gqrx frequency
            rc = setfreq(RIG_PORT, float(gqrx_freq))
            # Set fldigi to gqrx frequency
            if fldigi_option_set == 1:
                server.main.set_frequency(float(gqrx_freq))
            old_gqrx_freq = gqrx_freq
            old_rig_freq = gqrx_freq

        if dummy_rig.dummy_rig_request:
            dummy_rig.dummy_rig_request = 0
            if dummy_rig.dummy_rig_freq != 0:
                rc = setfreq(RIG_PORT, float(dummy_rig.dummy_rig_freq))
            print('Setting rig frequency as requested from dummy rig(LOG4OM etc)')

    except Exception as error:
        log_error(f"Error: {str(error)}")
        # sys.exit()

    # MODE
    try:
        rig_mode = getmode(RIG_PORT)
        log('old_rig_mode = ' + str(old_rig_mode) + ' rig_mode = ' + str(rig_mode))
        if rig_mode != old_rig_mode:
            # set gqrx to Hamlib mode
            # rc = setmode(DUMMY_RIG_PORT, rig_mode)
            rc = setmode(GQRX_PORT, rig_mode)
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
    except Exception as error:
        log_error(f"Error: {str(error)}")
        # sys.exit()

    # VFO
    try:
        rig_vfo = getvfo(RIG_PORT)
        log('old_rig_vfo = ' + str(old_rig_vfo) + ' rig_vfo = ' + str(rig_vfo))
        # dummy_rig_vfo = getvfo(DUMMY_RIG_PORT)
        # print('dummy rig VFO read: ' + str(dummy_rig_vfo))
    
        if rig_vfo != old_rig_vfo:
            # set gqrx to Hamlib vfo
            # rc = setvfo(DUMMY_RIG_PORT, rig_vfo)
            rc = setvfo(GQRX_PORT, rig_vfo)
            old_rig_vfo = rig_vfo

    except Exception as error:
        log_error(f"Error: {str(error)}")
        # sys.exit()

    log('------------------------------------------------------------')
    sys.stdout.flush()
    time.sleep(REQUEST_PERIOD)

