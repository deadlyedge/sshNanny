import json
import time
import pymongo
import paramiko
from static import xlogger

logger = xlogger.get_my_logger(__name__)

PROCESS_LINES = 10  # only these command show in 'ssh top' would count
PROCESS_PERCENTAGE = 10  # if a command's cpu usage% lower than this, it wouldn't count
NOT_COUNT = [  # some system command should be excluded.
    'kernel_task', 'top', 'launchd', 'backupd',
    'diskimages-helpe', 'ScreenSaverEngin'
]

with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

myDB_Client = pymongo.MongoClient(
    'mongodb://%s:%s@%s/' % (config['database_user'],
                             config['database_password'],
                             config['database_address'])
)

myDatabase = myDB_Client['homeMac_usage']
usageDB = myDatabase.usage


def showSSH():
    lines = []
    counter = 0
    stdin, stdout, stderr = ssh.exec_command('top -u -s 5 -stats cpu,state,command -n %s' % PROCESS_LINES)
    for line in iter(lambda: stdout.readline(2048), ""):
        if 'COMMAND' in line or counter != 0:
            if 'COMMAND' in line:
                line = '0 ---- ----'
            reform = line.split()
            cpu = float(reform.pop(0))
            state = reform.pop(0)
            program = ' '.join(reform)
            if cpu > PROCESS_PERCENTAGE \
                    and state != 'sleeping' \
                    and program not in NOT_COUNT:
                lines.append({'program': program,
                              'cpu': cpu,
                              'state': state
                              })
            counter += 1
        if counter == PROCESS_LINES + 1:
            if lines:
                usageDB.insert_one({'timestamp': int(time.time()), 'programs': lines})
                logger.info(f'{lines = }')  # this info format only work in python 3.8, you may delete the f*...
            else:
                logger.debug('empty list...')
            lines = []
            counter = 0


if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    # ssh.load_system_host_keys()  # I don't know what it means actually, it may helps so I just keep it.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    while True:
        try:
            ssh.connect(config['ssh_address'],
                        username=config['ssh_user'],
                        password=config['ssh_password'])
        except TimeoutError:
            logger.error('失联中。。。')  # the host mac maybe sleep or shutdown.  we can wait, right?
            time.sleep(60)
            continue

        showSSH()
