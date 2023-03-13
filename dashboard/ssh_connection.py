from paramiko import SSHClient, AutoAddPolicy
from queue import Queue
import threading
import time

username = "pi"
password = "raspberry"

# rpi-A is the transmitter
class RpiA:
    host = 'rpi-A.local'
    command = "python CapstoneProject/src/symposium_tx.py 6"
    
    def __init__(self, msg_queue: Queue):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(hostname=self.host, username=username, password=password)
        self.msg_queue = msg_queue
        
    def pi_interface_msg_send(self, stdin, stdout, stderr):
        for line in iter(stdout.readline, ""):
            # Received a request for input
            if line.startswith("INP:"):
                time.sleep(0.1) # to ensure its ready for input
                message = ' '
                try:
                    message = self.msg_queue.get(timeout=2)
                except:
                    pass
                stdin.write(f"{message}\n")
            else:
                print(line, end="")
        stdin.close()
        stdout.close()
        stderr.close()
        self.client.close()
            
    def exec(self):
        stdin, stdout, stderr = self.client.exec_command(self.command, get_pty=True)
        x = threading.Thread(target=self.pi_interface_msg_send, args=(stdin, stdout,stderr,), daemon=True)
        x.start()
        
        
# rpi-B is the receiver
class RpiB:
    host = 'rpi-B.local'
    command = "python CapstoneProject/src/symposium_rx.py 7"
    
    def __init__(self, msg_queue: Queue, data_queue: Queue):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(hostname=self.host, username=username, password=password)
        self.msg_queue = msg_queue
        self.data_queue = data_queue
        
    def pi_interface_msg_recv(self, stdin, stdout, stderr):
        for line in iter(stdout.readline, ""):
            if line.startswith("DAT:"):
                # Received Data
                data = line[4:].replace("\r\n","").split(",")
                try:
                    self.data_queue.put_nowait((float(data[0]), float(data[1]), float(data[2])))
                except:
                    pass
            elif line.startswith("MSG:"):
                # Received a message
                msg = line[4:].strip()
                if len(msg) > 0:
                    try:
                        self.msg_queue.put_nowait(msg)
                    except:
                        pass
            else:
                # Print to command line in all other circumstances
                print(line, end="")
        stdin.close()
        stdout.close()
        stderr.close()
        self.client.close()
        
    def exec(self):
        stdin, stdout, stderr = self.client.exec_command(self.command, get_pty=True)
        x = threading.Thread(target=self.pi_interface_msg_recv, args=(stdin, stdout,stderr,), daemon=True)
        x.start()
        