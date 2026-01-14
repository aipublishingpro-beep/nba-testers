import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="NBA Edge Finder - TEST MODE", page_icon="🎯", layout="wide")

# ========== TEST MODE BANNER ==========
st.markdown("""
<div style='background:linear-gradient(135deg,#ff6600,#ff3300);padding:15px;border-radius:10px;margin-bottom:20px;text-align:center'>
    <span style='color:#fff;font-size:1.5em;font-weight:bold'>⚠️ TEST MODE — Signals Only. No Trading.</span>
</div>
""", unsafe_allow_html=True)

# ========== AUTO-REFRESH (Only after 7PM ET) ==========
current_hour = datetime.now(pytz.timezone('US/Eastern')).hour
if current_hour >= 19:
    st.markdown("""<meta http-equiv="refresh" content="30">""", unsafe_allow_html=True)
    auto_status = "🔄 Auto-refresh ON (30s)"
else:
    auto_status = "⏸️ Auto-refresh OFF (starts 7PM ET)"

# ========== TEAM DATA ==========
TEAM_ABBREVS = {
    "Atlanta Hawks": "Atlanta", "Boston Celtics": "Boston", "Brooklyn Nets": "Brooklyn",
    "Charlotte Hornets": "Charlotte", "Chicago Bulls": "Chicago", "Cleveland Cavaliers": "Cleveland",
    "Dallas Mavericks": "Dallas", "Denver Nuggets": "Denver", "Detroit Pistons": "Detroit",
    "Golden State Warriors": "Golden State", "Houston Rockets": "Houston", "Indiana Pacers": "Indiana",
    "LA Clippers": "LA Clippers", "Los Angeles Clippers": "LA Clippers", "LA Lakers": "LA Lakers",
    "Los Angeles Lakers": "LA Lakers", "Memphis Grizzlies": "Memphis", "Miami Heat": "Miami",
    "Milwaukee Bucks": "Milwaukee", "Minnesota Timberwolves": "Minnesota", "New Orleans Pelicans": "New Orleans",
    "New York Knicks": "New York", "Oklahoma City Thunder": "Oklahoma City", "Orlando Magic": "Orlando",
    "Philadelphia 76ers": "Philadelphia", "Phoenix Suns": "Phoenix", "Portland Trail Blazers": "Portland",
    "Sacramento Kings": "Sacramento", "San Antonio Spurs": "San Antonio", "Toronto Raptors": "Toronto",
    "Utah Jazz": "Utah", "Washington Wizards": "Washington"
}

