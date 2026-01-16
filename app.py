import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
import json
from streamlit.components.v1 import html

st.set_page_config(page_title="NBA Edge Finder (DEMO)", page_icon="🏀", layout="wide")

# ========== BROWSER STORAGE (localStorage) ==========
def save_to_browser(key, data):
    """Save data to browser localStorage"""
    json_str = json.dumps(data)
    html(f"""
        <script>
            localStorage.setItem('{key}', '{json_str}');
        </script>
    """, height=0)

def load_from_browser_script():
    """Inject script to load data from localStorage into a hidden div"""
    return """
        <script>
            const data = localStorage.getItem('nba_positions_demo');
            if (data) {
                window.parent.postMessage({type: 'localStorage', data: data}, '*');
            }
        </script>
    """

# ========== AUTO-REFRESH SETUP ==========
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'positions' not in st.session_state:
    st.session_state.positions = []
if 'positions_loaded' not in st.session_state:
    st.session_state.positions_loaded = False

if st.session_state.auto_refresh:
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)
    auto_status = "🔄 Auto-refresh ON (30s)"
else:
    auto_status = "⏸️ Auto-refresh OFF"

st.markdown("""
<style>
.stLinkButton > a {
    background-color: #00aa00 !important;
    border-color: #00aa00 !important;
    color: white !important;
}
.stLinkButton > a:hover {
    background-color: #00cc00 !important;
    border-color: #00cc00 !important;
}
</style>
""", unsafe_allow_html=True)

# ========== KALSHI TEAM CODES ==========
KALSHI_CODES = {
    "Atlanta": "atl", "Boston": "bos", "Brooklyn": "bkn", "Charlotte": "cha",
    "Chicago": "chi", "Cleveland": "cle", "Dallas": "dal", "Denver": "den",
    "Detroit": "det", "Golden State": "gsw", "Houston": "hou", "Indiana": "ind",
    "LA Clippers": "lac", "LA Lakers": "lal", "Memphis": "mem", "Miami": "mia",
    "Milwaukee": "mil", "Minnesota": "min", "New Orleans": "nop", "New York": "nyk",
    "Oklahoma City": "okc", "Orlando": "orl", "Philadelphia": "phi", "Phoenix": "phx",
    "Portland": "por", "Sacramento": "sac", "San Antonio": "sas", "Toronto": "tor",
    "Utah": "uta", "Washington": "was"
}

def build_kalshi_totals_url(away_team, home_team):
    away_code = KALSHI_CODES.get(away_team, "xxx")
    home_code = KALSHI_CODES.get(home_team, "xxx")
    today = datetime.now(pytz.timezone('US/Eastern'))
    date_str = today.strftime("%y%b%d").lower()
    ticker = f"kxnbatotal-{date_str}{away_code}{home_code}"
    return f"https://kalshi.com/markets/kxnbatotal/pro-basketball-total-points/{ticker}"

def build_kalshi_ml_url(away_team, home_team):
    away_code = KALSHI_CODES.get(away_team, "xxx")
    home_code = KALSHI_CODES.get(home_team, "xxx")
    today = datetime.now(pytz.timezone('US/Eastern'))
    date_str = today.strftime("%y%b%d").lower()
    ticker = f"kxnbagame-{date_str}{away_code}{home_code}"
    return f"https://kalshi.com/markets/kxnbagame/pro-basketball-moneyline/{ticker}"

if 'default_contracts' not in st.session_state:
    st.session_state.default_contracts = 1

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

