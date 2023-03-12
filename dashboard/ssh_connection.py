from paramiko import SSHClient, AutoAddPolicy
from queue import Queue
import threading
import random
import time

username = "pi"
password = "raspberry"

# rpi-A is the transmitter
class RpiA:
    host = 'rpi-A.local'
    command = "python CapstoneProject/src/symposium_tx.py 6"
    #other_command = "python CapstoneProject/src/symposium_rx.py 7"
    
    def __init__(self, msg_queue: Queue, data_queue: Queue):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(self.host, username, password)
        self.msg_queue = msg_queue
        self.data_queue = data_queue
        
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
                print(f'Sending to RPI-A: {message}')
                stdin.write(message)
                print("Wrote to stdin")
            else:
                print(line, end="")
            self.data_queue.put_nowait((random.randint(500, 1000), random.randint(0,10)))
        stdin.close()
        stdout.close()
        stderr.close()
        self.client.close()
            
    
        
    def exec(self):
        stdin, stdout, stderr = self.client.exec_command(self.command, get_pty=True)
        
        print("Create thread")
        x = threading.Thread(target=self.pi_interface_msg_send, args=(stdin, stdout,stderr,), daemon=True)
        x.start()
        print("Thread Created")
        