# ========== SIDEBAR LEGEND ==========
with st.sidebar:
    st.header("📖 TESTER LEGEND")
    
    st.markdown("""
    <div style='background:#ff6600;padding:8px;border-radius:5px;margin-bottom:10px'>
        <span style='color:#fff;font-weight:bold'>⚠️ TEST MODE ONLY</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎯 Signal Types")
    st.markdown("""
    🟢 **STRONG NO** → High confidence Under  
    🔵 **NO** → Under signal  
    🟡 **LEAN NO** → Slight Under lean  
    ⚪ **SKIP** → No clear edge  
    🟡 **LEAN YES** → Slight Over lean  
    🔵 **YES** → Over signal  
    🟢 **STRONG YES** → High confidence Over
    """)
    
    st.divider()
    
    st.subheader("📊 What Signals Use")
    st.markdown("""
    • Live pace (pts/min)  
    • Live projection  
    • Minutes played gate  
    • Cushion vs threshold
    """)
    
    st.divider()
    
    st.subheader("🔥 Pace Labels")
    st.markdown("""
    🟢 **SLOW** → Under-friendly  
    🟡 **AVG** → Neutral  
    🟠 **FAST** → Over-leaning  
    🔴 **SHOOTOUT** → Over-friendly
    """)
    
    st.divider()
    
    st.subheader("📈 Live Trend")
    st.markdown("""
    🔥 **HOT** → Scoring up  
    ❄️ **COLD** → Scoring down  
    ➡️ **NORMAL** → Steady pace
    """)
    
    st.divider()
    
    st.subheader("🎯 Cushion Tiers")
    st.markdown("""
    🟢 **BIG** → +20 pts or more  
    🟡 **MEDIUM** → +10 to +19  
    🟠 **SMALL** → +5 to +9  
    🔴 **NONE** → Under +5
    """)
    
    st.divider()
    st.caption("TESTER v1.0")

st.divider()

# ========== FEEDBACK SECTION ==========
st.subheader("💬 TESTER FEEDBACK")

st.markdown("""
<div style='background:#1a1a2e;padding:15px;border-radius:10px;margin-bottom:15px'>
    <span style='color:#00aaff;font-weight:bold'>Help improve this app!</span><br>
    <span style='color:#aaa'>Share bugs, suggestions, or questions below.</span>
</div>
""", unsafe_allow_html=True)

fb_col1, fb_col2 = st.columns([1, 2])

feedback_type = fb_col1.selectbox(
    "Category",
    ["🐛 Bug Report", "💡 Suggestion", "❓ Question", "🎯 Signal Feedback", "📝 Other"],
    key="feedback_type"
)

feedback_text = st.text_area(
    "Your feedback",
    placeholder="Describe the issue, suggestion, or question...",
    height=120,
    key="feedback_text"
)

# Optional contact
feedback_name = st.text_input("Name (optional)", placeholder="Your name", key="feedback_name")

if st.button("📋 Copy Feedback to Clipboard", use_container_width=True):
    if feedback_text:
        clipboard_text = f"""
NBA EDGE FINDER - TESTER FEEDBACK
---------------------------------
Category: {feedback_type}
From: {feedback_name if feedback_name else 'Anonymous'}
Date: {now.strftime('%Y-%m-%d %I:%M %p ET')}

{feedback_text}
---------------------------------
        """.strip()
        
        st.code(clipboard_text, language=None)
        st.success("👆 Copy the text above and send via email or Discord!")
    else:
        st.warning("Please enter your feedback first")

# Alternative: Direct email link
if feedback_text:
    import urllib.parse
    subject = urllib.parse.quote(f"NBA Edge Finder Feedback: {feedback_type}")
    body = urllib.parse.quote(f"Category: {feedback_type}\nFrom: {feedback_name if feedback_name else 'Anonymous'}\n\n{feedback_text}")
    
    st.markdown(f"""
    <a href="mailto:aipublishingpro@gmail.com?subject={subject}&body={body}" style='display:inline-block;background:#00aa00;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;margin-top:10px'>
        📧 Open in Email App
    </a>
    """, unsafe_allow_html=True)

st.caption("Your feedback helps make the app better!")

# ========== DATA FUNCTIONS ==========
def fetch_espn_scores():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        games = {}
        for event in data.get("events", []):
            comp = event.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue
            home_team, away_team, home_score, away_score = None, None, 0, 0
            for c in competitors:
                name = c.get("team", {}).get("displayName", "")
                team_name = TEAM_ABBREVS.get(name, name)
                score = int(c.get("score", 0) or 0)
                if c.get("homeAway") == "home":
                    home_team, home_score = team_name, score
                else:
                    away_team, away_score = team_name, score
            status_obj = event.get("status", {})
            status_type = status_obj.get("type", {}).get("name", "STATUS_SCHEDULED")
            clock = status_obj.get("displayClock", "")
            period = status_obj.get("period", 0)
            game_key = f"{away_team}@{home_team}"
            games[game_key] = {
                "away_team": away_team, "home_team": home_team,
                "away_score": away_score, "home_score": home_score,
                "total": away_score + home_score,
                "period": period, "clock": clock, "status_type": status_type
            }
        return games
    except:
        return {}

def fetch_yesterday_teams():
    yesterday = (datetime.now(pytz.timezone('US/Eastern')) - timedelta(days=1)).strftime('%Y%m%d')
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={yesterday}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        teams_played = set()
        for event in data.get("events", []):
            comp = event.get("competitions", [{}])[0]
            for c in comp.get("competitors", []):
                full_name = c.get("team", {}).get("displayName", "")
                team_name = TEAM_ABBREVS.get(full_name, full_name)
                teams_played.add(team_name)
        return teams_played
    except:
        return set()

def get_minutes_played(period, clock, status_type):
    if status_type == "STATUS_FINAL":
        return 48 if period <= 4 else 48 + (period - 4) * 5
    if status_type == "STATUS_HALFTIME":
        return 24
    if period == 0:
        return 0
    try:
        clock_str = str(clock)
        if ':' in clock_str:
            parts = clock_str.split(':')
            mins = int(parts[0])
            secs = int(float(parts[1])) if len(parts) > 1 else 0
        else:
            mins = 0
            secs = float(clock_str) if clock_str else 0
        time_left = mins + secs/60
        if period <= 4:
            return (period - 1) * 12 + (12 - time_left)
        else:
            return 48 + (period - 5) * 5 + (5 - time_left)
    except:
        return (period - 1) * 12 if period <= 4 else 48 + (period - 5) * 5

def get_pace_label(pace):
    """Return pace label and color"""
    if pace < 4.5:
        return "🟢 SLOW", "#00ff00"
    elif pace < 4.8:
        return "🟡 AVG", "#ffff00"
    elif pace < 5.2:
        return "🟠 FAST", "#ff8800"
    else:
        return "🔴 SHOOTOUT", "#ff0000"

def get_trend_label(pace, avg_pace=4.85):
    """Return trend based on pace vs average"""
    if pace > avg_pace + 0.3:
        return "🔥 HOT"
    elif pace < avg_pace - 0.3:
        return "❄️ COLD"
    else:
        return "➡️ NORMAL"

def get_signal(mins, cushion, pace, side):
    """
    Simple condition-based signal engine.
    Uses: live pace, live projection, minute gate, cushion gate.
    Returns: signal label, color
    """
    # Hard minute gate - need enough data
    if mins < 6:
        return "⏳ WAITING", "#888888"
    
    # Hard cushion gate
    if cushion < 5:
        return "⚪ SKIP", "#888888"
    
    # Pace factor for signal strength
    pace_boost = 0
    if side == "NO":
        if pace < 4.5:
            pace_boost = 2
        elif pace < 4.8:
            pace_boost = 1
        elif pace > 5.2:
            pace_boost = -1
    else:  # YES
        if pace > 5.2:
            pace_boost = 2
        elif pace > 4.8:
            pace_boost = 1
        elif pace < 4.5:
            pace_boost = -1
    
    # Signal based on cushion + pace
    effective_cushion = cushion + (pace_boost * 3)
    
    if effective_cushion >= 25:
        return f"🟢 STRONG {side}", "#00ff00"
    elif effective_cushion >= 15:
        return f"🔵 {side}", "#00aaff"
    elif effective_cushion >= 8:
        return f"🟡 LEAN {side}", "#ffff00"
    elif cushion >= 5:
        return f"🟡 LEAN {side}", "#ffff00"
    else:
        return "⚪ SKIP", "#888888"

# ========== FETCH DATA ==========
games = fetch_espn_scores()
game_list = sorted(list(games.keys()))
yesterday_teams = fetch_yesterday_teams()
now = datetime.now(pytz.timezone('US/Eastern'))

# ========== HEADER ==========
st.title("🎯 NBA EDGE FINDER")
st.caption(f"TEST MODE | {auto_status} | Last update: {now.strftime('%I:%M:%S %p ET')}")

# ========== LIVE SIGNALS SECTION ==========
st.subheader("📡 LIVE SIGNALS")

# Example thresholds for testing display
EXAMPLE_THRESHOLDS = [225.5, 230.5, 235.5, 240.5]

if game_list:
    live_games = []
    upcoming_games = []
    final_games = []
    
    for game_key in game_list:
        g = games[game_key]
        mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
        
        if g['status_type'] == "STATUS_FINAL":
            final_games.append((game_key, g, mins))
        elif mins >= 6:
            live_games.append((game_key, g, mins))
        else:
            upcoming_games.append((game_key, g, mins))
    
    # ===== LIVE GAMES WITH SIGNALS =====
    if live_games:
        st.markdown("### 🔴 LIVE — Active Signals")
        
        for game_key, g, mins in live_games:
            total = g['total']
            pace = round(total / mins, 2) if mins > 0 else 0
            proj = round(pace * 48) if mins > 0 else 0
            
            pace_label, pace_color = get_pace_label(pace)
            trend = get_trend_label(pace)
            
            # Calculate signals for each threshold
            signals_no = []
            signals_yes = []
            
            for thresh in EXAMPLE_THRESHOLDS:
                cushion_no = thresh - proj
                cushion_yes = proj - thresh
                
                if cushion_no >= 5:
                    sig, col = get_signal(mins, cushion_no, pace, "NO")
                    if "SKIP" not in sig and "WAITING" not in sig:
                        signals_no.append((thresh, cushion_no, sig, col))
                
                if cushion_yes >= 5:
                    sig, col = get_signal(mins, cushion_yes, pace, "YES")
                    if "SKIP" not in sig and "WAITING" not in sig:
                        signals_yes.append((thresh, cushion_yes, sig, col))
            
            # Determine best signal
            best_signal = "⚪ SKIP"
            best_color = "#888888"
            best_info = ""
            
            if signals_no:
                best = max(signals_no, key=lambda x: x[1])
                best_signal = best[2]
                best_color = best[3]
                best_info = f"@ {best[0]} (+{best[1]:.0f} cushion)"
            elif signals_yes:
                best = max(signals_yes, key=lambda x: x[1])
                best_signal = best[2]
                best_color = best[3]
                best_info = f"@ {best[0]} (+{best[1]:.0f} cushion)"
            
            game_status = f"Q{g['period']} {g['clock']}"
            
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:10px;border:2px solid {best_color};margin-bottom:10px'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span style='color:#fff;font-size:1.2em;font-weight:bold'>{game_key.replace('@', ' @ ')}</span>
                        <span style='color:#888;margin-left:10px'>{game_status}</span>
                    </div>
                    <span style='color:{best_color};font-size:1.3em;font-weight:bold'>{best_signal}</span>
                </div>
                <div style='margin-top:10px;display:flex;gap:20px;flex-wrap:wrap'>
                    <span style='color:#aaa'>🏀 <b style="color:#fff">{total} pts</b> in {mins:.0f} min</span>
                    <span style='color:#aaa'>⚡ <b style="color:{pace_color}">{pace}/min</b> {pace_label}</span>
                    <span style='color:#aaa'>📊 Proj: <b style="color:#fff">{proj}</b></span>
                    <span style='color:#aaa'>{trend}</span>
                    <span style='color:#888;font-size:0.9em'>{best_info}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== UPCOMING GAMES =====
    if upcoming_games:
        st.markdown("### ⏳ UPCOMING — Waiting for Data")
        
        for game_key, g, mins in upcoming_games:
            b2b_away = g['away_team'] in yesterday_teams
            b2b_home = g['home_team'] in yesterday_teams
            
            fatigue_note = ""
            if b2b_away and not b2b_home:
                fatigue_note = f"🔴 {g['away_team']} B2B"
            elif b2b_home and not b2b_away:
                fatigue_note = f"🔴 {g['home_team']} B2B"
            elif b2b_away and b2b_home:
                fatigue_note = "🔴 Both B2B"
            
            if mins > 0:
                status = f"Q{g['period']} {g['clock']} — {g['total']} pts"
            else:
                status = "Not started"
            
            st.markdown(f"""
            <div style='background:#1a1a2e;padding:12px;border-radius:8px;border:1px solid #444;margin-bottom:8px'>
                <span style='color:#fff;font-weight:bold'>{game_key.replace('@', ' @ ')}</span>
                <span style='color:#888;margin-left:15px'>{status}</span>
                <span style='color:#ff8800;margin-left:15px'>{fatigue_note}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== FINAL GAMES =====
    if final_games:
        st.markdown("### ✅ FINAL — Completed")
        
        for game_key, g, mins in final_games:
            total = g['total']
            pace = round(total / mins, 2) if mins > 0 else 0
            pace_label, pace_color = get_pace_label(pace)
            
            st.markdown(f"""
            <div style='background:#0a0a15;padding:12px;border-radius:8px;border:1px solid #333;margin-bottom:8px'>
                <span style='color:#888;font-weight:bold'>{game_key.replace('@', ' @ ')}</span>
                <span style='color:#666;margin-left:15px'>FINAL: {total} pts</span>
                <span style='color:{pace_color};margin-left:15px'>{pace}/min {pace_label}</span>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("No games scheduled today")

st.divider()

# ========== B2B INFO ==========
if yesterday_teams:
    st.info(f"📅 **Back-to-Back Teams Today:** {', '.join(sorted(yesterday_teams))}")

st.divider()

# ========== CUSHION SCANNER ==========
st.subheader("🎯 CUSHION SCANNER")

cs1, cs2 = st.columns([1, 1])
cush_min = cs1.selectbox("Min minutes played", [6, 9, 12, 18, 24], index=1)
cush_side = cs2.selectbox("Signal side", ["NO (Under)", "YES (Over)"])
side_clean = "NO" if "NO" in cush_side else "YES"

thresholds = [225.5, 230.5, 235.5, 240.5, 245.5]
cush_data = []

for gk, g in games.items():
    mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
    if mins >= cush_min and g['status_type'] != "STATUS_FINAL":
        pace = g['total'] / mins if mins > 0 else 0
        proj = round(pace * 48) if mins > 0 else 0
        cush_data.append({"game": gk, "proj": proj, "pace": pace, "mins": mins})

if cush_data:
    # Header row
    hcols = st.columns([2, 1, 1] + [1]*len(thresholds))
    hcols[0].markdown("**Game**")
    hcols[1].markdown("**Proj**")
    hcols[2].markdown("**Pace**")
    for i, t in enumerate(thresholds):
        hcols[i+3].markdown(f"**{t}**")
    
    for cd in sorted(cush_data, key=lambda x: x['proj'], reverse=(side_clean=="YES")):
        pace_label, pace_color = get_pace_label(cd['pace'])
        
        rcols = st.columns([2, 1, 1] + [1]*len(thresholds))
        rcols[0].write(cd['game'].replace("@", " @ "))
        rcols[1].write(f"{cd['proj']}")
        rcols[2].markdown(f"<span style='color:{pace_color}'>{cd['pace']:.1f}</span>", unsafe_allow_html=True)
        
        for i, t in enumerate(thresholds):
            if side_clean == "NO":
                c = t - cd['proj']
            else:
                c = cd['proj'] - t
            
            if c >= 20:
                rcols[i+3].markdown(f"<span style='color:#00ff00'>**+{c:.0f}** 🟢</span>", unsafe_allow_html=True)
            elif c >= 10:
                rcols[i+3].markdown(f"<span style='color:#ffff00'>**+{c:.0f}** 🟡</span>", unsafe_allow_html=True)
            elif c >= 5:
                rcols[i+3].markdown(f"<span style='color:#ff8800'>+{c:.0f} 🟠</span>", unsafe_allow_html=True)
            else:
                rcols[i+3].markdown(f"<span style='color:#666'>—</span>", unsafe_allow_html=True)
else:
    st.info(f"No live games with {cush_min}+ minutes played")

st.divider()

# ========== PACE SCANNER ==========
st.subheader("🔥 PACE SCANNER")

pace_data = []
for gk, g in games.items():
    mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
    if mins >= 6:
        pace = round(g['total'] / mins, 2)
        proj = round(pace * 48)
        pace_data.append({
            "game": gk, "pace": pace, "proj": proj, 
            "total": g['total'], "mins": mins,
            "period": g['period'], "clock": g['clock'], 
            "final": g['status_type'] == "STATUS_FINAL"
        })

pace_data.sort(key=lambda x: x['pace'])

if pace_data:
    for p in pace_data:
        lbl, clr = get_pace_label(p['pace'])
        trend = get_trend_label(p['pace'])
        status = "FINAL" if p['final'] else f"Q{p['period']} {p['clock']}"
        
        st.markdown(f"""
        <div style='background:#1a1a2e;padding:10px;border-radius:8px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center'>
            <span style='color:#fff'><b>{p['game'].replace('@', ' @ ')}</b></span>
            <span style='color:#aaa'>{p['total']} pts in {p['mins']:.0f} min</span>
            <span style='color:{clr};font-weight:bold'>{p['pace']}/min {lbl}</span>
            <span style='color:#888'>{trend}</span>
            <span style='color:#fff'>Proj: <b>{p['proj']}</b></span>
            <span style='color:#666'>{status}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No games with 6+ minutes played yet")

st.divider()

# ========== ALL GAMES SCOREBOARD ==========
st.subheader("📺 ALL GAMES")

if games:
    cols = st.columns(4)
    for i, (k, g) in enumerate(games.items()):
        with cols[i % 4]:
            st.markdown(f"**{g['away_team']}** {g['away_score']}")
            st.markdown(f"**{g['home_team']}** {g['home_score']}")
            status = "FINAL" if g['status_type'] == "STATUS_FINAL" else f"Q{g['period']} {g['clock']}"
            st.caption(f"{status} | {g['total']} pts")
else:
    st.info("No games today")

st.divider()

# ========== FOOTER ==========
st.markdown("""
<div style='background:#1a1a2e;padding:15px;border-radius:10px;text-align:center;margin-top:20px'>
    <span style='color:#ff6600;font-weight:bold'>⚠️ TEST MODE — For testing and research purposes only.</span><br>
    <span style='color:#888;font-size:0.9em'>Signals are for educational demonstration. Not financial advice. No trading functionality.</span>
</div>
""", unsafe_allow_html=True)

st.caption("TESTER v1.0")
