// Controles de toque para celular/tablet (pyKombat no navegador).
//
// Desenha um controle virtual por cima do jogo — direcional à esquerda e os
// botões à direita, para jogar com o celular deitado — e o expõe ao Python
// como mais um controle: window.pkTouchPad() devolve uma entrada no mesmo
// formato de window.pkPads() (net.js), com os botões no layout "standard" da
// Gamepad API. Assim menus e luta funcionam sem nada específico de toque.
//
// Também: no primeiro toque pede tela cheia e trava a tela deitada (onde o
// navegador deixa) e, com o celular em pé, mostra um aviso para girá-lo; e
// retoma o áudio que o celular suspende (window.pkResumeAudio).
//
// ?touch=1 força os controles (para testar no PC); ?touch=0 desliga.
(function () {
  'use strict';

  const params = new URLSearchParams(window.location.search);
  const force = params.get('touch');
  const isTouch = force === '1' || (force !== '0' && (
    (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) ||
    ('ontouchstart' in window && navigator.maxTouchPoints > 0)));

  // bits do layout "standard" (mesmos índices de STD_BUTTONS em src/inputs.py)
  const B = { LK: 0, HK: 1, LP: 2, HP: 3, SPECIAL: 4, BLOCK: 5, FATAL: 6,
              BACK: 8, START: 9, UP: 12, DOWN: 13, LEFT: 14, RIGHT: 15 };

  let bits = 0;          // botões segurados agora
  let stickId = null;    // toque que controla o direcional
  let stickBits = 0;

  window.pkTouchPad = function () {
    if (!isTouch) return '';
    return 'touch:' + (bits | stickBits) + '::standard:Touch controls';
  };

  // Áudio: o celular suspende o AudioContext quando a página perde o foco (ex.:
  // a caixa de texto do código da sala) e ele não volta sozinho. Guarda os
  // contextos que o jogo criar e os retoma no próximo toque/tecla ou ao voltar.
  const audioCtxs = [];
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) {
      const Wrapped = function (opts) {
        const c = opts === undefined ? new AC() : new AC(opts);
        audioCtxs.push(c);
        return c;
      };
      Wrapped.prototype = AC.prototype;
      window.AudioContext = Wrapped;
      if (window.webkitAudioContext) window.webkitAudioContext = Wrapped;
    }
  } catch (e) { /* sem Web Audio */ }
  window.pkResumeAudio = function () {
    for (const c of audioCtxs) {
      try { if (c.state !== 'running') c.resume().catch(function () {}); } catch (e) { /* fechado */ }
    }
  };
  for (const ev of ['touchend', 'mousedown', 'keydown', 'focus']) {
    window.addEventListener(ev, window.pkResumeAudio, true);
  }
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) window.pkResumeAudio();
  });

  if (!isTouch) return;

  const css = `
    body.pk-touch, body.pk-touch canvas { touch-action: none; -webkit-user-select: none; user-select: none;
      -webkit-touch-callout: none; overscroll-behavior: none; }
    #pk-touch { position: fixed; inset: 0; z-index: 50; pointer-events: none; display: none;
      font-family: 'Trebuchet MS', arial, sans-serif; }
    #pk-touch.on { display: block; }
    #pk-touch .pk-ctl { pointer-events: auto; position: absolute; touch-action: none; }
    #pk-stick { left: calc(env(safe-area-inset-left, 0px) + 3vmin); bottom: 4vmin;
      width: 36vmin; height: 36vmin; border-radius: 50%;
      background: radial-gradient(circle, rgba(255,255,255,.10) 0%, rgba(255,255,255,.04) 70%);
      border: 2px solid rgba(232,185,35,.45); }
    #pk-knob { position: absolute; left: 50%; top: 50%; width: 15vmin; height: 15vmin; margin: -7.5vmin 0 0 -7.5vmin;
      border-radius: 50%; background: rgba(232,185,35,.45); border: 2px solid rgba(255,230,150,.6);
      pointer-events: none; }
    .pk-btn { width: 14vmin; height: 14vmin; border-radius: 50%; display: flex; align-items: center;
      justify-content: center; color: #fff; font-weight: bold; font-size: 3vmin; letter-spacing: 1px;
      text-shadow: 0 0 3px #000; border: 2px solid rgba(255,255,255,.45); opacity: .55;
      box-sizing: border-box; }
    .pk-btn.down { opacity: .95; transform: scale(.94); }
    .pk-btn.pk-long { font-size: 2.3vmin; letter-spacing: 0; }
    .pk-p { background: rgba(176,0,0,.55); }
    .pk-k { background: rgba(30,90,200,.55); }
    .pk-s { background: rgba(232,160,20,.6); }
    .pk-b { background: rgba(90,90,90,.6); }
    .pk-f { background: rgba(110,0,0,.7); width: 10vmin; height: 10vmin; font-size: 2.4vmin; }
    .pk-sys { height: 7vmin; padding: 0 3vmin; border-radius: 4vmin; width: auto; font-size: 2.6vmin;
      background: rgba(0,0,0,.5); top: 2vmin; }
    #pk-rotate { position: fixed; inset: 0; z-index: 1000000; display: none; background: #000;
      color: #e8b923; font-weight: bold; text-transform: uppercase; letter-spacing: 3px;
      align-items: center; justify-content: center; flex-direction: column; text-align: center; }
    #pk-rotate .pk-phone { width: 14vmin; height: 24vmin; border: 4px solid #e8b923; border-radius: 2.5vmin;
      margin-bottom: 5vmin; animation: pkrot 1.8s ease-in-out infinite; }
    @keyframes pkrot { 0%, 25% { transform: rotate(0deg); } 60%, 100% { transform: rotate(-90deg); } }
    @media (orientation: portrait) { body.pk-touch #pk-rotate { display: flex; } }
  `;

  // [rótulo, bit, classe, direita (vmin), baixo (vmin)]
  const BUTTONS = [
    ['LP', B.LP, 'pk-p', 35, 21], ['HP', B.HP, 'pk-p', 19, 25], ['SPECIAL', B.SPECIAL, 'pk-s', 3, 29],
    ['LK', B.LK, 'pk-k', 35, 4], ['HK', B.HK, 'pk-k', 19, 8], ['BLOCK', B.BLOCK, 'pk-b', 3, 12],
    ['FATAL', B.FATAL, 'pk-f', 6, 46],
  ];

  function build() {
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    document.body.classList.add('pk-touch');

    const root = document.createElement('div');
    root.id = 'pk-touch';
    root.innerHTML = '<div id="pk-stick" class="pk-ctl"><div id="pk-knob"></div></div>';
    for (const [label, bit, cls, right, bottom] of BUTTONS) {
      const b = document.createElement('div');
      b.className = 'pk-ctl pk-btn ' + cls + (label.length > 4 ? ' pk-long' : '');
      b.dataset.bit = bit;
      b.textContent = label;
      b.style.right = 'calc(env(safe-area-inset-right, 0px) + ' + right + 'vmin)';
      b.style.bottom = bottom + 'vmin';
      root.appendChild(b);
    }
    // pausa / voltar (menus) no topo, longe dos polegares
    // (nos cantos, fora da barra de vida e do relógio)
    for (const [label, bit, side] of [['BACK', B.BACK, 'left'], ['PAUSE', B.START, 'right']]) {
      const b = document.createElement('div');
      b.className = 'pk-ctl pk-btn pk-sys';
      b.dataset.bit = bit;
      b.textContent = label;
      b.style[side] = 'calc(env(safe-area-inset-' + side + ', 0px) + 2vmin)';
      root.appendChild(b);
    }
    document.body.appendChild(root);

    const rot = document.createElement('div');
    rot.id = 'pk-rotate';
    rot.innerHTML = '<div class="pk-phone"></div>Rotate your phone';
    document.body.appendChild(rot);

    const opts = { passive: false };
    root.addEventListener('touchstart', onTouch, opts);
    root.addEventListener('touchmove', onTouch, opts);
    root.addEventListener('touchend', onTouch, opts);
    root.addEventListener('touchcancel', onTouch, opts);
    // o primeiro toque em qualquer lugar (gesto do usuário) libera tela cheia e trava deitado
    document.addEventListener('touchend', landscape, { once: true });

    // só mostra depois que o jogo carregou (some a tela de download)
    const timer = setInterval(function () {
      const tr = document.getElementById('transfer');
      if (!tr || tr.hidden || tr.style.display === 'none') {
        root.classList.add('on');
        clearInterval(timer);
      }
    }, 400);
  }

  function landscape() {
    const el = document.documentElement;
    const req = el.requestFullscreen || el.webkitRequestFullscreen;
    let p = null;
    try { p = req ? req.call(el, { navigationUI: 'hide' }) : null; } catch (e) { p = null; }
    const lock = function () {
      try {
        if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(function () {});
      } catch (e) { /* iOS: sem trava; fica o aviso para girar */ }
    };
    if (p && p.then) p.then(lock, lock); else lock();
  }

  function onTouch(e) {
    e.preventDefault();
    const stick = document.getElementById('pk-stick');
    let newBits = 0;
    let stickTouch = null;
    for (const t of e.touches) {
      if (stickId === null && e.type === 'touchstart' && stick.contains(t.target)) stickId = t.identifier;
      if (t.identifier === stickId) { stickTouch = t; continue; }
      // o botão sob o dedo agora (dá para deslizar de um botão para outro)
      const el = document.elementFromPoint(t.clientX, t.clientY);
      const btn = el && el.closest ? el.closest('.pk-btn') : null;
      if (btn) newBits |= 1 << Number(btn.dataset.bit);
    }
    if (stickTouch === null) stickId = null;
    updateStick(stick, stickTouch);
    const pressed = newBits & ~bits;
    if (pressed && navigator.vibrate) { try { navigator.vibrate(8); } catch (err) { /* sem vibração */ } }
    bits = newBits;
    for (const b of document.querySelectorAll('#pk-touch .pk-btn')) {
      b.classList.toggle('down', !!(bits & (1 << Number(b.dataset.bit))));
    }
  }

  function updateStick(stick, t) {
    const knob = document.getElementById('pk-knob');
    if (!t) {
      stickBits = 0;
      knob.style.transform = '';
      return;
    }
    const r = stick.getBoundingClientRect();
    const rad = r.width / 2;
    let dx = t.clientX - (r.left + rad);
    let dy = t.clientY - (r.top + rad);
    const len = Math.hypot(dx, dy);
    if (len > rad) { dx = dx / len * rad; dy = dy / len * rad; }
    knob.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
    // 8 direções: cada eixo conta a partir de ~38% do raio
    const dz = rad * 0.38;
    stickBits = 0;
    if (dx < -dz) stickBits |= 1 << B.LEFT;
    else if (dx > dz) stickBits |= 1 << B.RIGHT;
    if (dy < -dz) stickBits |= 1 << B.UP;
    else if (dy > dz) stickBits |= 1 << B.DOWN;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
