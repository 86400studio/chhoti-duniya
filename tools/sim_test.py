"""Engine simulation. Run from the repo root:  python3 tools/sim_test.py
Plays 21 simulated days (3 sessions a day) with a pretend child who loves some shelves and dislikes others,
then checks that the feed engine and the time rules behave as the PRD says."""
import http.server, json, os, socketserver, sys, threading
from collections import Counter, defaultdict
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
os.chdir(ROOT)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(('127.0.0.1', 8743), http.server.SimpleHTTPRequestHandler)
srv.RequestHandlerClass.log_message = lambda *a, **k: None
threading.Thread(target=srv.serve_forever, daemon=True).start()

CLOCK = """(() => { const R = Date; let off = 0;
  class D extends R { constructor(...a) { if (a.length === 0) { super(R.now() + off); } else { super(...a); } } static now() { return R.now() + off; } }
  window.__RealDate = R; window.__setAbs = ms => { off = ms - R.now(); }; window.Date = D; })();"""

SIM = """(days) => {
  let seed = 20261116; const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const c = window.__cd, LIKE = { animals: 0.9, rhymes: 0.85, action: 0.8, treat: 0.95, colours: 0.7, shapes: 0.15, letters: 0.3 };
  const like = s => (s in LIKE ? LIKE[s] : 0.6);
  const base = new window.__RealDate(); base.setHours(0, 0, 0, 0); const B = base.getTime();
  const log = [], sessions = [], thinking = [], seenSub = {};
  for (let d = 0; d < days; d++) {
    for (const hour of [8, 11.5, 15]) {
      let clock = B + d * 864e5 + hour * 36e5; window.__setAbs(clock);
      if (c.remaining() <= 0) { sessions.push({ d, closed: true }); continue; }
      let first = true, lastId = null, n = 0, byTime = false, lastEnergy = null, lastCat = 0;
      while (n < 60) {
        const offered = first ? c.pick(c.cfg.homeSlots, { home: true, all: true }) : c.pick(c.cfg.shelfSlots, { not: { [lastId]: 1 } });
        if (!offered.length) { byTime = true; break; }
        if (first) { thinking.push(offered.slice(0, 8).some(x => x.v.cat === 5)); }
        (first ? offered.slice(0, 9) : offered).forEach(x => { seenSub[x.v.sub] = (seenSub[x.v.sub] || 0) + 1; });
        const pool = first ? (rnd() < 0.25 ? offered : offered.slice(0, 9)) : offered;
        let ch;
        if (rnd() < 0.3) { ch = pool[Math.floor(rnd() * pool.length)]; }
        else { const w = pool.map(x => like(x.v.sub)); let t = rnd() * w.reduce((a, b) => a + b, 0); ch = pool[pool.length - 1]; for (let i = 0; i < pool.length; i++) { t -= w[i]; if (t <= 0) { ch = pool[i]; break; } } }
        const v = ch.v, L = like(v.sub), r = rnd();
        const frac = r < L ? 1 : (r < L + (1 - L) * 0.6 ? 0.1 : 0.5);
        const treatOk = v.cat === 9 ? c.treatEarned() : null;
        const playsBefore = c.playsToday(v.id);
        const leftBefore = c.remaining();
        c.sim(v.id, frac);
        clock += v.secs * frac * 1000; window.__setAbs(clock);
        log.push({ d, id: v.id, cat: v.cat, sub: v.sub, lang: v.lang, energy: v.energy, ch: v.ch, level: v.level, secs: Math.round(v.secs * frac), full: v.secs, frac, why: ch.why, treatOk, playsBefore, leftBefore, first });
        lastId = v.id; lastEnergy = v.energy; lastCat = v.cat; first = false; n++;
        c.endIfSpent();
        if (c.remaining() <= 0) { byTime = true; break; }
      }
      const S = c.state(), keys = Object.keys(S.days).sort(), day = S.days[keys[keys.length - 1]], se = day.sess[day.sess.length - 1];
      sessions.push({ d, closed: false, secs: se ? se.secs : 0, byTime, lastEnergy, lastCat, videos: n, daySecs: day.secs });
      c.endSession();
    }
  }
  // Direct check of the "not for her" rule: abandon one video on three separate days.
  const probe = 'TJhfl5vdxp4'; let pc = B + (days + 1) * 864e5 + 9 * 36e5;
  for (let i = 0; i < 3; i++) { window.__setAbs(pc + i * 864e5); c.sim(probe, 0.1); c.endSession(); }
  const S = c.state();
  const hideUnit = { hidden: !!(S.hide[probe] && S.hide[probe] > Date.now()), I: S.hist[probe].I, offeredAfter: c.pick(c.cfg.homeSlots, { home: true, all: true }).some(x => x.v.id === probe) };
  return { log, sessions, thinking, seenSub, hideUnit, subI: S.subI, hide: Object.keys(S.hide), levels: Object.fromEntries([...new Set(c.catalog.map(v => v.sub))].map(s => [s, c.levelOf(s)])), set: S.set, cfg: c.cfg, shares: Object.fromEntries(c.catalog.map(v => [v.cat, 1])) };
}"""

fails = []
def check(name, ok, extra=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' | ' + str(extra)) if extra != '' else ''))
    if not ok: fails.append(name)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    pg = b.new_page()
    pg.add_init_script(CLOCK)
    pg.route('**/iframe_api', lambda r: r.abort()); pg.route('**/i.ytimg.com/**', lambda r: r.abort()); pg.route('**/fonts.g*/**', lambda r: r.abort())
    pg.goto('http://127.0.0.1:8743/index.html', wait_until='domcontentloaded')
    R = pg.evaluate(SIM, 21)
    b.close()
