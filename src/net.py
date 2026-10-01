# Multiplayer online: salas com código para jogar com amigos.
#
# Navegador: WebRTC (PeerJS, ver web/net.js). O host registra o id
#   "pykombat-v1-<CÓDIGO>" no servidor de sinalização e o amigo conecta direto
#   nele (peer-to-peer). Basta compartilhar o código ou o link ?room=CÓDIGO.
# Desktop: TCP direto. O "código" é IP:PORTA do host (rede local ou porta
#   liberada no roteador).
#
# Modelo: o host simula a luta e manda o snapshot de cada tick; o convidado
# manda só os botões que está apertando. Mensagens são JSON (uma por linha).
import json
import random
import sys

WEB = sys.platform == 'emscripten'
PORT = 7777
CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def newCode(n=5):
    return ''.join(random.choice(CODE_CHARS) for _ in range(n))


def encode(msg):
    return json.dumps(msg, separators=(',', ':'))


def decode(raw):
    try:
        return json.loads(raw)
    except Exception:
        return None


class WebTransport:
    """Ponte para window.pkNet (JS, web/net.js)."""

    def __init__(self):
        import platform
        self.js = platform.window.pkNet
        self.code = ''
        self.state = 'idle'
        self.error = ''

    def host(self, code):
        self.code = code
        self.js.host(code)

    def join(self, code):
        self.code = code
        self.js.join(code)

    def poll(self):
        st = str(self.js.status())
        self.state, _, self.error = st.partition('|')

    def send(self, msg):
        self.js.send(encode(msg))

    def recv(self):
        raw = str(self.js.recv())
        if not raw:
            return []
        out = []
        for line in raw.split('\n'):
            m = decode(line)
            if m is not None:
                out.append(m)
        return out

    def close(self):
        try:
            self.js.close()
        except Exception:
            pass
        self.state = 'closed'

    def shareUrl(self):
        try:
            return str(self.js.shareUrl(self.code))
        except Exception:
            return ''

    def copy(self, text):
        try:
            self.js.copy(text)
            return True
        except Exception:
            return False


class TcpTransport:
    """Desktop: socket TCP não bloqueante, mensagens separadas por '\\n'."""

    def __init__(self):
        self.code = ''
        self.state = 'idle'
        self.error = ''
        self.server = None
        self.sock = None
        self.buf = b''
        self.out = b''

    def host(self, code=None, port=PORT):
        import socket
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(1)
            self.server.setblocking(False)
            self.code = '%s:%d' % (localIp(), port)
            self.state = 'waiting'
        except OSError as e:
            self.state, self.error = 'error', str(e)

    def join(self, code):
        import socket
        host, _, port = code.strip().partition(':')
        self.code = code
        try:
            self.sock = socket.create_connection((host, int(port or PORT)), timeout=4)
            self._setup()
            self.state = 'open'
        except (OSError, ValueError) as e:
            self.state, self.error = 'error', str(e)

    def _setup(self):
        import socket
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def poll(self):
        if self.server is not None and self.sock is None:
            try:
                self.sock, _ = self.server.accept()
                self._setup()
                self.state = 'open'
            except BlockingIOError:
                pass
            except OSError as e:
                self.state, self.error = 'error', str(e)
        self._flush()

    def _flush(self):
        if self.sock is None or not self.out:
            return
        try:
            n = self.sock.send(self.out)
            self.out = self.out[n:]
        except BlockingIOError:
            pass
        except OSError as e:
            self.state, self.error = 'closed', str(e)

    def send(self, msg):
        if self.sock is None or self.state != 'open':
            return
        self.out += (encode(msg) + '\n').encode()
        self._flush()

    def recv(self):
        if self.sock is None or self.state != 'open':
            return []
        try:
            while True:
                chunk = self.sock.recv(65536)
                if not chunk:
                    self.state = 'closed'
                    break
                self.buf += chunk
        except BlockingIOError:
            pass
        except OSError as e:
            self.state, self.error = 'closed', str(e)
        out = []
        while b'\n' in self.buf:
            line, self.buf = self.buf.split(b'\n', 1)
            m = decode(line.decode('utf-8', 'replace'))
            if m is not None:
                out.append(m)
        return out

    def close(self):
        for s in (self.sock, self.server):
            if s is not None:
                try:
                    s.close()
                except OSError:
                    pass
        self.sock = self.server = None
        self.state = 'closed'

    def shareUrl(self):
        return ''

    def copy(self, text):
        return False


def localIp():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return '127.0.0.1'


def transport():
    return WebTransport() if WEB else TcpTransport()


def roomFromUrl():
    """Código de sala vindo do link compartilhado (?room=XXXXX), só no navegador."""
    if not WEB:
        return ''
    try:
        import platform
        return str(platform.window.pkNet.roomFromUrl() or '')
    except Exception:
        return ''
