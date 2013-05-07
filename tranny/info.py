"""
Misc info functions related to the underlying OS
"""
from collections import namedtuple
from time import time
from os import getpid
from psutil import Process, disk_partitions, disk_usage


def uptime_sys():
    with open('/proc/uptime', 'r') as f:
        uptime_data = f.readline()
        uptime_seconds = float(uptime_data.split()[0])
    return uptime_seconds


def uptime_app():
    return time() - Process(getpid()).create_time


def disk_free():
    disk_info = dict()
    for path in [p.mountpoint for p in filter(valid_path, disk_partitions(all=True))]:
        disk_info[path] = disk_usage(path)
    return disk_info


def file_size(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if 1024.0 > num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def valid_path(path):
    """ Determine if a path is deemed "valid". This means we are looking for real partitions (not kernel devices)
    and mounted partitions.

    :param path: Usually named tuple returned from psutil.disk_partitions()
    :type path: namedtuple
    :return: Valid path state
    :rtype: bool
    """
    bad_prefix = ['/sys', '/dev', '/proc', '/run', '/tmp']
    if hasattr(path, "mountpoint"):
        path = path.mountpoint
    return not any(path.startswith(prefix) for prefix in bad_prefix)
