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

  function peerOptions() {
    const o = { debug: 1 };
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
  };

  net.host = function (code) {
    net.close();
    if (typeof Peer === 'undefined') { net.state = 'error'; net.error = 'peerjs-missing'; return; }
    net.code = String(code);
    net.state = 'connecting';
    const peer = new Peer(PREFIX + net.code, peerOptions());
    net.peer = peer;
    peer.on('open', function () { if (net.state !== 'open') net.state = 'waiting'; });
    peer.on('connection', function (c) {
      if (net.conn && net.conn.open) { c.on('open', function () { c.close(); }); return; }
      wire(c);
      if (c.open) net.state = 'open';
    });
    peer.on('disconnected', function () {
      // perdeu o servidor de sinalização; a conexão P2P (se houver) continua
      if (net.state === 'waiting') { try { peer.reconnect(); } catch (e) { /* ignora */ } }
    });
    peer.on('error', function (e) { net.state = 'error'; net.error = String(e && e.type || e); });
  };

  net.join = function (code) {
    net.close();
    if (typeof Peer === 'undefined') { net.state = 'error'; net.error = 'peerjs-missing'; return; }
    net.code = String(code).toUpperCase();
    net.state = 'connecting';
    const peer = new Peer(peerOptions());
    net.peer = peer;
    peer.on('open', function () {
      wire(peer.connect(PREFIX + net.code, { reliable: true, serialization: 'raw' }));
    });
    peer.on('error', function (e) { net.state = 'error'; net.error = String(e && e.type || e); });
    // sala inexistente/inalcançável: não fica "conectando" para sempre
    setTimeout(function () {
      if (net.peer === peer && net.state === 'connecting') {
        net.state = 'error';
        net.error = 'peer-unavailable';
      }
    }, 15000);
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
