# Chhoti Duniya

A private, curated video app for one toddler (age 2 at launch, November 2026). Hindi and English only.
It replaces YouTube Kids on her father's phone: only approved videos, inside daily time limits, with a
feed engine that balances what she loves against what she is missing.

- Live: https://86400studio.github.io/chhoti-duniya/
- Repo: `86400studio/chhoti-duniya` (GitHub Pages serves `main`)
- Owner: 86400 (non-technical; works through Claude). Full product plan: the PRD doc "PRD: Curated Hindi + English Video App for a 2-Year-Old".

## 1. Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole app: markup, styles, script, and the catalog. No build step. |
| `manifest.json`, `icon-192.png`, `icon-512.png` | Lets Chrome install it to the home screen and open it full screen. |
| `tools/catalog.py` | Source of truth for the catalog. Run it to rewrite the CATALOG block in `index.html`. |
| `tools/scan_snippet.js` | Checks candidate videos (title, length, embeddable) through YouTube's own player, on the live page. |
| `tools/ui_test.py` | 43 UI checks against a stand-in player (`tools/fake_youtube.js`). |
| `tools/sim_test.py` | Simulates 21 days of viewing and checks the engine and the time rules. |
| `CLAUDE.md` | Short rules for Claude sessions. |

## 2. How the app works

**Screens.** Home (shelf buttons on top, then cards: first 8 are the engine's "plate", the rest are every
other allowed video, best first). Player (full-screen video; tap pauses; swipe up or the bottom handle opens
a tray of 6 recommendations plus a Home button). Goodbye (when time is up). Parent gate (hold the lock
3 seconds, type three numbers shown as words). Parent area (time rules, language mix, shelves, weekly
report, per-video thumbs up and block, backup).

**Player.** YouTube's embedded player (IFrame Player API, controls off). A transparent "tap guard" sits over
it so taps never reach YouTube's links; our own cover hides YouTube's paused and end screens. See section 7.

**Engine** (all numbers live in the `CFG` block at the top of the script):

- Signals per viewing: finished (80% or more) +1.0, came back within 7 days +1.5, partial 0, abandoned (under 25%) -1.0, parent thumbs up +2.0. A view under 3 seconds leaves no trace.
- Interest per video and per subcategory: `I = 0.8 * I + 0.2 * signal`, held between -1 and 1.5. A subcategory with under 3 viewings borrows its category average.
- Score: `0.30 quality + 0.30 subcategory interest + 0.15 video interest + 0.15 novelty + 0.10 balance need - 0.5 if already watched today`.
- Slots: Home plate 4 favourite + 2 balance + 2 new; tray 3 + 2 + 1. Every screen carries the Hindi share (default 60%), nudged by one card if the week drifts more than 10 points.
- Guardrails: 2 plays of a video per day; rest a shelf or channel after 2 in a row (unless that removes a whole language); one thinking video on the first screen of each session until one is watched; only videos that fit the time left; non-calm videos must leave 125 s for a calm closer; under 5 minutes left, calm videos only; treat shelf = 1 a day, after 2 finished core videos, never last; abandoned 3 times in a row = hidden 14 days.
- Levels: a subcategory moves up after 8 finished viewings across 4 different videos.

**Time rules** (defaults, changeable in the parent area): 60 minutes a day, 3 sessions of 20 minutes,
2 hours between sessions, nothing after 19:30. Only playing time counts. A session also closes after
30 idle minutes.

**State.** Everything is in the phone browser's localStorage under `cd_v1`: `set` (settings), `hist`
(per video), `subI` (per subcategory), `days` (per-day seconds, sessions, shelves, languages), `block`,
`blockCh`, `like`, `hide`, `done` (level progress), `errs`, `words`. There is no server. A new deploy
never touches this state; new catalog ids simply appear.

## 3. What the owner does

Daily: nothing. Optional: thumbs up or block a video in the parent area.
Monthly: opens the parent area, taps "Copy report", pastes it to Claude with the words
"Chhoti Duniya monthly refresh". Nothing else. He does not attach files; Claude works from this repo.

## 4. Monthly refresh procedure (for Claude)

1. Attach this repo with push access and read this file.
2. Read the pasted report: time per day, shelf shares against targets, language split, favourites, "not for her", blocked videos and channels, thumbs up, videos that would not play.
3. Edit `tools/catalog.py`:
   - remove videos he blocked, "not for her" videos, and videos that would not play;
   - add 10 to 20 new videos, aimed at shelves under their target share and at subcategories she loves;
   - keep Hindi and English each near half of the catalog.