srv.shutdown()

log, sess, cfg, st = R['log'], [s for s in R['sessions'] if not s['closed']], R['cfg'], R['set']
print('simulated: %d days, %d sessions, %d viewings, %.0f minutes' % (21, len(sess), len(log), sum(x['secs'] for x in log) / 60))

# --- time rules
cap, ln = st['cap'] * 60, st['len'] * 60
day_secs = defaultdict(int)
for x in log: day_secs[x['d']] += x['secs']
check('no session runs past its length (plus the 30 s fit allowance)', max(s['secs'] for s in sess) <= ln + cfg['fitSlackSecs'], 'longest %d s of %d' % (max(s['secs'] for s in sess), ln))
check('no day runs past the daily cap', max(day_secs.values()) <= cap + cfg['fitSlackSecs'], 'longest day %d min of %d' % (max(day_secs.values()) / 60, cap / 60))
check('three sessions a day at most', max(Counter(s['d'] for s in sess).values()) <= st['num'])
check('every offered video fitted the time left', all(x['full'] <= x['leftBefore'] + cfg['fitSlackSecs'] for x in log))
timed = [s for s in sess if s['byTime']]
calm = sum(1 for s in timed if s['lastEnergy'] == 'calm')
check('sessions that run out of time end on a calm video (80% or more)', timed and calm / len(timed) >= 0.8, '%d of %d' % (calm, len(timed)))

# --- guardrails
check('no video played more than twice in a day', all(x['playsBefore'] < cfg['maxPlaysPerDay'] for x in log))
treats = [x for x in log if x['cat'] == 9]
tpd = Counter(x['d'] for x in treats)
check('at most one treat video a day', (max(tpd.values()) if tpd else 0) <= cfg['treatPerDay'], 'most in one day: %d' % (max(tpd.values()) if tpd else 0))
check('treats only after two core videos were finished', len(treats) > 0 and all(x['treatOk'] for x in treats), '%d treats in 21 days' % len(treats))
check('a treat is never the last video of a session', not any(s['lastCat'] == 9 for s in sess))
run, mx, prev = 0, 0, None
for x in log:
    key = (x['d'], x['cat']); run = run + 1 if (prev == x['cat']) else 1; prev = x['cat']; mx = max(mx, run)
check('same shelf at most 3 in a row (2 by rule, 3 when choices run short)', mx <= 3, 'longest run %d' % mx)
check('a thinking video is on the first screen of every session until one is watched', all(R['thinking']), '%d of %d' % (sum(R['thinking']), len(R['thinking'])))

# --- balance, weeks 2 and 3 (after the engine has history)
late = [x for x in log if x['d'] >= 7]
tot = sum(x['secs'] for x in late)
hi = 100 * sum(x['secs'] for x in late if x['lang'] == 'hi') / tot
check('Hindi share lands near the 60% target (48 to 72)', 48 <= hi <= 72, '%.0f%%' % hi)
TARGET = {1: 20, 2: 20, 3: 10, 4: 12, 5: 12, 6: 8, 7: 8, 8: 5, 9: 5}
share = {c: 100 * sum(x['secs'] for x in late if x['cat'] == c) / tot for c in TARGET}
print('   shelf shares, weeks 2-3 (watched% / target%): ' + ', '.join('%d: %.0f/%d' % (c, share[c], TARGET[c]) for c in TARGET))
check('every core shelf gets watched', all(share[c] > 1.5 for c in range(1, 9)), {c: round(v, 1) for c, v in share.items()})
check('no shelf takes over (none above 2x its target plus 8 points)', all(share[c] <= 2 * TARGET[c] + 8 for c in TARGET))
check('treat shelf stays small (10% or less)', share[9] <= 10, '%.1f%%' % share[9])

# --- learning her taste
I = {k: v['I'] for k, v in R['subI'].items()}
print('   interest by subcategory: ' + ', '.join('%s %.2f' % (k, v) for k, v in sorted(I.items(), key=lambda kv: -kv[1])))
check('loved shelves score above disliked ones', min(I.get('animals', 0), I.get('rhymes', 0)) > max(I.get('shapes', 0), I.get('letters', 0)))
print('   times each subcategory was put in front of her: ' + ', '.join('%s %d' % kv for kv in sorted(R['seenSub'].items(), key=lambda kv: -kv[1])))
late_shapes = sum(1 for x in late if x['sub'] == 'shapes'); early_shapes = sum(1 for x in log if x['d'] < 7 and x['sub'] == 'shapes')
print('   disliked "shapes" viewings: week 1 = %d, weeks 2-3 = %d (per week %.1f)' % (early_shapes, late_shapes, late_shapes / 2))
hu = R['hideUnit']
check('a video abandoned three times is hidden and no longer offered', hu['hidden'] and not hu['offeredAfter'], 'interest %.2f' % hu['I'])
check('a level unlocks after enough finished viewings', any(v >= 2 for v in R['levels'].values()), {k: v for k, v in R['levels'].items() if v > 1})
uniq = len(set(x['id'] for x in log))
check('she sees a wide spread of the catalog (60% or more in 3 weeks)', uniq >= 0.6 * 138, '%d of 138 videos' % uniq)

print('\n%d failed' % len(fails)); sys.exit(1 if fails else 0)
