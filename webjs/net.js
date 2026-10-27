// Ponte JS <-> Python (pygbag) para o pyKombat no navegador:
//  * window.pkPads(): estado dos controles (Gamepad API) — DualSense, Xbox etc.
//    pareados por Bluetooth/USB aparecem aqui com o layout "standard" — e o
//    controle virtual de toque do celular (touch.js).
//  * window.pkNet: salas online via WebRTC (PeerJS). O host registra
//    "pykombat-v1-<CODE>" no servidor de sinalização; o convidado conecta nele.
//    Depois disso o tráfego é peer-to-peer.
//
// Para testar com um servidor PeerJS próprio: ?peerhost=localhost&peerport=9000
(function () {
  'use strict';

  // ---------------------------------------------------------------- gamepads
  window.pkPads = function () {
    const out = [];
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (let i = 0; i < pads.length; i++) {
      const g = pads[i];
      if (!g || !g.connected) continue;
      let bits = 0;
      for (let b = 0; b < g.buttons.length && b < 31; b++) {
        const btn = g.buttons[b];
        if (btn && (btn.pressed || btn.value > 0.5)) bits |= (1 << b);
      }
      const axes = [];
      for (let a = 0; a < g.axes.length && a < 4; a++) axes.push(g.axes[a].toFixed(2));
      const name = String(g.id || 'gamepad').replace(/[|:]/g, ' ').slice(0, 40);
      out.push(g.index + ':' + bits + ':' + axes.join(',') + ':' + g.mapping + ':' + name);
    }
    // controle virtual de toque (touch.js), no celular/tablet
    const touch = window.pkTouchPad ? window.pkTouchPad() : '';
    if (touch) out.push(touch);
    return out.join('|');
  };

  // ---------------------------------------------------------------- rede
  const PREFIX = 'pykombat-v1-';
  const params = new URLSearchParams(window.location.search);

  // STUN extras + os TURN públicos do PeerJS (que não são confiáveis). Para
  // passar NAT de operadora (4G/5G) costuma ser preciso um TURN próprio:
  // ?turn=turn:host:3478&turnuser=USUARIO&turnpass=SENHA
  function iceServers() {
    const list = [
      { urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] },
      { urls: 'stun:stun.cloudflare.com:3478' },
      { urls: ['turn:eu-0.turn.peerjs.com:3478', 'turn:us-0.turn.peerjs.com:3478'],
        username: 'peerjs', credential: 'peerjsp' },
    ];
    if (params.get('turn')) {
      list.push({ urls: params.get('turn').split(','), username: params.get('turnuser') || '',
                  credential: params.get('turnpass') || '' });
    }
    return list;
  }

  function peerOptions() {
    const o = { debug: 1, config: { iceServers: iceServers(), sdpSemantics: 'unified-plan' } };
    if (params.get('peerhost')) {
      o.host = params.get('peerhost');
      o.port = Number(params.get('peerport') || 9000);
      o.path = params.get('peerpath') || '/';
      o.secure = params.get('peersecure') === '1';
    }
    return o;
  }

  const net = {
    state: 'idle',   // idle | connecting | waiting | open | closed | error
    error: '',
    code: '',
    inbox: [],
    peer: null,
    conn: null,
    role: '',      // host | guest
  };

  function wire(conn) {
    net.conn = conn;
    conn.on('open', function () { net.state = 'open'; });
    conn.on('data', function (d) {
      net.inbox.push(typeof d === 'string' ? d : JSON.stringify(d));
    });
    conn.on('close', function () { if (net.conn === conn) net.state = 'closed'; });
    conn.on('error', function (e) { net.state = 'error'; net.error = String(e && e.type || e); });
  }

  net.close = function () {
    try { if (net.conn) net.conn.close(); } catch (e) { /* ignora */ }
    try { if (net.peer) net.peer.destroy(); } catch (e) { /* ignora */ }
    net.conn = null;
    net.peer = null;
    net.inbox = [];
    net.state = 'idle';
    net.error = '';
    net.role = '';
  };

  // erros do servidor de sinalização (não da sala em si): dá para tentar de novo
  const SERVER_ERRORS = ['network', 'socket-error', 'socket-closed', 'server-error', 'disconnected'];

  function startHost() {
    const peer = new Peer(PREFIX + net.code, peerOptions());
    net.peer = peer;
    peer.on('open', function () {
      if (net.peer === peer && net.state !== 'open') { net.state = 'waiting'; net.error = ''; }
    });
    peer.on('connection', function (c) {
      if (net.conn && net.conn.open) { c.on('open', function () { c.close(); }); return; }
      wire(c);
      if (c.open) net.state = 'open';
    });
    peer.on('disconnected', function () {
      // perdeu o servidor de sinalização (ex.: celular trocou de app para mandar
      // o código); a conexão P2P (se houver) continua. Sem ele a sala some.
      if (net.peer !== peer) return;
      if (net.state !== 'open') net.state = 'connecting';
      setTimeout(keepHosting, 1000);
    });
    peer.on('error', function (e) {
      const type = String(e && e.type || e);
      if (net.peer !== peer) return;
      if (net.state !== 'open' && SERVER_ERRORS.indexOf(type) >= 0) {
        net.state = 'connecting';
        setTimeout(keepHosting, 2000);
        return;
      }
      net.state = 'error';
      net.error = type;
    });
  }

  // host: mantém a sala registrada no servidor enquanto espera o amigo
  function keepHosting() {
    const peer = net.peer;
    if (!peer || net.role !== 'host' || net.state === 'open' || net.state === 'error') return;
    if (document.hidden) return;   // o navegador congela a aba; tenta ao voltar
    if (peer.destroyed) startHost();
    else if (peer.disconnected) { try { peer.reconnect(); } catch (e) { /* ignora */ } }
  }
  document.addEventListener('visibilitychange', keepHosting);
  window.addEventListener('online', keepHosting);

  net.host = function (code) {
    net.close();
    if (typeof Peer === 'undefined') { net.state = 'error'; net.error = 'peerjs-missing'; return; }
    net.role = 'host';
    net.code = String(code);
    net.state = 'connecting';
    startHost();
  };

  net.join = function (code) {
    net.close();
    if (typeof Peer === 'undefined') { net.state = 'error'; net.error = 'peerjs-missing'; return; }
    net.role = 'guest';
    net.code = String(code).toUpperCase();
    net.state = 'connecting';
    const peer = new Peer(peerOptions());
    net.peer = peer;
    let signaled = false;
    peer.on('open', function () {
      signaled = true;
      wire(peer.connect(PREFIX + net.code, { reliable: true, serialization: 'raw' }));
    });
    peer.on('error', function (e) { net.state = 'error'; net.error = String(e && e.type || e); });
    // não fica "conectando" para sempre. Se o servidor achou a sala mas a conexão
    // direta não abriu, o problema é a rede (NAT/firewall), não o código.
    setTimeout(function () {
      if (net.peer === peer && net.state === 'connecting') {
        net.state = 'error';
        net.error = signaled ? 'negotiation-failed' : 'server-unreachable';
      }
    }, 25000);
  };

  net.send = function (s) {
    if (net.conn && net.conn.open) {
      try { net.conn.send(String(s)); } catch (e) { net.state = 'error'; net.error = String(e); }
    }
  };

  // todas as mensagens pendentes, separadas por \n (JSON nunca contém \n cru)
  net.recv = function () {
    if (!net.inbox.length) return '';
    const s = net.inbox.join('\n');
    net.inbox = [];
    return s;
  };

  net.status = function () { return net.state + '|' + net.error; };
  net.roomFromUrl = function () { return (params.get('room') || '').toUpperCase(); };
  net.shareUrl = function (code) {
    const u = new URL(window.location.href);
    u.searchParams.set('room', code);
    return u.toString();
  };
  net.copy = function (text) {
    try { navigator.clipboard.writeText(String(text)); } catch (e) { /* ignora */ }
  };

  window.pkNet = net;
})();
