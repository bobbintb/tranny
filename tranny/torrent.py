# -*- coding: utf-8 -*-
# The contents of this file are subject to the Python Software Foundation
# License Version 2.3 (the License).  You may not copy or use this file, in
# either source code or executable form, except in compliance with the License.
# You may obtain a copy of the License at http://www.python.org/license.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.

# Written by Petru Paler

# Minor modifications made by Andrew Resch to replace the BTFailure errors with Exceptions
from hashlib import sha1
from tranny import util, exceptions


def decode_int(x, f):
    f += 1
    newf = x.index('e', f)
    n = int(x[f:newf])
    if x[f] == '-':
        if x[f + 1] == '0':
            raise ValueError
    elif x[f] == '0' and newf != f+1:
        raise ValueError
    return n, newf+1


def decode_string(x, f):
    colon = x.index(':', f)
    n = int(x[f:colon])
    if x[f] == '0' and colon != f+1:
        raise ValueError
    colon += 1
    return x[colon:colon+n], colon+n


def decode_list(x, f):
    r, f = [], f+1
    while x[f] != 'e':
        v, f = decode_func[x[f]](x, f)
        r.append(v)
    return r, f + 1


def decode_dict(x, f):
    r, f = {}, f+1
    while x[f] != 'e':
        k, f = decode_string(x, f)
        r[k], f = decode_func[x[f]](x, f)
    return r, f + 1


decode_func = {
    'l': decode_list,
    'd': decode_dict,
    'i': decode_int,
    '0': decode_string,
    '1': decode_string,
    '2': decode_string,
    '3': decode_string,
    '4': decode_string,
    '5': decode_string,
    '6': decode_string,
    '7': decode_string,
    '8': decode_string,
    '9': decode_string
}


def bdecode(x):
    try:
        r, l = decode_func[x[0]](x, 0)
    except (IndexError, KeyError, ValueError):
        raise exceptions.TrannyException("not a valid bencoded string")
    return r

from types import StringType, IntType, LongType, DictType, ListType, TupleType


class Bencached(object):

    __slots__ = ['bencoded']

    def __init__(self, s):
        self.bencoded = s


def encode_bencached(x, r):
    r.append(x.bencoded)


def encode_int(x, r):
    r.extend(('i', str(x), 'e'))


def encode_bool(x, r):
    if x:
        encode_int(1, r)
    else:
        encode_int(0, r)


def encode_string(x, r):
    r.extend((str(len(x)), ':', x))


def encode_list(x, r):
    r.append('l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append('e')


def encode_dict(x, r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)), ':', k))
        encode_func[type(v)](v, r)
    r.append('e')

encode_func = {
    Bencached: encode_bencached,
    IntType: encode_int,
    LongType: encode_int,
    StringType: encode_string,
    ListType: encode_list,
    TupleType: encode_list,
    DictType: encode_dict
}

try:
    from types import BooleanType
    encode_func[BooleanType] = encode_bool
except ImportError:
    pass


def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return ''.join(r)


class BDict(dict):
    def encode(self, bdict=None):
        return bencode(bdict if bdict else self)

    def decode(self, bdict=None):
        return bdecode(bdict if bdict else self)


class Torrent(BDict):
    """
    Represents a torrent file as a python dict instance. This maps
    perfectly to the bencoded structure of the torrent file
    """
    @staticmethod
    def from_file(file_path):
        with open(file_path, "rb") as torrent_file:
            return Torrent.from_str(torrent_file.read())

    @classmethod
    def from_str(cls, torrent_data):
        """ Generate a torrent instance from a bencoded string of torrent data.

        :param cls:
        :type cls:
        :param torrent_data:
        :type torrent_data:
        :return:
        :rtype:
        """
        torrent = Torrent()
        torrent.update(torrent.decode(torrent_data))
        return torrent

    @property
    def info_hash(self):
        """ Calculate and return the hex representation of the torrents info key
        value

        :return: Hex encoded hash of the torrent info field
        :rtype: str
        """
        return self.calc_hash().hexdigest()

    @property
    def info_hash_binary(self):
        return self.calc_hash().digest()

    def calc_hash(self):
        return sha1(self.encode(self[b'info']))

    def size(self, human=False):
        """ Calculate and return the size of the torrent

        :param human: Return a human readable size string
        :type human: str
        :return: Torrent Size
        :rtype: str,int
        """
        try:
            total = sum([f['length'] for f in self['info']['files']])
        except KeyError:
            total = self['info']['length']
        return util.file_size(total) if human else total

    @property
    def name(self):
        return self['info']['name']
