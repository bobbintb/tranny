# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urlparse, urljoin
from time import time
from os import getpid
from fuzzywuzzy import fuzz
from psutil import Process, disk_partitions, disk_usage
from flask import request, url_for, redirect
from tranny import exceptions


def fmt_ratio(ratio):
    return "{:.2f}".format(float(ratio))


def uptime_sys():
    with open('/proc/uptime', 'r') as f:
        uptime_data = f.readline()
        uptime_seconds = float(uptime_data.split()[0])
    return uptime_seconds


def uptime_app():
    try:
        return time() - Process(getpid()).create_time
    except TypeError:
        return time() - Process(getpid()).create_time()


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


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def find_closest_match(string, iterable, key):
    if len(iterable) == 1:
        return iterable[0]
    def cmp(item):
        return fuzz.ratio(string.lower(), item.get(key, "").lower())
    return sorted(iterable, key=cmp, reverse=True)[0]


def raise_unless(v, exc=exceptions.TrannyException, msg=None):
    if not v:
        raise exc(msg)


contains = lambda seq, values: all([k in values for k in seq])