STAR_PLAYERS = {
    "Atlanta": ["Trae Young"], "Boston": ["Jayson Tatum", "Jaylen Brown"], "Brooklyn": ["Mikal Bridges"],
    "Charlotte": ["LaMelo Ball"], "Chicago": ["Zach LaVine"],
    "Cleveland": ["Donovan Mitchell", "Darius Garland", "Evan Mobley"],
    "Dallas": ["Luka Doncic", "Kyrie Irving"], "Denver": ["Nikola Jokic", "Jamal Murray"],
    "Detroit": ["Cade Cunningham"], "Golden State": ["Stephen Curry", "Draymond Green"],
    "Houston": ["Jalen Green", "Alperen Sengun"], "Indiana": ["Tyrese Haliburton", "Pascal Siakam"],
    "LA Clippers": ["Kawhi Leonard", "James Harden"], "LA Lakers": ["LeBron James", "Anthony Davis"],
    "Memphis": ["Ja Morant", "Desmond Bane"], "Miami": ["Jimmy Butler", "Bam Adebayo"],
    "Milwaukee": ["Giannis Antetokounmpo", "Damian Lillard"],
    "Minnesota": ["Anthony Edwards", "Rudy Gobert"],
    "New Orleans": ["Zion Williamson", "Brandon Ingram"], "New York": ["Jalen Brunson", "Karl-Anthony Towns"],
    "Oklahoma City": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"],
    "Orlando": ["Paolo Banchero", "Franz Wagner"], "Philadelphia": ["Joel Embiid", "Tyrese Maxey"],
    "Phoenix": ["Kevin Durant", "Devin Booker", "Bradley Beal"], "Portland": ["Anfernee Simons"],
    "Sacramento": ["De'Aaron Fox", "Domantas Sabonis"], "San Antonio": ["Victor Wembanyama"],
    "Toronto": ["Scottie Barnes", "RJ Barrett"], "Utah": ["Lauri Markkanen"], "Washington": ["Jordan Poole"]
}

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🏀 NBA EDGE FINDER")
    st.caption("Public Demo Version")
    st.divider()
    st.subheader("📖 SIGNAL TIERS")
    st.markdown("""
    🟢 **STRONG** → High confidence  
    🔵 **SIGNAL** → Good opportunity  
    🟡 **LEAN** → Slight edge  
    ⚪ **TOSS-UP** → No clear edge  
    🔴 **SKIP** → Avoid
    """)
    st.divider()
    st.subheader("🔥 PACE LABELS")
    st.markdown("""
    🟢 **SLOW** → Under 4.5/min  
    🟡 **AVG** → 4.5 - 4.8/min  
    🟠 **FAST** → 4.8 - 5.2/min  
    🔴 **SHOOTOUT** → Over 5.2/min
    """)
    st.divider()
    st.caption("DEMO v15.11")
    st.caption("💾 Positions saved in browser")

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

def fetch_espn_injuries():
    injuries = {}
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        injury_list = data.get("injuries", data.get("teams", []))
        for team_data in injury_list:
            team_name = team_data.get("team", {}).get("displayName", "")
            if not team_name:
                team_name = team_data.get("team", {}).get("name", "")
            if not team_name:
                team_name = team_data.get("displayName", "")
            team_key = TEAM_ABBREVS.get(team_name, team_name)
            if not team_key:
                continue
            injuries[team_key] = []
            player_list = team_data.get("injuries", team_data.get("athletes", []))
            for player in player_list:
                name = player.get("athlete", {}).get("displayName", "")
                if not name:
                    name = player.get("displayName", "")
                if not name:
                    name = player.get("name", "")
                status = player.get("status", "")
                if not status:
                    status = player.get("type", {}).get("description", "")
                if name:
                    injuries[team_key].append({"name": name, "status": status})
    except:
        pass
    return injuries

def get_minutes_played(period, clock, status_type):
    if status_type == "STATUS_FINAL": return 48 if period <= 4 else 48 + (period - 4) * 5
    if status_type == "STATUS_HALFTIME": return 24
    if period == 0: return 0
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
        if period <= 4: return (period - 1) * 12 + (12 - time_left)
        else: return 48 + (period - 5) * 5 + (5 - time_left)
    except:
        return (period - 1) * 12 if period <= 4 else 48 + (period - 5) * 5

# ========== FETCH DATA ==========
games = fetch_espn_scores()
game_list = sorted(list(games.keys()))
yesterday_teams_raw = fetch_yesterday_teams()
injuries = fetch_espn_injuries()
now = datetime.now(pytz.timezone('US/Eastern'))

today_teams = set()
for game_key in games.keys():
    parts = game_key.split("@")
    today_teams.add(parts[0])
    today_teams.add(parts[1])
yesterday_teams = yesterday_teams_raw.intersection(today_teams)