4. Find candidates with `tools/scan_snippet.js` on the live page (needs a real browser; the sandbox cannot reach YouTube). Trusted channels so far and their upload lists are in section 6.
5. Apply the gates in section 5 to every candidate.
6. `python3 tools/catalog.py`, then both tests, then bump `CFG.version`, update the change log, commit, push to `main`.
7. Load the live link, confirm the version, play one new video, and report back: what was added, what was removed, what could not be checked.

## 5. Gates for a new video

Checked by machine (scan snippet): embeddable; 90 to 600 seconds (treats up to 600).
Checked by judgement from channel and title, and to be confirmed by the owner's Block button:
Hindi or English only, one language per video; real moving video with a human voice (no slideshows or
text-to-speech); calm pacing; no toy unboxing, surprise eggs, pranks, challenges, scary or violent content,
ghosts or monsters, seasonal or religious festival videos, product plugs; channel with 100,000+ subscribers
and a long history. Quality `q` is an estimate: channel base (Super Simple Songs 88, Sesame Street India 85,
ChuChu TV Hindi 80, Infobells Hindi 78, Vlad and Niki Hindi 60) plus a bonus of 2 to 4 for videos that
invite a response. Nobody has watched the videos end to end; say so whenever reporting on the catalog.

## 6. Channels in the catalog

| Channel | Language | Upload list for the scan snippet |
| --- | --- | --- |
| Super Simple Songs | English | playlists `PL028565C616627F50`, `PLdkj6XH8GYPTaey_5gCeJF2HZt6kYLN7M`, `PLdkj6XH8GYPRZ1D4bhsHJimqSAGzZg2e9` |
| ChuChu TV Hindi | Hindi | `UUbH4Ii9Htdqc-QgxoV3M0Qw`, playlist `PLIM0H1HVDCe7S2TtsAatniQmSkORcB4fN` |
| Infobells Hindi | Hindi | `UU1ciY6kR3yj3kaKZ6R7ewAg` |
| Sesame Street India | Hindi | inside the ChuChu and Sesame playlist above |
| Vlad and Niki Hindi | Hindi (treat shelf) | found by web search |

Known gaps at launch: Stories holds story-songs, not real kahaniya; Real world has no real-footage
videos; Create and do is thin; no "Diana in Hindi" video under 10 minutes was found; all English comes
from one channel.

## 7. Decisions and limits to respect

- **Tap guard.** On the owner's phone any tap inside YouTube's player opened YouTube, which made the app unusable for a 2-year-old. The guard (and the tray and covers) sit over the player. This goes against YouTube's embed rules (nothing may cover the player). The owner was told; it can be switched off in the parent area.
- **Ads.** He has no YouTube Premium, so ads play and cannot be removed. The guard blocks "Skip ad"; a parent can hold the small button in the top-right corner of the video for one second to lift the guard for 8 seconds.
- **No Claude API, no server, no accounts.** Keep it that way unless he asks.
- **Privacy.** The page is public but unlisted and not indexed. It must contain no name, photo or personal detail. Her greeting name is typed in the parent area and stays on the phone.
- **Testing.** Claude has tested on desktop Chrome and with the two test suites, not on a real phone. Touch behaviour, full-screen landscape lock and ad behaviour are confirmed only by the owner's use.

## 8. Testing and deploying

```
python3 tools/catalog.py     # rewrite the catalog block
python3 tools/ui_test.py     # must print "0 failed"
python3 tools/sim_test.py    # must print "0 failed"
git push origin main         # this is the deploy
```

The tests need Python with Playwright and a Chrome binary (`CHROME=/path/to/chrome` if it is not at
`/usr/bin/google-chrome`). In the browser console, `__cd` exposes read-only helpers: `__cd.cfg.version`,
`__cd.pick(...)`, `__cd.report()`, `__cd.state()`.

## 9. Change log

- 1.1.1 (16 Nov 2026): resuming after a pause now closes the tray (the real player resumes through a buffering state).
- 1.1.0 (16 Nov 2026): full-screen player with swipe-up tray; Home lists every allowed video below the plate; calm closer guaranteed; treat never last; back gesture stays in the app; hide rule reachable after three abandons; playback errors expire after 7 days; tests and docs added.
- 1.0.1 (16 Nov 2026): both languages kept on screen; install manifest and icons.
- 1.0.0 (16 Nov 2026): first full app: 138-video catalog, engine, time rules, parent area, tap guard.
