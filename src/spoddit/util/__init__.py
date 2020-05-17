import logging
from functools import reduce
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

import requests
import operator

logger = logging.getLogger(__name__)


def get_nested(data_dict, path, separator='.'):
    return reduce(operator.getitem, path.split(separator), data_dict)


def listify(x):
    return x if type(x) == list else [x]


def merge_dict(dict1, dict2):
    """
    Merge dicts and keep values of common keys in a list
    :param dict1: dictionary to be merged
    :param dict2: dictionary to be merged
    :return: a merged dictionary where similar key's values are merged into distinct lists
    """
    merged_dict = {}
    for key in list(set(list(dict1.keys()) + list(dict2.keys()))):
        if key in dict1 and key in dict2:
            # if both dicts have the same key, we merge the values
            merged_dict[key] = list(set(listify(dict1[key]) + listify(dict2[key])))
        else:
            # otherwise we simply listify the values
            merged_dict[key] = listify(dict.get(dict1, key) or dict.get(dict2, key))

    return merged_dict


class ThreadedHttpServer(Thread):
    __AVAILABLE_PORTS = [1337, 1234, 1235, 1236]
    is_running = False
    server_address = ('', '')
    httpd = None

    def __init__(self):
        super().__init__()

    def get_server_address(self):
        return ':'.join(map(str, self.server_address))

    def shutdown(self):
        """
        Shutdown SpotifyRedirectServer
        """
        if self.httpd is not None:
            self.httpd.shutdown()

    def run(self):
        f"""
        Start redirect server at localhost

        Several ports will be tried to bind to in order to start up the server.
        Namely {self.__AVAILABLE_PORTS}
        :return: 0 on shutdown or the OSError error number of started HTTPServer
        """
        print(f'Starting up redirect server trying following ports: {", ".join(map(str, self.__AVAILABLE_PORTS))}')
        ports = self.__AVAILABLE_PORTS
        while (len(ports) > 0 and
               (self.httpd is None or
                requests.get(self.get_server_address()).status_code != 200)):
            try:
                port = ports.pop()
                self.server_address = ('localhost', port)
                print(f'Starting up redirect server at {self.get_server_address()}')
                self.httpd = HTTPServer(self.server_address, BaseHTTPRequestHandler)
                self.httpd.serve_forever()
            except OSError as e:
                # Address already in use
                if e.errno == 98:
                    print(f'Address already in use {self.get_server_address()}')
                    if len(ports) > 0:
                        print('Trying another port...')
                    else:
                        print('Run out of available ports.')
                        print(f'Make sure that on ouf those supported ports are available: '
                              f'{", ".join(map(str, self.__AVAILABLE_PORTS))}')
                        return e.errno
                else:
                    print(f'ERROR: {e}')
                    return e.errno
        print('Shutting down redirect server')
        return 0