# ========== HEADER ==========
st.title("🏀 NBA EDGE FINDER (DEMO)")
hdr1, hdr2, hdr3 = st.columns([3, 1, 1])
hdr1.caption(f"{auto_status} | Last update: {now.strftime('%I:%M:%S %p ET')} | DEMO v15.11")

if hdr2.button("🔄 Auto" if not st.session_state.auto_refresh else "⏹️ Stop", use_container_width=True):
    st.session_state.auto_refresh = not st.session_state.auto_refresh
    st.rerun()

if hdr3.button("🔄 Refresh", use_container_width=True):
    st.rerun()

# ========== LOAD POSITIONS FROM BROWSER ==========
st.markdown("#### 💾 Position Storage")
positions_input = st.text_area(
    "📋 Paste your saved positions here (or copy to save):",
    value=json.dumps(st.session_state.positions) if st.session_state.positions else "[]",
    height=100,
    key="positions_json",
    help="Copy this JSON to save your positions. Paste it back after refresh to restore."
)

col_load, col_clear = st.columns(2)
if col_load.button("📥 Load Positions", use_container_width=True):
    try:
        loaded = json.loads(positions_input)
        if isinstance(loaded, list):
            st.session_state.positions = loaded
            st.success(f"✅ Loaded {len(loaded)} positions!")
            st.rerun()
    except:
        st.error("❌ Invalid JSON format")

if col_clear.button("🗑️ Clear All", use_container_width=True):
    st.session_state.positions = []
    st.rerun()

st.divider()

# ========== 🏥 INJURY REPORT ==========
st.subheader("🏥 INJURY REPORT - TODAY'S GAMES")

if game_list:
    teams_playing = set()
    for game_key in game_list:
        parts = game_key.split("@")
        teams_playing.add(parts[0])
        teams_playing.add(parts[1])
    
    star_injuries = []
    for team in sorted(teams_playing):
        team_injuries = injuries.get(team, [])
        stars = STAR_PLAYERS.get(team, [])
        for inj in team_injuries:
            name = inj.get("name", "")
            status = inj.get("status", "").upper()
            is_star = any(star.lower() in name.lower() for star in stars)
            if is_star:
                if "OUT" in status: simple_status = "OUT"
                elif "DAY-TO-DAY" in status or "DTD" in status: simple_status = "DTD"
                elif "QUESTIONABLE" in status or "GTD" in status: simple_status = "GTD"
                else: simple_status = status[:10]
                star_injuries.append((team, name, simple_status))
    
    if star_injuries:
        st.markdown("### ⭐ KEY PLAYER INJURIES")
        cols = st.columns(3)
        for idx, (team, name, status) in enumerate(star_injuries):
            with cols[idx % 3]:
                status_color = "#ff0000" if status == "OUT" else "#ffaa00"
                st.markdown(f"<div style='background:linear-gradient(135deg,#2a1a1a,#1a1a2e);padding:10px;border-radius:8px;border-left:4px solid {status_color};margin-bottom:8px'><span style='color:#fff;font-weight:bold'>⭐ {name}</span><br><span style='color:{status_color};font-size:0.9em'>{status}</span><span style='color:#888;font-size:0.85em'> • {team}</span></div>", unsafe_allow_html=True)
        st.caption(f"📊 {len(star_injuries)} key players injured/questionable")
    else:
        st.info("✅ No key player injuries reported for today's games")
else:
    st.info("No games scheduled today")

st.divider()

# ========== B2B INFO ==========
if yesterday_teams:
    st.info(f"📅 **Back-to-Back Teams Today**: {', '.join(sorted(yesterday_teams))}")
else:
    st.info("📅 **No B2B teams today** — all teams are rested")

st.divider()

# ========== ADD NEW POSITION ==========
st.subheader("➕ TRACK A POSITION")

game_options = ["Select a game..."] + [gk.replace("@", " @ ") for gk in game_list]
selected_game = st.selectbox("🏀 Game", game_options, key="game_select")

