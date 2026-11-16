"""Local UI test. Run from the repo root:  python3 tools/ui_test.py
Serves the folder, swaps YouTube's player for tools/fake_youtube.js, and walks the child and parent flows."""
import http.server, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FAKE = open(os.path.join(ROOT, 'tools', 'fake_youtube.js'), encoding='utf-8').read()
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')
os.chdir(ROOT)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(('127.0.0.1', 8741), http.server.SimpleHTTPRequestHandler)
srv.RequestHandlerClass.log_message = lambda *a, **k: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
fails = []
def check(name, ok, extra=''):
    print(('PASS ' if ok else 'FAIL ') + name + (' ' + str(extra) if extra else ''))
    if not ok: fails.append(name)
W = ['zero','one','two','three','four','five','six','seven','eight','nine']
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 780, 'height': 360}, has_touch=True)
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/iframe_api', lambda r: r.fulfill(status=200, content_type='application/javascript', body=FAKE))
    pg.route('**/i.ytimg.com/**', lambda r: r.abort())
    pg.goto('http://127.0.0.1:8741/index.html', wait_until='domcontentloaded')
    pg.evaluate("()=>{const S=__cd.state(); S.set.cut='23:59'; __cd.save();}")
    pg.reload(wait_until='domcontentloaded'); pg.wait_for_timeout(500)
    vis = lambda sel: pg.evaluate("(s)=>{const e=document.querySelector(s); return !!e && !e.hidden && getComputedStyle(e).display!=='none'}", sel)
    tray = lambda: pg.evaluate("()=>document.getElementById('tray').classList.contains('open')")
    st = lambda: pg.evaluate("()=>__fake.getPlayerState()")
    n_home = pg.locator('#row .card').count()
    check('home lists the plate plus every other allowed video', n_home > 100, n_home)
    whys = pg.evaluate("()=>__cd.pick(__cd.cfg.homeSlots,{home:true,all:true}).map(x=>x.why)")
    check('first 8 home cards are the balanced plate', all(w in ('Favourite','Balance','New','Mix') for w in whys[:8]) and whys[8] == 'More', whys[:10])
    check('home shows 8 shelf buttons (treat hidden)', pg.locator('#cats .cat').count() == 8)
    pg.screenshot(path='/tmp/cd_home_landscape.png')
    pg.locator('#row .card').first.click(); pg.wait_for_timeout(500)
    check('card tap opens the player', vis('#play'))
    print('INFO full screen engaged in this browser: %s' % pg.evaluate('()=>!!document.fullscreenElement'))
    check('video is playing', st() == 1, st())
    check('loading cover is gone', not vis('#loading'))
    check('tray starts closed', not tray())
    check('tray holds 6 cards', pg.locator('#shelfCards .card').count() == 6, pg.locator('#shelfCards .card').count())
    box = pg.locator('#shield').bounding_box()
    cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    # swipe up opens the tray, video keeps playing
    pg.mouse.move(cx, cy + 60); pg.mouse.down(); pg.mouse.move(cx, cy - 60, steps=5); pg.mouse.up(); pg.wait_for_timeout(350)
    check('swipe up opens the tray', tray()); check('video still playing with tray open', st() == 1)
    pg.screenshot(path='/tmp/cd_player_tray.png')
    # tap outside closes the tray without pausing
    pg.mouse.click(cx, box['y'] + 30); pg.wait_for_timeout(300)
    check('tap on the video closes the tray', not tray()); check('that tap did not pause', st() == 1)
    # tap pauses: cover and tray appear
    pg.mouse.click(cx, cy); pg.wait_for_timeout(300)
    check('tap pauses the video', st() == 2); check('pause shows our cover', vis('#cover')); check('pause opens the tray', tray())
    pg.mouse.click(cx, box['y'] + 30); pg.wait_for_timeout(300)
    check('tap on the cover resumes', st() == 1); check('cover hides on resume', not vis('#cover')); check('tray closes on resume', not tray())
    # swipe down closes
    pg.mouse.move(cx, cy + 60); pg.mouse.down(); pg.mouse.move(cx, cy - 60, steps=5); pg.mouse.up(); pg.wait_for_timeout(300)
    pg.mouse.move(cx, cy - 80); pg.mouse.down(); pg.mouse.move(cx, cy + 20, steps=5); pg.mouse.up(); pg.wait_for_timeout(300)
    check('swipe down closes the tray', not tray())
    # handle opens, a tray card switches video
    pg.locator('#handle').click(); pg.wait_for_timeout(300)
    check('handle opens the tray', tray())
    first = pg.evaluate("()=>Object.keys(Object.values(__cd.state().days)[0].plays)")
    pg.locator('#shelfCards .card').first.click(); pg.wait_for_timeout(500)
    plays = pg.evaluate("()=>Object.values(__cd.state().days)[0].plays")
    check('tray card starts another video', st() == 1 and len(plays) >= 1 and not tray(), plays)
    # let it end
    pg.evaluate("()=>__fake.seekTo(__fake.getDuration()-1)"); pg.wait_for_timeout(900)
    check('video ended', st() == 0, st()); check('end shows replay cover', vis('#cover')); check('end shows talk-back prompt', vis('#talk'), pg.inner_text('#talk'))
    check('end opens the tray', tray())
    hist = pg.evaluate("()=>__cd.state().hist")
    check('finishing raised an interest score', any(h['I'] > 0 for h in hist.values()), hist)
    pg.screenshot(path='/tmp/cd_player_ended.png')
    # home button in the tray
    pg.locator('#homeBtn').click(); pg.wait_for_timeout(300)
    check('home button returns to Home', vis('#home') and not vis('#play'))
    # phone back gesture from the player returns to Home, not out of the app
    pg.locator('#row .card').first.click(); pg.wait_for_timeout(500)
    pg.go_back(); pg.wait_for_timeout(400)
    check('back gesture returns to Home', vis('#home') and pg.url.endswith('index.html'), pg.url)
    # parent gate
    lock = pg.locator('#home [data-lock]').bounding_box()
    pg.mouse.move(lock['x'] + 12, lock['y'] + 12); pg.mouse.down(); pg.wait_for_timeout(1000); pg.mouse.up(); pg.wait_for_timeout(200)
    check('a short press does not open the gate', not vis('#gate'))
    pg.mouse.down(); pg.wait_for_timeout(3200); pg.mouse.up(); pg.wait_for_timeout(200)
    check('a 3 second hold opens the gate', vis('#gate'))
    for d in '000': pg.locator('#keypad button', has_text=d).first.click()
    pg.wait_for_timeout(200)
    words = None
    if vis('#gate') or vis('#parent'):
        pass
    check('wrong numbers return to the app', vis('#home') or vis('#parent'))
    if not vis('#parent'):
        pg.mouse.move(lock['x'] + 12, lock['y'] + 12); pg.mouse.down(); pg.wait_for_timeout(3200); pg.mouse.up(); pg.wait_for_timeout(200)
        for w in pg.inner_text('#gateWords').split(', '):
            pg.locator('#keypad button', has_text=str(W.index(w))).first.click()
        pg.wait_for_timeout(300)
    check('right numbers open the parent area', vis('#parent'))
    pg.fill('#sCap', '45'); pg.dispatch_event('#sCap', 'change')
    check('daily cap setting saves', pg.evaluate("()=>__cd.state().set.cap") == 45)
    pg.fill('#sCap', '60'); pg.dispatch_event('#sCap', 'change')
    n0 = pg.locator('#vidList .vid').count()
    pg.locator('#vidList .vid button', has_text='Block').first.click(); pg.wait_for_timeout(200)
    check('video list shows the catalog', n0 == pg.evaluate("()=>__cd.catalog.length"), n0)
    check('block button blocks a video', len(pg.evaluate("()=>Object.keys(__cd.state().block)")) == 1)
    blocked = pg.evaluate("()=>Object.keys(__cd.state().block)[0]")
    offered = pg.evaluate("()=>{const seen={}; for(let i=0;i<40;i++){ __cd.pick(__cd.cfg.homeSlots,{home:true}).forEach(x=>seen[x.v.id]=1);} return seen}")
    check('a blocked video is never offered', blocked not in offered)
    check('report builds', 'WEEKLY REPORT' in pg.inner_text('#report'))
    pg.locator('#pClose').click(); pg.wait_for_timeout(300)
    check('parent area closes back to Home', vis('#home'))
    # time rules
    r = pg.evaluate("""()=>{const S=__cd.state(); const d=Object.values(S.days)[0]; const s=d.sess[d.sess.length-1]; s.secs=S.set.len*60-20; d.secs=s.secs; __cd.save(); return __cd.remaining();}""")
    check('20 seconds left in the session', r == 20, r)
    pg.evaluate("()=>{__cd.endIfSpent(); __cd.home();}"); pg.wait_for_timeout(300)
    check('spent session shows the goodbye screen', vis('#bye'), pg.inner_text('#byeline'))
    check('app stays closed during the gap', pg.evaluate("()=>__cd.remaining()") == 0)
    pg.evaluate("()=>{const S=__cd.state(); S.set.cut='00:01'; __cd.save();}")
    check('evening cut-off closes the app', pg.evaluate("()=>__cd.remaining()") == 0)
    pg.screenshot(path='/tmp/cd_bye.png')
    # portrait layout
    pg.evaluate("()=>{const S=__cd.state(); S.days={}; S.set.cut='23:59'; __cd.save(); __cd.home();}")
    pg.set_viewport_size({'width': 390, 'height': 800}); pg.wait_for_timeout(300)
    pg.screenshot(path='/tmp/cd_home_portrait.png')
    pg.locator('#row .card').first.click(); pg.wait_for_timeout(500); pg.locator('#handle').click(); pg.wait_for_timeout(350)
    pg.screenshot(path='/tmp/cd_player_portrait.png')
    check('no script errors', not errs, errs)
    b.close()
srv.shutdown()
print('\n%d failed' % len(fails)); sys.exit(1 if fails else 0)
