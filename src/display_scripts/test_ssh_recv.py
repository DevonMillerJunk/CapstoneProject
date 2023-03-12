from paramiko import SSHClient, AutoAddPolicy

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect('rpi-A.local', username='pi', password='raspberry')

# Run a command (execute PHP interpreter)
stdin, stdout, stderr = client.exec_command('python CapstoneProject/src/test_receiver.py 6 False', get_pty=True)
for line in iter(stdout.readline, ""):
    print(line, end="")

print(f'STDOUT: {stdout.read().decode("utf8")}')
print(f'STDERR: {stderr.read().decode("utf8")}')

# Get return code from command (0 is default for success)
print(f'Return code: {stdout.channel.recv_exit_status()}')

# Because they are file objects, they need to be closed
stdin.close()
stdout.close()
stderr.close()

client.close()