if selected_game != "Select a game...":
    parts = selected_game.replace(" @ ", "@").split("@")
    away_t, home_t = parts[0], parts[1]
    col_ml, col_tot = st.columns(2)
    col_ml.link_button(f"🔗 ML on Kalshi", build_kalshi_ml_url(away_t, home_t), use_container_width=True)
    col_tot.link_button(f"🔗 Totals on Kalshi", build_kalshi_totals_url(away_t, home_t), use_container_width=True)

with st.form("add_position_form"):
    market_type = st.radio("📈 Market Type", ["Moneyline (Winner)", "Totals (Over/Under)"], horizontal=True)
    p1, p2, p3 = st.columns(3)
    if selected_game != "Select a game...":
        parts = selected_game.replace(" @ ", "@").split("@")
        ml_options = [f"{parts[1]} (Home)", f"{parts[0]} (Away)"]
    else:
        ml_options = ["Select game first"]
    totals_options = ["NO (Under)", "YES (Over)"]
    if market_type == "Moneyline (Winner)":
        side = p1.selectbox("📊 Pick Winner", ml_options)
    else:
        side = p1.selectbox("📊 Side", totals_options)
    price_paid = p2.number_input("💵 Price (¢)", min_value=1, max_value=99, value=50, step=1)
    contracts = p3.number_input("📄 Contracts", min_value=1, value=st.session_state.default_contracts, step=1)
    threshold_select = st.number_input("🎯 Threshold (Totals only)", min_value=180.0, max_value=280.0, value=225.5, step=0.5)
    add_btn = st.form_submit_button("✅ ADD POSITION", use_container_width=True)
    if add_btn and selected_game != "Select a game..." and side != "Select game first":
        game_key = selected_game.replace(" @ ", "@")
        parts = game_key.split("@")
        if market_type == "Moneyline (Winner)":
            team_pick = parts[1] if "Home" in side else parts[0]
            st.session_state.positions.append({'game': game_key, 'type': 'ml', 'pick': team_pick, 'price': price_paid, 'contracts': contracts, 'cost': round(price_paid * contracts / 100, 2)})
        else:
            side_clean = "NO" if "NO" in side else "YES"
            st.session_state.positions.append({'game': game_key, 'type': 'totals', 'side': side_clean, 'threshold': threshold_select, 'price': price_paid, 'contracts': contracts, 'cost': round(price_paid * contracts / 100, 2)})
        st.success("✅ Position added! Copy the JSON above to save.")
        st.rerun()

st.divider()

# ========== ACTIVE POSITIONS ==========
st.subheader("📈 ACTIVE POSITIONS")

