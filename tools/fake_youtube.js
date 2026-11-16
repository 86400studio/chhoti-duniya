// Stand-in for YouTube's player script, used only by the local tests (the sandbox cannot reach YouTube).
window.YT = { Player: function (id, opts) {
  var state = -1, t = 0, dur = 120, timer = null;
  function fire(s) { state = s; opts.events.onStateChange({ data: s }); }
  function run() { clearInterval(timer); timer = setInterval(function () { if (state === 1) { t += 0.5; if (t >= dur) { t = dur; clearInterval(timer); fire(0); } } }, 100); }
  this.loadVideoById = function (v) {
    var hit = (window.__cd ? window.__cd.catalog : []).filter(function (x) { return x.id === v; })[0];
    dur = hit ? hit.secs : 120; t = 0; clearInterval(timer); fire(3);
    setTimeout(function () { fire(1); run(); }, 150);
  };
  this.playVideo = function () { if (state !== 1) { fire(1); run(); } };
  this.pauseVideo = function () { if (state === 1 || state === 3) { fire(2); } };
  this.seekTo = function (x) { t = x; };
  this.getCurrentTime = function () { return t; };
  this.getDuration = function () { return dur; };
  this.getPlayerState = function () { return state; };
  this.stopVideo = function () {};
  window.__fake = this;
  setTimeout(function () { opts.events.onReady({}); }, 50);
} };
setTimeout(function () { if (window.onYouTubeIframeAPIReady) { window.onYouTubeIframeAPIReady(); } }, 20);
