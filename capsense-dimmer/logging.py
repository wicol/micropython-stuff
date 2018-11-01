import usocket
import config


class SocketLogger:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket_addr = usocket.getaddrinfo(host, port)[0][-1]
        self.is_connected = False
        self.socket = None

    def connect(self):
        try:
            print('Connecting to {}:{}'.format(self.host, self.port))
            self.socket = usocket.socket()
            self.socket.connect(self.socket_addr)
            print('Connected')
            self.is_connected = True
        except Exception as e:
            print('Could not connect to {}:{} due to: {}: {}'.format(
                self.host, self.port, type(e), e)
            )
        return self.is_connected

    def log(self, msg, level, stdout=False):
        lvl_msg = '{}: {}\n'.format(level, msg)
        if stdout:
            print(lvl_msg, end='')
        try:
            self.socket.send(lvl_msg)
        except:
            self.is_connected = False
            print('Failed sending msg: {}'.format(lvl_msg), end='')

    def debug(self, msg, stdout=False):
        self.log(msg, 'DEBUG', stdout)

    def info(self, msg, stdout=False):
        self.log(msg, 'INFO', stdout)

    def warning(self, msg, stdout=False):
        self.log(msg, 'WARNING', stdout)

    def error(self, msg, stdout=False):
        self.log(msg, 'ERROR', stdout)


logger = SocketLogger(config.SOCKET_LOGGER_HOST, config.SOCKET_LOGGER_PORT)