if st.session_state.positions:
    for idx, pos in enumerate(st.session_state.positions):
        game_key = pos['game']
        g = games.get(game_key)
        price = pos.get('price', 50)
        contracts = pos.get('contracts', 1)
        cost = pos.get('cost', round(price * contracts / 100, 2))
        pos_type = pos.get('type', 'totals')
        potential_win = round((100 - price) * contracts / 100, 2)
        potential_loss = cost
        if g:
            total = g['total']
            mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
            is_final = g['status_type'] == "STATUS_FINAL"
            game_status = "FINAL" if is_final else f"Q{g['period']} {g['clock']}"
            if pos_type == 'ml':
                pick = pos.get('pick', '')
                parts = game_key.split("@")
                away_team, home_team = parts[0], parts[1]
                home_score, away_score = g['home_score'], g['away_score']
                pick_score = home_score if pick == home_team else away_score
                opp_score = away_score if pick == home_team else home_score
                lead = pick_score - opp_score
                if is_final:
                    won = pick_score > opp_score
                    if won:
                        status_label, status_color = "✅ WON!", "#00ff00"
                        pnl_display, pnl_color = f"+${potential_win:.2f}", "#00ff00"
                    else:
                        status_label, status_color = "❌ LOST", "#ff0000"
                        pnl_display, pnl_color = f"-${potential_loss:.2f}", "#ff0000"
                elif mins > 0:
                    if lead >= 15: status_label, status_color = "🟢 CRUISING", "#00ff00"
                    elif lead >= 8: status_label, status_color = "🟢 LEADING", "#00ff00"
                    elif lead >= 1: status_label, status_color = "🟡 AHEAD", "#ffff00"
                    elif lead >= -5: status_label, status_color = "🟠 CLOSE", "#ff8800"
                    else: status_label, status_color = "🔴 BEHIND", "#ff0000"
                    pnl_display, pnl_color = f"Win: +${potential_win:.2f}", "#888888"
                else:
                    status_label, status_color = "⏳ WAITING", "#888888"
                    lead = 0
                    pnl_display, pnl_color = f"Win: +${potential_win:.2f}", "#888888"
                st.markdown(f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:10px;border:2px solid {status_color};margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><div><span style='color:#fff;font-size:1.2em;font-weight:bold'>{game_key.replace('@', ' @ ')}</span><span style='color:#888;margin-left:10px'>{game_status}</span></div><span style='color:{status_color};font-size:1.3em;font-weight:bold'>{status_label}</span></div><div style='margin-top:10px;display:flex;gap:30px;flex-wrap:wrap'><span style='color:#aaa'>🎯 <b style=\"color:#fff\">ML: {pick}</b></span><span style='color:#aaa'>💵 <b style=\"color:#fff\">{contracts}x @ {price}¢</b> (${cost:.2f})</span><span style='color:#aaa'>📊 Score: <b style=\"color:#fff\">{pick_score}-{opp_score}</b></span><span style='color:#aaa'>📈 Lead: <b style=\"color:{status_color}\">{lead:+d}</b></span><span style='color:{pnl_color}'>{pnl_display}</span></div></div>", unsafe_allow_html=True)
            else:
                projected = round((total / mins) * 48) if mins > 0 else None
                cushion = (pos['threshold'] - projected) if pos.get('side') == "NO" and projected else ((projected - pos['threshold']) if projected else 0)
                if is_final:
                    won = (total < pos['threshold']) if pos.get('side') == "NO" else (total > pos['threshold'])
                    if won:
                        status_label, status_color = "✅ WON!", "#00ff00"
                        pnl_display, pnl_color = f"+${potential_win:.2f}", "#00ff00"
                    else:
                        status_label, status_color = "❌ LOST", "#ff0000"
                        pnl_display, pnl_color = f"-${potential_loss:.2f}", "#ff0000"
                elif projected:
                    if cushion >= 15: status_label, status_color = "🟢 VERY SAFE", "#00ff00"
                    elif cushion >= 8: status_label, status_color = "🟢 LOOKING GOOD", "#00ff00"
                    elif cushion >= 3: status_label, status_color = "🟡 ON TRACK", "#ffff00"
                    elif cushion >= -3: status_label, status_color = "🟠 WARNING", "#ff8800"
                    else: status_label, status_color = "🔴 AT RISK", "#ff0000"
                    pnl_display, pnl_color = f"Win: +${potential_win:.2f}", "#888888"
                else:
                    status_label, status_color = "⏳ WAITING", "#888888"
                    pnl_display, pnl_color = f"Win: +${potential_win:.2f}", "#888888"
                st.markdown(f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:10px;border:2px solid {status_color};margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><div><span style='color:#fff;font-size:1.2em;font-weight:bold'>{game_key.replace('@', ' @ ')}</span><span style='color:#888;margin-left:10px'>{game_status}</span></div><span style='color:{status_color};font-size:1.3em;font-weight:bold'>{status_label}</span></div><div style='margin-top:10px;display:flex;gap:30px;flex-wrap:wrap'><span style='color:#aaa'>📊 <b style=\"color:#fff\">{pos.get('side', 'NO')} {pos.get('threshold', 0)}</b></span><span style='color:#aaa'>💵 <b style=\"color:#fff\">{contracts}x @ {price}¢</b> (${cost:.2f})</span><span style='color:#aaa'>📈 Proj: <b style=\"color:#fff\">{projected if projected else '—'}</b></span><span style='color:#aaa'>🎯 Cushion: <b style=\"color:{status_color}\">{cushion:+.0f}</b></span><span style='color:{pnl_color}'>{pnl_display}</span></div></div>", unsafe_allow_html=True)
            btn1, btn2 = st.columns([3, 1])
            parts = game_key.split("@")
            if pos_type == 'ml': kalshi_url = build_kalshi_ml_url(parts[0], parts[1])
            else: kalshi_url = build_kalshi_totals_url(parts[0], parts[1])
            btn1.link_button(f"🔗 Trade on Kalshi", kalshi_url, use_container_width=True)
            if btn2.button("🗑️ Remove", key=f"del_{idx}"):
                st.session_state.positions.pop(idx)
                st.rerun()
        else:
            if pos_type == 'ml': display_text = f"ML: {pos.get('pick', '?')}"
            else: display_text = f"{pos.get('side', 'NO')} {pos.get('threshold', 0)}"
            st.markdown(f"<div style='background:#1a1a2e;padding:15px;border-radius:10px;border:1px solid #444;margin-bottom:10px'><span style='color:#888'>{game_key.replace('@', ' @ ')} — {display_text} — {contracts}x @ {price}¢</span><span style='color:#666;margin-left:15px'>⏳ Game not started</span></div>", unsafe_allow_html=True)
            if st.button("🗑️ Remove", key=f"del_{idx}"):
                st.session_state.positions.pop(idx)
                st.rerun()
    
    st.info("💡 **To save positions**: Copy the JSON text from the box above before closing/refreshing. Paste it back to restore.")
