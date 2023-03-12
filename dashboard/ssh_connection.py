from paramiko import SSHClient, AutoAddPolicy
from queue import Queue
import threading
import random

username = "pi"
password = "raspberry"
quit_cmd = ""

# rpi-A is the transmitter
class RpiA:
    host = 'rpi-A.local'
    command = "python CapstoneProject/src/test_receiver.py 6 False"
    
    def __init__(self, msg_queue: Queue, data_queue: Queue):
        # self.client = SSHClient()
        # self.client.set_missing_host_key_policy(AutoAddPolicy())
        # self.client.connect(self.host, username, password)
        self.msg_queue = msg_queue
        self.data_queue = data_queue
        print("Raspberyy pi object created")
        
    def handle_msg_queue(self):
        print("Message queue handler called")
        while True:
            try:
                message = self.msg_queue.get(timeout=5)
                print(f'RPI received: {message}')
            except:
                pass
            self.data_queue.put_nowait((random.randint(500, 1000), random.randint(0,10)))
        
    def exec(self):
        print("Create thread")
        x = threading.Thread(target=self.handle_msg_queue, daemon=True)
        x.start()
        print("Thread Created")
        
        
        # stdin, stdout, stderr = self.client.exec_command(self.command, get_pty=True)
        # for line in iter(stdout.readline, ""):
        #     print(line, end="")

        # print(f'STDOUT: {stdout.read().decode("utf8")}')
        # print(f'STDERR: {stderr.read().decode("utf8")}')

        # # Get return code from command (0 is default for success)
        # print(f'Return code: {stdout.channel.recv_exit_status()}')
        

# # Run a command (execute PHP interpreter)
# stdin, stdout, stderr = client.exec_command('python CapstoneProject/src/test_receiver.py 6 False', get_pty=True)
# for line in iter(stdout.readline, ""):
#     print(line, end="")

# print(f'STDOUT: {stdout.read().decode("utf8")}')
# print(f'STDERR: {stderr.read().decode("utf8")}')

# # Get return code from command (0 is default for success)
# print(f'Return code: {stdout.channel.recv_exit_status()}')

# # Because they are file objects, they need to be closed
# stdin.close()
# stdout.close()
# stderr.close()

# client.close()