#!/usr/bin/env python
# secureConnectionHandler.py
import paramiko
import os

# initiate ssh connection to a remote host
def connect(host, serverLogin, private_key, port=22):
    transport = paramiko.Transport((host, port))
    if os.path.exists(private_key):
        rsa_key = paramiko.RSAKey.from_private_key_file(private_key)
        transport.connect(username=serverLogin, pkey=rsa_key)
    else:
        raise TypeError("Incorrect private key path")
    return transport

# create sftp connection from ssh connection (conn.get and conn.put)
def sftp_connect(transport):
    #return transport.open_sftp()
    return paramiko.SFTPClient.from_transport(transport)
#sftp_conn = sftp_connect(ssh_conn)
#sftp_conn.put('localpath.txt', 'remotepath.txt')

def exec_cmd(transport, command):
    channel = transport.open_session()
    channel.exec_command(command)
    output = channel.makefile('rb', -1).readlines()
    return output
#exec_cmd(secureConnection, 'a')
#exec_cmd(secureConnection, 's')
#response = exec_cmd(secureConnection, 'ls -al')
#print response