else:
    st.info("No positions tracked — use the form above to add your first position")

st.divider()

# ========== PACE SCANNER ==========
st.subheader("🔥 PACE SCANNER")

pace_data = []
for gk, g in games.items():
    mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
    if mins >= 6:
        pace = round(g['total'] / mins, 2)
        proj = round(pace * 48)
        pace_data.append({"game": gk, "pace": pace, "proj": proj, "total": g['total'], "mins": mins, "period": g['period'], "clock": g['clock'], "final": g['status_type'] == "STATUS_FINAL"})

pace_data.sort(key=lambda x: x['pace'])

if pace_data:
    for p in pace_data:
        if p['pace'] < 4.5: lbl, clr = "🟢 SLOW", "#00ff00"
        elif p['pace'] < 4.8: lbl, clr = "🟡 AVG", "#ffff00"
        elif p['pace'] < 5.2: lbl, clr = "🟠 FAST", "#ff8800"
        else: lbl, clr = "🔴 SHOOTOUT", "#ff0000"
        status = "FINAL" if p['final'] else f"Q{p['period']} {p['clock']}"
        st.markdown(f"**{p['game'].replace('@', ' @ ')}** — {p['total']} pts in {p['mins']:.0f} min — **{p['pace']}/min** <span style='color:{clr}'>**{lbl}**</span> — Proj: **{p['proj']}** — {status}", unsafe_allow_html=True)
else:
    st.info("No games with 6+ minutes played yet")

st.divider()

# ========== ALL GAMES ==========
st.subheader("📺 ALL GAMES")
if games:
    cols = st.columns(4)
    for i, (k, g) in enumerate(games.items()):
        with cols[i % 4]:
            st.write(f"**{g['away_team']}** {g['away_score']}")
            st.write(f"**{g['home_team']}** {g['home_score']}")
            status = "FINAL" if g['status_type'] == "STATUS_FINAL" else f"Q{g['period']} {g['clock']}"
            st.caption(f"{status} | {g['total']} pts")
else:
    st.info("No games today")

st.divider()

# ========== HOW TO USE ==========
st.subheader("📖 HOW TO USE THIS APP")
st.markdown("""
**🏥 INJURY REPORT** — Shows key player injuries for today's games.

**📅 B2B TEAMS** — Teams playing back-to-back (played yesterday + playing today).

**💾 POSITION STORAGE** — Copy/paste the JSON to save your positions between sessions.

**➕ POSITION TRACKER** — Track your bets with live P&L projections as games progress.

**🔥 PACE SCANNER** — Quick view of all live game paces. 🟢 SLOW (<4.5/min) favors unders, 🔴 SHOOTOUT (>5.2/min) favors overs.

**📺 ALL GAMES** — Simple scoreboard with live scores for all today's games.

---

**💡 TIP**: Use the Pace Scanner to identify games trending under/over their projected totals, then track your positions to monitor cushion in real-time.
""")

st.divider()
st.caption("⚠️ For entertainment only. Not financial advice.")
st.caption("DEMO v15.11 - Public Version")
