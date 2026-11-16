// Candidate checker. Paste into the browser console (or run through a browser tool) on the LIVE site,
// because YouTube's player only works from the hosted https page. It uses YouTube's own player API to
// read a playlist (or a channel's uploads: "UU" + the channel id without its "UC") and then reports,
// for every video: title, length in seconds, and whether it can be embedded. Nothing is played aloud.
//
// Usage:  await cdScan({ infobells: 'UU1ciY6kR3yj3kaKZ6R7ewAg' }, ['extraVideoId1'])
// Result: window.__scan.vids = { id: { t: title, dur: seconds, ok: playable, e: errorCode } }
window.cdScan = async function (lists, extraIds) {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const out = window.__scan = { lists: {}, vids: {}, done: false };
  const make = i => new Promise(res => {
    const d = document.createElement('div'); d.id = 'scan' + i;
    d.style.cssText = 'position:fixed;right:' + (i % 4) * 124 + 'px;bottom:' + Math.floor(i / 4) * 70 + 'px;width:120px;height:68px;z-index:99';
    document.body.appendChild(d);
    const st = { err: null };
    const pl = new YT.Player('scan' + i, { width: 120, height: 68, playerVars: { origin: location.origin, playsinline: 1 },
      events: { onReady: () => { pl.mute(); res({ p: pl, st }); }, onError: e => { st.err = e.data; } } });
  });
  const players = await Promise.all([0, 1, 2, 3, 4, 5, 6, 7].map(make));   // 8 in parallel: background tabs throttle timers
  let k = 0;
  for (const [name, id] of Object.entries(lists || {})) {
    const p = players[k++ % players.length].p;
    p.cuePlaylist({ listType: 'playlist', list: id });
    let ids = null;
    for (let i = 0; i < 25; i++) { await wait(500); ids = p.getPlaylist(); if (ids && ids.length) { break; } }
    out.lists[name] = (ids || []).slice(0, 150);
  }
  const all = [...new Set(Object.values(out.lists).flat().concat(extraIds || []))];
  let idx = 0;
  await Promise.all(players.map(async ({ p, st }) => {
    while (idx < all.length) {
      const id = all[idx++]; st.err = null; p.cueVideoById(id); let d = null;
      for (let i = 0; i < 8; i++) {
        await wait(300); try { d = p.getVideoData(); } catch (e) { /* ignore */ }
        if (st.err !== null) { break; }
        if (d && d.video_id === id && p.getPlayerState() === 5 && p.getDuration() > 0) { break; }
      }
      out.vids[id] = { t: (d && d.video_id === id) ? d.title : '', dur: Math.round(p.getDuration() || 0), ok: st.err === null && !!d && d.video_id === id && d.isPlayable !== false, e: st.err };
    }
  }));
  out.done = true;
  return Object.keys(out.vids).length;
};
