#!/usr/bin/env python
from logging import getLogger
import time
from os import getpid, unlink
from os.path import exists, join, dirname
import signal
import psutil
import tranny

PID_FILE_NAME = join(dirname(__file__), "tranny.pid")

log = getLogger("tranny.daemon")


class ProcessRunning(Exception):
    pass


def process_running(pid_val):
    """ Check if the process id is running.

    :param pid_val: Process ID to look for
    :type pid_val: int
    :return: Process running status
    :rtype: bool
    """
    #return any([pid for pid in listdir('/proc') if pid.isdigit() and int(pid) == pid_val])
    return int(pid_val) in psutil.get_pid_list()


def pid_check():
    """ Check for an existing running process and throw a ProcessRunning exception. The existing
    pid is gathered from the tranny.pid file in the project root.
    """
    pid = getpid()
    try:
        file_pid = int(open(PID_FILE_NAME).read())
    except IOError:
        file_pid = False
    if file_pid and process_running(file_pid):
        raise ProcessRunning("Existing tranny process already running under pid: {0}".format(pid))
    with open(PID_FILE_NAME, "w") as pid_file:
        pid_file.write(str(pid))


def pid_cleanup():
    if exists(PID_FILE_NAME):
        try:
            unlink(PID_FILE_NAME)
        except IOError:
            return False
    return True


def handle_sighup(signum, stack):
    """ Reload the services and configuration files upon receiving a SIGHUP

    :param signum:
    :param stack:
    :return:
    :rtype:
    """
    log.info("Received sighup reload signal")
    tranny.reload_conf()


def main():
    """ Do it.

    :return:
    :rtype:
    """
    try:
        signal.signal(signal.SIGHUP, handle_sighup)
    except (RuntimeError, AttributeError):
        log.warning("Failed to register process signal handler, process reloading will not be available")

    do_cleanup = True
    try:
        pid_check()
        tranny.start()
        tranny.run_forever()
    except ProcessRunning as msg:
        do_cleanup = False
        print(msg.message)
    finally:
        if do_cleanup:
            pid_cleanup()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "-p":
        from tests import lsprofcalltree
        import cProfile

        profileFileName = 'profiles/main_' + time.strftime('%Y%m%d_%H%M%S') + '.profile'

        profile = cProfile.Profile()
        profile.run('main()')
        kProfile = lsprofcalltree.KCacheGrind(profile)
        kFile = open(profileFileName, 'w+')
        kProfile.output(kFile)
        kFile.close()

        profile.print_stats()
    else:
        main()

