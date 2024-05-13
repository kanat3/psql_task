import sys
import paramiko 
import getpass
import logging
import datetime
import os
from dotenv import load_dotenv

now = datetime.datetime.now().strftime('_%d-%m-%y_%H:%M:%S')
log_file = 'logs/psql_install' + now + '.log'

def check_cmd():
    if len(sys.argv) != 4:
        print("Usage: " + sys.argv[0] + " -p <port> <user>@<host>")
        sys.exit(1)

def connect():
    host = ''
    user = ''
    port = 22

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_file,
                    filemode='w') 
    logging.getLogger("paramiko").setLevel(logging.DEBUG)
    logger = logging.getLogger('connect')
    
    if len(sys.argv) == 4:
        address = sys.argv[3].split("@")
        if len(address) != 2:
           logger.error("Bad host format!")
           sys.exit(1)
        port = int(sys.argv[2])
        user = address[0]
        host = address[1]
    else:
        logger.error("Bad command line format!")
        sys.exit(1)

    passwd = getpass.getpass("Enter password:")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, user, passwd)
    sftp = client.open_sftp()
    client.exec_command('mkdir /export')
    sftp.put("docker-compose.yml", "/export/docker-compose.yml")
    sftp.put(".env", "/export/.env")
    client.exec_command('cd /export && set -a && source .env')
    client.exec_command('cd /export && docker compose up --build')
    sftp.close()
    client.close()

if __name__ == '__main__':
    check_cmd()
    connect()
