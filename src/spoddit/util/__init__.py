import logging
from functools import reduce
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path
import configparser as cp

import requests
import operator

logger = logging.getLogger(__name__)


def get_nested(data_dict, path, separator='.'):
    return reduce(operator.getitem, path.split(separator), data_dict)


def parse_config(config_path, defaults=None):

    if defaults is None:
        defaults = {}

    config = None

    # config file location passed by arguments
    if Path(config_path).is_file():
        config = cp.ConfigParser()
        config.read([config_path])
        defaults.update(dict(config.items()))
        logger.debug(dict(config.items())) if config is not None else logging.debug('No config provided')

    if config is not None:
        logger.debug('CONFIG:')
        for section in config.sections():

            logger.debug(f'{section}')
            for (key, value) in config.items(section):
                logger.debug(f'  {key} = {value}')
    else:
        logger.warning(f'config "{config_path}" not found')

    return config



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
