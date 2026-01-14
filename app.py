import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="NBA Edge Finder - TEST MODE", page_icon="🎯", layout="wide")

# ========== TEST MODE BANNER ==========
st.markdown("""
<div style='background:linear-gradient(135deg,#ff6600,#ff3300);padding:12px;border-radius:10px;margin-bottom:15px;text-align:center'>
    <span style='color:#fff;font-size:1.3em;font-weight:bold'>⚠️ TEST MODE — Signals Only. No Trading.</span>
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

TEAM_STATS = {
    "Atlanta": {"pace": 100.5, "def_rank": 26, "net_rating": -3.2, "ft_rate": 0.26, "reb_rate": 49.5, "three_pct": 36.2, "home_win_pct": 0.52, "away_win_pct": 0.35, "division": "Southeast"},
    "Boston": {"pace": 99.8, "def_rank": 2, "net_rating": 11.2, "ft_rate": 0.24, "reb_rate": 51.2, "three_pct": 38.5, "home_win_pct": 0.78, "away_win_pct": 0.65, "division": "Atlantic"},
    "Brooklyn": {"pace": 98.2, "def_rank": 22, "net_rating": -4.5, "ft_rate": 0.23, "reb_rate": 48.8, "three_pct": 35.8, "home_win_pct": 0.42, "away_win_pct": 0.28, "division": "Atlantic"},
    "Charlotte": {"pace": 99.5, "def_rank": 28, "net_rating": -6.8, "ft_rate": 0.25, "reb_rate": 48.2, "three_pct": 34.5, "home_win_pct": 0.38, "away_win_pct": 0.22, "division": "Southeast"},
    "Chicago": {"pace": 98.8, "def_rank": 20, "net_rating": -2.1, "ft_rate": 0.24, "reb_rate": 49.8, "three_pct": 35.2, "home_win_pct": 0.48, "away_win_pct": 0.32, "division": "Central"},
    "Cleveland": {"pace": 97.2, "def_rank": 3, "net_rating": 8.5, "ft_rate": 0.27, "reb_rate": 52.5, "three_pct": 36.8, "home_win_pct": 0.75, "away_win_pct": 0.58, "division": "Central"},
    "Dallas": {"pace": 99.0, "def_rank": 12, "net_rating": 4.2, "ft_rate": 0.26, "reb_rate": 50.2, "three_pct": 37.5, "home_win_pct": 0.62, "away_win_pct": 0.48, "division": "Southwest"},
    "Denver": {"pace": 98.5, "def_rank": 10, "net_rating": 5.8, "ft_rate": 0.25, "reb_rate": 51.8, "three_pct": 36.5, "home_win_pct": 0.72, "away_win_pct": 0.45, "division": "Northwest"},
    "Detroit": {"pace": 97.8, "def_rank": 29, "net_rating": -8.2, "ft_rate": 0.24, "reb_rate": 48.5, "three_pct": 34.2, "home_win_pct": 0.32, "away_win_pct": 0.18, "division": "Central"},
    "Golden State": {"pace": 100.2, "def_rank": 8, "net_rating": 3.5, "ft_rate": 0.23, "reb_rate": 50.5, "three_pct": 38.2, "home_win_pct": 0.65, "away_win_pct": 0.42, "division": "Pacific"},
    "Houston": {"pace": 101.5, "def_rank": 18, "net_rating": 1.2, "ft_rate": 0.28, "reb_rate": 50.8, "three_pct": 35.5, "home_win_pct": 0.55, "away_win_pct": 0.38, "division": "Southwest"},
    "Indiana": {"pace": 103.5, "def_rank": 24, "net_rating": 2.8, "ft_rate": 0.26, "reb_rate": 49.2, "three_pct": 37.8, "home_win_pct": 0.58, "away_win_pct": 0.42, "division": "Central"},
    "LA Clippers": {"pace": 98.0, "def_rank": 14, "net_rating": 1.5, "ft_rate": 0.25, "reb_rate": 50.0, "three_pct": 36.0, "home_win_pct": 0.55, "away_win_pct": 0.40, "division": "Pacific"},
    "LA Lakers": {"pace": 99.5, "def_rank": 15, "net_rating": 2.2, "ft_rate": 0.27, "reb_rate": 51.0, "three_pct": 35.8, "home_win_pct": 0.58, "away_win_pct": 0.42, "division": "Pacific"},
    "Memphis": {"pace": 100.8, "def_rank": 6, "net_rating": 4.5, "ft_rate": 0.26, "reb_rate": 52.2, "three_pct": 35.2, "home_win_pct": 0.68, "away_win_pct": 0.48, "division": "Southwest"},
    "Miami": {"pace": 97.5, "def_rank": 5, "net_rating": 3.8, "ft_rate": 0.24, "reb_rate": 50.8, "three_pct": 36.5, "home_win_pct": 0.65, "away_win_pct": 0.45, "division": "Southeast"},
    "Milwaukee": {"pace": 99.2, "def_rank": 9, "net_rating": 5.2, "ft_rate": 0.28, "reb_rate": 51.5, "three_pct": 37.2, "home_win_pct": 0.70, "away_win_pct": 0.52, "division": "Central"},
    "Minnesota": {"pace": 98.8, "def_rank": 4, "net_rating": 7.5, "ft_rate": 0.25, "reb_rate": 52.8, "three_pct": 36.2, "home_win_pct": 0.72, "away_win_pct": 0.55, "division": "Northwest"},
    "New Orleans": {"pace": 100.0, "def_rank": 16, "net_rating": 1.8, "ft_rate": 0.27, "reb_rate": 50.5, "three_pct": 36.8, "home_win_pct": 0.55, "away_win_pct": 0.38, "division": "Southwest"},
    "New York": {"pace": 98.5, "def_rank": 7, "net_rating": 6.2, "ft_rate": 0.25, "reb_rate": 51.2, "three_pct": 37.0, "home_win_pct": 0.68, "away_win_pct": 0.52, "division": "Atlantic"},
    "Oklahoma City": {"pace": 99.8, "def_rank": 1, "net_rating": 12.5, "ft_rate": 0.26, "reb_rate": 52.0, "three_pct": 37.5, "home_win_pct": 0.82, "away_win_pct": 0.68, "division": "Northwest"},
    "Orlando": {"pace": 97.0, "def_rank": 11, "net_rating": 3.2, "ft_rate": 0.26, "reb_rate": 51.5, "three_pct": 35.5, "home_win_pct": 0.62, "away_win_pct": 0.45, "division": "Southeast"},
    "Philadelphia": {"pace": 98.2, "def_rank": 13, "net_rating": 2.5, "ft_rate": 0.28, "reb_rate": 50.2, "three_pct": 36.2, "home_win_pct": 0.58, "away_win_pct": 0.42, "division": "Atlantic"},
    "Phoenix": {"pace": 99.0, "def_rank": 17, "net_rating": 2.0, "ft_rate": 0.25, "reb_rate": 49.8, "three_pct": 36.8, "home_win_pct": 0.60, "away_win_pct": 0.42, "division": "Pacific"},
    "Portland": {"pace": 99.5, "def_rank": 27, "net_rating": -5.5, "ft_rate": 0.24, "reb_rate": 48.5, "three_pct": 35.0, "home_win_pct": 0.40, "away_win_pct": 0.25, "division": "Northwest"},
    "Sacramento": {"pace": 101.2, "def_rank": 19, "net_rating": 0.8, "ft_rate": 0.25, "reb_rate": 49.5, "three_pct": 36.5, "home_win_pct": 0.55, "away_win_pct": 0.38, "division": "Pacific"},
    "San Antonio": {"pace": 100.5, "def_rank": 25, "net_rating": -4.8, "ft_rate": 0.26, "reb_rate": 49.0, "three_pct": 34.8, "home_win_pct": 0.42, "away_win_pct": 0.28, "division": "Southwest"},
    "Toronto": {"pace": 98.8, "def_rank": 21, "net_rating": -1.5, "ft_rate": 0.24, "reb_rate": 49.5, "three_pct": 35.5, "home_win_pct": 0.48, "away_win_pct": 0.32, "division": "Atlantic"},
    "Utah": {"pace": 100.2, "def_rank": 30, "net_rating": -7.5, "ft_rate": 0.25, "reb_rate": 48.0, "three_pct": 35.2, "home_win_pct": 0.35, "away_win_pct": 0.22, "division": "Northwest"},
    "Washington": {"pace": 101.0, "def_rank": 23, "net_rating": -6.2, "ft_rate": 0.27, "reb_rate": 48.8, "three_pct": 34.5, "home_win_pct": 0.38, "away_win_pct": 0.25, "division": "Southeast"}
}

TEAM_LOCATIONS = {
    "Atlanta": (33.757, -84.396), "Boston": (42.366, -71.062), "Brooklyn": (40.683, -73.976),
    "Charlotte": (35.225, -80.839), "Chicago": (41.881, -87.674), "Cleveland": (41.496, -81.688),
    "Dallas": (32.790, -96.810), "Denver": (39.749, -105.010), "Detroit": (42.341, -83.055),
    "Golden State": (37.768, -122.388), "Houston": (29.751, -95.362), "Indiana": (39.764, -86.156),
    "LA Clippers": (34.043, -118.267), "LA Lakers": (34.043, -118.267), "Memphis": (35.138, -90.051),
    "Miami": (25.781, -80.188), "Milwaukee": (43.045, -87.917), "Minnesota": (44.979, -93.276),
    "New Orleans": (29.949, -90.082), "New York": (40.751, -73.994), "Oklahoma City": (35.463, -97.515),
    "Orlando": (28.539, -81.384), "Philadelphia": (39.901, -75.172), "Phoenix": (33.446, -112.071),
    "Portland": (45.532, -122.667), "Sacramento": (38.580, -121.500), "San Antonio": (29.427, -98.438),
    "Toronto": (43.643, -79.379), "Utah": (40.768, -111.901), "Washington": (38.898, -77.021)
}

STAR_PLAYERS = {
    "Atlanta": ["Trae Young"], "Boston": ["Jayson Tatum", "Jaylen Brown"], "Brooklyn": ["Mikal Bridges"],
    "Charlotte": ["LaMelo Ball"], "Chicago": ["Zach LaVine", "DeMar DeRozan"],
    "Cleveland": ["Donovan Mitchell", "Darius Garland", "Evan Mobley"],
    "Dallas": ["Luka Doncic", "Kyrie Irving"], "Denver": ["Nikola Jokic", "Jamal Murray"],
    "Detroit": ["Cade Cunningham"], "Golden State": ["Stephen Curry", "Draymond Green"],
    "Houston": ["Jalen Green", "Alperen Sengun"], "Indiana": ["Tyrese Haliburton", "Pascal Siakam"],
    "LA Clippers": ["Kawhi Leonard", "Paul George"], "LA Lakers": ["LeBron James", "Anthony Davis"],
    "Memphis": ["Ja Morant", "Desmond Bane"], "Miami": ["Jimmy Butler", "Bam Adebayo"],
    "Milwaukee": ["Giannis Antetokounmpo", "Damian Lillard"],
    "Minnesota": ["Anthony Edwards", "Karl-Anthony Towns", "Rudy Gobert"],
    "New Orleans": ["Zion Williamson", "Brandon Ingram"], "New York": ["Jalen Brunson", "Julius Randle"],
    "Oklahoma City": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"],
    "Orlando": ["Paolo Banchero", "Franz Wagner"], "Philadelphia": ["Joel Embiid", "Tyrese Maxey"],
    "Phoenix": ["Kevin Durant", "Devin Booker", "Bradley Beal"], "Portland": ["Anfernee Simons"],
    "Sacramento": ["De'Aaron Fox", "Domantas Sabonis"], "San Antonio": ["Victor Wembanyama"],
    "Toronto": ["Scottie Barnes"], "Utah": ["Lauri Markkanen"], "Washington": ["Jordan Poole"]
}

# ========== SIDEBAR LEGEND ==========
with st.sidebar:
    st.header("📖 LEGEND")
    
    st.markdown("""
    <div style='background:#ff6600;padding:8px;border-radius:5px;margin-bottom:10px'>
        <span style='color:#fff;font-weight:bold'>⚠️ TEST MODE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎯 ML Signal Tiers")
    st.markdown("""
    🟢 **STRONG PICK** → 8.0+ score  
    🔵 **MODEL PICK** → 6.5 - 7.9  
    🟡 **LEAN** → 5.5 - 6.4  
    ⚪ **TOSS-UP** → 4.5 - 5.4  
    🔴 **SKIP** → Below 4.5
    """)
    
    st.divider()
    
    st.subheader("📊 10-Factor ML System")
    st.markdown("""
    1. Rest Advantage  
    2. Net Rating Edge  
    3. Defense Ranking  
    4. Home Court  
    5. Injury Impact  
    6. Travel Fatigue  
    7. Home/Away Splits  
    8. Division Rivalry  
    9. Altitude (Denver)  
    10. Team Quality
    """)
    
    st.divider()
    
    st.subheader("📊 10-Factor Totals")
    st.markdown("""
    1. 🐢 Pace  
    2. 🛡️ Defense Rank  
    3. 🛏️ Rest/Fatigue  
    4. 🎯 3PT Shooting  
    5. 🏥 Star Injuries  
    6. 💥 Blowout Risk  
    7. 🏔️ Altitude  
    8. 🎁 FT Rate  
    9. 🏀 Rebound Control  
    10. 🏠 Home Scoring
    """)
    
    st.divider()
    st.caption("TESTER v1.0")

# ========== HELPER FUNCTIONS ==========
def calc_distance(loc1, loc2):
    from math import radians, sin, cos, sqrt, atan2
    lat1, lon1 = radians(loc1[0]), radians(loc1[1])
    lat2, lon2 = radians(loc2[0]), radians(loc2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 3959 * 2 * atan2(sqrt(a), sqrt(1-a))

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
        for team_data in data.get("injuries", []):
            team_name = team_data.get("team", {}).get("displayName", "")
            team_key = TEAM_ABBREVS.get(team_name, team_name)
            injuries[team_key] = []
            for player in team_data.get("injuries", []):
                name = player.get("athlete", {}).get("displayName", "")
                status = player.get("status", "")
                injuries[team_key].append({"name": name, "status": status})
    except:
        pass
    return injuries

def get_injury_score(team, injuries):
    team_injuries = injuries.get(team, [])
    stars = STAR_PLAYERS.get(team, [])
    score = 0
    out_stars = []
    for inj in team_injuries:
        name = inj.get("name", "")
        status = inj.get("status", "").upper()
        is_star = any(star.lower() in name.lower() for star in stars)
        if "OUT" in status:
            score += 4.0 if is_star else 1.0
            if is_star:
                out_stars.append(name)
        elif "DAY-TO-DAY" in status or "GTD" in status or "QUESTIONABLE" in status:
            score += 2.5 if is_star else 0.5
    return score, out_stars

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

def calc_ml_score(home_team, away_team, yesterday_teams, injuries):
    """Calculate 10-factor ML score. Returns (pick, score, edge, reasons, home_stars, away_stars)"""
    home = TEAM_STATS.get(home_team, {})
    away = TEAM_STATS.get(away_team, {})
    home_loc = TEAM_LOCATIONS.get(home_team, (0, 0))
    away_loc = TEAM_LOCATIONS.get(away_team, (0, 0))
    
    score_home = 0
    score_away = 0
    reasons_home = []
    reasons_away = []
    
    # 1. REST ADVANTAGE
    home_b2b = home_team in yesterday_teams
    away_b2b = away_team in yesterday_teams
    if away_b2b and not home_b2b:
        score_home += 1.0
        reasons_home.append("🛏️ Opp B2B")
    elif home_b2b and not away_b2b:
        score_away += 1.0
        reasons_away.append("🛏️ Opp B2B")
    elif not home_b2b and not away_b2b:
        score_home += 0.5
        score_away += 0.5
    
    # 2. NET RATING
    home_net = home.get('net_rating', 0)
    away_net = away.get('net_rating', 0)
    net_diff = home_net - away_net
    if net_diff > 5:
        score_home += 1.0
        reasons_home.append(f"📊 Net +{home_net:.1f}")
    elif net_diff > 2:
        score_home += 0.7
        reasons_home.append(f"📊 Net +{home_net:.1f}")
    elif net_diff > 0:
        score_home += 0.5
    elif net_diff > -2:
        score_away += 0.5
    elif net_diff > -5:
        score_away += 0.7
        reasons_away.append(f"📊 Net +{away_net:.1f}")
    else:
        score_away += 1.0
        reasons_away.append(f"📊 Net +{away_net:.1f}")
    
    # 3. DEFENSE RANK
    home_def = home.get('def_rank', 15)
    away_def = away.get('def_rank', 15)
    if home_def <= 5:
        score_home += 1.0
        reasons_home.append(f"🛡️ #{home_def} DEF")
    elif home_def <= 10:
        score_home += 0.7
        reasons_home.append(f"🛡️ #{home_def} DEF")
    elif home_def <= 15:
        score_home += 0.4
    if away_def <= 5:
        score_away += 1.0
        reasons_away.append(f"🛡️ #{away_def} DEF")
    elif away_def <= 10:
        score_away += 0.7
        reasons_away.append(f"🛡️ #{away_def} DEF")
    elif away_def <= 15:
        score_away += 0.4
    
    # 4. HOME COURT
    score_home += 1.0
    
    # 5. INJURY IMPACT
    home_inj, home_stars = get_injury_score(home_team, injuries)
    away_inj, away_stars = get_injury_score(away_team, injuries)
    inj_diff = away_inj - home_inj
    if inj_diff > 3:
        score_home += 1.0
        if away_stars:
            reasons_home.append(f"🏥 {away_stars[0][:10]} OUT")
    elif inj_diff > 1:
        score_home += 0.6
        if away_stars:
            reasons_home.append(f"🏥 {away_stars[0][:10]} OUT")
    elif inj_diff < -3:
        score_away += 1.0
        if home_stars:
            reasons_away.append(f"🏥 {home_stars[0][:10]} OUT")
    elif inj_diff < -1:
        score_away += 0.6
        if home_stars:
            reasons_away.append(f"🏥 {home_stars[0][:10]} OUT")
    else:
        score_home += 0.3
        score_away += 0.3
    
    # 6. TRAVEL FATIGUE
    travel_miles = calc_distance(away_loc, home_loc)
    if travel_miles > 2000:
        score_home += 1.0
        reasons_home.append(f"✈️ {int(travel_miles)}mi")
    elif travel_miles > 1500:
        score_home += 0.7
        reasons_home.append(f"✈️ {int(travel_miles)}mi")
    elif travel_miles > 1000:
        score_home += 0.5
    elif travel_miles > 500:
        score_home += 0.3
    
    # 7. HOME/AWAY SPLITS
    home_hw = home.get('home_win_pct', 0.5)
    away_aw = away.get('away_win_pct', 0.5)
    reasons_home.append(f"🏠 {int(home_hw*100)}% home")
    if home_hw > 0.65:
        score_home += 0.8
    elif home_hw > 0.55:
        score_home += 0.5
    if away_aw < 0.35:
        score_home += 0.5
        reasons_home.append(f"📉 Opp {int(away_aw*100)}% road")
    elif away_aw < 0.45:
        score_home += 0.3
        reasons_home.append(f"📉 Opp {int(away_aw*100)}% road")
    
    # 8. DIVISION RIVALRY
    if home.get('division') == away.get('division') and home.get('division'):
        score_home += 0.5
        reasons_home.append("⚔️ Division")
    
    # 9. ALTITUDE
    if home_team == "Denver":
        score_home += 1.0
        reasons_home.append("🏔️ Altitude")
    
    # 10. QUALITY FACTOR
    if home_net > 5:
        score_home += 0.5
        if f"📊 Net +{home_net:.1f}" not in reasons_home:
            reasons_home.append("⭐ Elite")
    if away_net > 5:
        score_away += 0.5
        if f"📊 Net +{away_net:.1f}" not in reasons_away:
            reasons_away.append("⭐ Elite")
    
    # Normalize to 10-point scale
    total = score_home + score_away
    if total > 0:
        home_final = round((score_home / total) * 10, 1)
        away_final = round((score_away / total) * 10, 1)
    else:
        home_final = 5.0
        away_final = 5.0
    
    if home_final >= away_final:
        pick = home_team
        score = home_final
        edge = round((home_final - 5) * 4, 0)
        reasons = reasons_home[:4]
    else:
        pick = away_team
        score = away_final
        edge = round((away_final - 5) * 4, 0)
        reasons = reasons_away[:4]
    
    return pick, score, edge, reasons, home_stars, away_stars

def get_signal_tier(score):
    if score >= 8.0:
        return "🟢 STRONG PICK", "#00ff00"
    elif score >= 6.5:
        return "🔵 MODEL PICK", "#00aaff"
    elif score >= 5.5:
        return "🟡 LEAN", "#ffff00"
    elif score >= 4.5:
        return "⚪ TOSS-UP", "#888888"
    else:
        return "🔴 SKIP", "#ff0000"

def calc_totals_score(home_team, away_team, yesterday_teams, injuries):
    home = TEAM_STATS.get(home_team, {})
    away = TEAM_STATS.get(away_team, {})
    
    score_under = 0
    score_over = 0
    reasons_under = []
    reasons_over = []
    
    # 1. PACE
    home_pace = home.get('pace', 100)
    away_pace = away.get('pace', 100)
    avg_pace = (home_pace + away_pace) / 2
    if avg_pace < 98.5:
        score_under += 1.5
        reasons_under.append(f"🐢 Slow {avg_pace:.1f}")
    elif avg_pace < 99.5:
        score_under += 1.0
        reasons_under.append(f"🐢 Pace {avg_pace:.1f}")
    elif avg_pace > 101:
        score_over += 1.5
        reasons_over.append(f"🔥 Fast {avg_pace:.1f}")
    elif avg_pace > 100:
        score_over += 1.0
        reasons_over.append(f"🔥 Pace {avg_pace:.1f}")
    
    # 2. DEFENSE
    home_def = home.get('def_rank', 15)
    away_def = away.get('def_rank', 15)
    avg_def = (home_def + away_def) / 2
    if avg_def <= 8:
        score_under += 1.5
        reasons_under.append(f"🛡️ DEF #{int(avg_def)}")
    elif avg_def <= 12:
        score_under += 1.0
        reasons_under.append(f"🛡️ DEF #{int(avg_def)}")
    elif avg_def >= 22:
        score_over += 1.5
        reasons_over.append(f"💥 DEF #{int(avg_def)}")
    elif avg_def >= 18:
        score_over += 1.0
        reasons_over.append(f"💥 DEF #{int(avg_def)}")
    
    # 3. REST/FATIGUE
    home_b2b = home_team in yesterday_teams
    away_b2b = away_team in yesterday_teams
    if home_b2b and away_b2b:
        score_under += 1.5
        reasons_under.append("🛏️ Both B2B")
    elif home_b2b or away_b2b:
        score_under += 0.75
        tired_team = home_team if home_b2b else away_team
        reasons_under.append(f"🛏️ {tired_team[:3]} B2B")
    
    # 4. 3PT SHOOTING
    home_3pt = home.get('three_pct', 36)
    away_3pt = away.get('three_pct', 36)
    avg_3pt = (home_3pt + away_3pt) / 2
    if avg_3pt < 35.5:
        score_under += 1.0
        reasons_under.append(f"🎯 Low 3PT {avg_3pt:.1f}%")
    elif avg_3pt > 37.5:
        score_over += 1.0
        reasons_over.append(f"🎯 High 3PT {avg_3pt:.1f}%")
    
    # 5. INJURY IMPACT
    home_inj, home_stars = get_injury_score(home_team, injuries)
    away_inj, away_stars = get_injury_score(away_team, injuries)
    if home_stars or away_stars:
        score_under += 1.0
        out_names = (home_stars + away_stars)[:2]
        reasons_under.append(f"🏥 {', '.join([n[:8] for n in out_names])} OUT")
    
    # 6. BLOWOUT RISK
    home_net = home.get('net_rating', 0)
    away_net = away.get('net_rating', 0)
    net_diff = abs(home_net - away_net)
    if net_diff > 10:
        score_over += 0.75
        reasons_over.append("💥 Blowout risk")
    elif net_diff < 3:
        score_under += 0.5
        reasons_under.append("⚔️ Close game")
    
    # 7. ALTITUDE
    if home_team == "Denver":
        score_under += 0.75
        reasons_under.append("🏔️ Denver altitude")
    
    # 8. FT RATE
    home_ft = home.get('ft_rate', 0.25)
    away_ft = away.get('ft_rate', 0.25)
    avg_ft = (home_ft + away_ft) / 2
    if avg_ft > 0.27:
        score_under += 0.5
        reasons_under.append("🎁 High FT rate")
    elif avg_ft < 0.23:
        score_over += 0.5
        reasons_over.append("🏃 Low FT rate")
    
    # 9. REBOUND RATE
    home_reb = home.get('reb_rate', 50)
    away_reb = away.get('reb_rate', 50)
    avg_reb = (home_reb + away_reb) / 2
    if avg_reb > 51.5:
        score_under += 0.5
        reasons_under.append("🏀 Control boards")
    
    # 10. HOME SCORING
    if home.get('home_win_pct', 0.5) > 0.65 and home_net > 5:
        score_over += 0.5
        reasons_over.append("🏠 Home scoring")
    
    # Normalize
    total = score_under + score_over
    if total > 0:
        under_final = round((score_under / total) * 10, 1)
        over_final = round((score_over / total) * 10, 1)
    else:
        under_final = 5.0
        over_final = 5.0
    
    if under_final >= over_final:
        pick = "NO"
        score = under_final
        reasons = reasons_under[:4]
    else:
        pick = "YES"
        score = over_final
        reasons = reasons_over[:4]
    
    return pick, score, reasons

def get_totals_signal_tier(score, pick):
    if score >= 8.0:
        return f"🟢 STRONG {pick}", "#00ff00"
    elif score >= 6.5:
        return f"🔵 {pick}", "#00aaff"
    elif score >= 5.5:
        return f"🟡 LEAN {pick}", "#ffff00"
    elif score >= 4.5:
        return "⚪ TOSS-UP", "#888888"
    else:
        return "🔴 SKIP", "#ff0000"

# ========== FETCH DATA ==========
games = fetch_espn_scores()
game_list = sorted(list(games.keys()))
yesterday_teams = fetch_yesterday_teams()
injuries = fetch_espn_injuries()
now = datetime.now(pytz.timezone('US/Eastern'))

# ========== HEADER ==========
st.title("🎯 NBA EDGE FINDER")
st.caption(f"TEST MODE | {auto_status} | Last update: {now.strftime('%I:%M:%S %p ET')}")

# ========== 🎯 BIG SNAPSHOT - ML PICKS ==========
st.subheader("🎯 BIG SNAPSHOT - TODAY'S ML PICKS")

if game_list:
    all_picks = []
    for game_key in game_list:
        parts = game_key.split("@")
        away_team = parts[0]
        home_team = parts[1]
        
        pick, score, edge, reasons, home_out, away_out = calc_ml_score(home_team, away_team, yesterday_teams, injuries)
        signal, color = get_signal_tier(score)
        
        all_picks.append({
            'game': game_key, 'home': home_team, 'away': away_team,
            'pick': pick, 'score': score, 'edge': edge,
            'signal': signal, 'color': color, 'reasons': reasons
        })
    
    all_picks.sort(key=lambda x: x['score'], reverse=True)
    
    strong = [p for p in all_picks if p['score'] >= 8.0]
    buys = [p for p in all_picks if 6.5 <= p['score'] < 8.0]
    leans = [p for p in all_picks if 5.5 <= p['score'] < 6.5]
    tossups = [p for p in all_picks if 4.5 <= p['score'] < 5.5]
    skips = [p for p in all_picks if p['score'] < 4.5]
    
    if strong:
        st.markdown("### 🟢 STRONG PICK")
        for p in strong:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            is_home = p['pick'] == p['home']
            opp = p['away'] if is_home else p['home']
            tag = "🏠" if is_home else "✈️"
            
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**<span style='color:#00ff00'>{p['pick']}</span>** {tag} vs {opp}", unsafe_allow_html=True)
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10 | +{p['edge']:.0f}%</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: {p['pick'].upper()}</span>", unsafe_allow_html=True)
    
    if buys:
        st.markdown("### 🔵 MODEL PICK")
        for p in buys:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            is_home = p['pick'] == p['home']
            opp = p['away'] if is_home else p['home']
            tag = "🏠" if is_home else "✈️"
            
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**<span style='color:#00aaff'>{p['pick']}</span>** {tag} vs {opp}", unsafe_allow_html=True)
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10 | +{p['edge']:.0f}%</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: {p['pick'].upper()}</span>", unsafe_allow_html=True)
    
    if leans:
        st.markdown("### 🟡 LEAN")
        for p in leans:
            reasons_str = " • ".join(p['reasons'][:3]) if p['reasons'] else ""
            is_home = p['pick'] == p['home']
            opp = p['away'] if is_home else p['home']
            tag = "🏠" if is_home else "✈️"
            
            col1, col2, col3 = st.columns([3, 2, 5])
            col1.markdown(f"**<span style='color:#ffff00'>{p['pick']}</span>** {tag} vs {opp}", unsafe_allow_html=True)
            col2.markdown(f"<span style='color:{p['color']}'>{p['score']}/10 | +{p['edge']:.0f}%</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#888;font-size:0.85em'>{reasons_str}</span> → <span style='color:#ffff00;font-weight:bold'>{p['pick']}</span>", unsafe_allow_html=True)
    
    if tossups:
        st.markdown("### ⚪ TOSS-UP")
        for p in tossups:
            st.markdown(f"<span style='color:#888'>{p['away']}</span> ✈️ @ <span style='color:#888'>{p['home']}</span> 🏠 — <span style='color:{p['color']}'>{p['score']}/10</span> — No clear edge", unsafe_allow_html=True)
    
    if skips:
        st.markdown("### 🔴 SKIP")
        for p in skips:
            st.markdown(f"~~{p['away']} @ {p['home']}~~ — <span style='color:{p['color']}'>{p['score']}/10</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"📊 {len(strong)} Strong | {len(buys)} Signal | {len(leans)} Leans | {len(tossups)} Toss-ups | {len(skips)} Skips")
else:
    st.info("No games scheduled today")

st.divider()

# ========== 🎯 TOTALS BIG SNAPSHOT ==========
st.subheader("🎯 TOTALS BIG SNAPSHOT - TODAY'S OVER/UNDER PICKS")

if game_list:
    all_totals = []
    for game_key in game_list:
        parts = game_key.split("@")
        away_team = parts[0]
        home_team = parts[1]
        
        pick, score, reasons = calc_totals_score(home_team, away_team, yesterday_teams, injuries)
        signal, color = get_totals_signal_tier(score, pick)
        
        all_totals.append({
            'game': game_key, 'home': home_team, 'away': away_team,
            'pick': pick, 'score': score, 'signal': signal, 'color': color, 'reasons': reasons
        })
    
    all_totals.sort(key=lambda x: x['score'], reverse=True)
    
    strong_no = [p for p in all_totals if p['score'] >= 8.0 and p['pick'] == "NO"]
    strong_yes = [p for p in all_totals if p['score'] >= 8.0 and p['pick'] == "YES"]
    reg_no = [p for p in all_totals if 6.5 <= p['score'] < 8.0 and p['pick'] == "NO"]
    reg_yes = [p for p in all_totals if 6.5 <= p['score'] < 8.0 and p['pick'] == "YES"]
    lean_no = [p for p in all_totals if 5.5 <= p['score'] < 6.5 and p['pick'] == "NO"]
    lean_yes = [p for p in all_totals if 5.5 <= p['score'] < 6.5 and p['pick'] == "YES"]
    tossups_t = [p for p in all_totals if 4.5 <= p['score'] < 5.5]
    skips_t = [p for p in all_totals if p['score'] < 4.5]
    
    if strong_no:
        st.markdown("### 🟢 STRONG NO (Under)")
        for p in strong_no:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**{p['away']}** @ **{p['home']}**")
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: NO</span>", unsafe_allow_html=True)
    
    if strong_yes:
        st.markdown("### 🟢 STRONG YES (Over)")
        for p in strong_yes:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**{p['away']}** @ **{p['home']}**")
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: YES</span>", unsafe_allow_html=True)
    
    if reg_no:
        st.markdown("### 🔵 NO (Under)")
        for p in reg_no:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**{p['away']}** @ **{p['home']}**")
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: NO</span>", unsafe_allow_html=True)
    
    if reg_yes:
        st.markdown("### 🔵 YES (Over)")
        for p in reg_yes:
            reasons_str = " • ".join(p['reasons']) if p['reasons'] else "Multiple factors"
            col1, col2, col3, col4 = st.columns([3, 2, 4, 2])
            col1.markdown(f"**{p['away']}** @ **{p['home']}**")
            col2.markdown(f"<span style='color:{p['color']};font-weight:bold'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#aaa;font-size:0.9em'>{reasons_str}</span>", unsafe_allow_html=True)
            col4.markdown(f"<span style='background:#00aa00;color:white;padding:8px 15px;border-radius:5px;font-weight:bold'>PICK: YES</span>", unsafe_allow_html=True)
    
    if lean_no:
        st.markdown("### 🟡 LEAN NO (Under)")
        for p in lean_no:
            reasons_str = " • ".join(p['reasons'][:3]) if p['reasons'] else ""
            col1, col2, col3 = st.columns([3, 2, 5])
            col1.markdown(f"{p['away']} @ {p['home']}")
            col2.markdown(f"<span style='color:{p['color']}'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#888;font-size:0.85em'>{reasons_str}</span> → <span style='color:#ffff00;font-weight:bold'>NO</span>", unsafe_allow_html=True)
    
    if lean_yes:
        st.markdown("### 🟡 LEAN YES (Over)")
        for p in lean_yes:
            reasons_str = " • ".join(p['reasons'][:3]) if p['reasons'] else ""
            col1, col2, col3 = st.columns([3, 2, 5])
            col1.markdown(f"{p['away']} @ {p['home']}")
            col2.markdown(f"<span style='color:{p['color']}'>{p['score']}/10</span>", unsafe_allow_html=True)
            col3.markdown(f"<span style='color:#888;font-size:0.85em'>{reasons_str}</span> → <span style='color:#ffff00;font-weight:bold'>YES</span>", unsafe_allow_html=True)
    
    if tossups_t:
        st.markdown("### ⚪ TOSS-UP")
        for p in tossups_t:
            st.markdown(f"{p['away']} @ {p['home']} — <span style='color:{p['color']}'>{p['score']}/10</span> — No clear edge", unsafe_allow_html=True)
    
    if skips_t:
        st.markdown("### 🔴 SKIP")
        for p in skips_t:
            st.markdown(f"~~{p['away']} @ {p['home']}~~ — <span style='color:{p['color']}'>{p['score']}/10</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    total_no = len(strong_no) + len(reg_no) + len(lean_no)
    total_yes = len(strong_yes) + len(reg_yes) + len(lean_yes)
    st.caption(f"📊 {len(strong_no)+len(strong_yes)} Strong | {len(reg_no)+len(reg_yes)} Signal | {len(lean_no)+len(lean_yes)} Leans | NO: {total_no} | YES: {total_yes}")
else:
    st.info("No games scheduled today")

st.divider()

if yesterday_teams:
    st.info(f"📅 **B2B Teams Today:** {', '.join(sorted(yesterday_teams))}")

st.divider()

# ========== PACE SCANNER ==========
st.subheader("🔥 PACE SCANNER")

pace_data = []
for gk, g in games.items():
    mins = get_minutes_played(g['period'], g['clock'], g['status_type'])
    if mins >= 6:
        pace = round(g['total'] / mins, 2)
        proj = round(pace * 48)
        pace_data.append({"game": gk, "pace": pace, "proj": proj, "total": g['total'], "mins": mins,
                         "period": g['period'], "clock": g['clock'], "final": g['status_type'] == "STATUS_FINAL"})

pace_data.sort(key=lambda x: x['pace'])

if pace_data:
    for p in pace_data:
        if p['pace'] < 4.5:
            lbl, clr = "🟢 SLOW", "#00ff00"
        elif p['pace'] < 4.8:
            lbl, clr = "🟡 AVG", "#ffff00"
        elif p['pace'] < 5.2:
            lbl, clr = "🟠 FAST", "#ff8800"
        else:
            lbl, clr = "🔴 SHOOTOUT", "#ff0000"
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

# ========== FOOTER ==========
st.markdown("""
<div style='background:#1a1a2e;padding:15px;border-radius:10px;text-align:center;margin-top:20px'>
    <span style='color:#ff6600;font-weight:bold'>⚠️ TEST MODE — For testing and research purposes only.</span><br>
    <span style='color:#888;font-size:0.9em'>Signals are for educational demonstration. Not financial advice.</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ========== FEEDBACK SECTION ==========
st.subheader("💬 TESTER FEEDBACK")

st.markdown("""
<div style='background:#1a1a2e;padding:15px;border-radius:10px;margin-bottom:15px'>
    <span style='color:#00aaff;font-weight:bold'>Help improve this app!</span><br>
    <span style='color:#aaa'>Share bugs, suggestions, or questions below.</span>
</div>
""", unsafe_allow_html=True)

feedback_type = st.selectbox(
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
        st.success("👆 Copy the text above and send via email!")
    else:
        st.warning("Please enter your feedback first")

if feedback_text:
    import urllib.parse
    subject = urllib.parse.quote(f"NBA Edge Finder Feedback: {feedback_type}")
    body = urllib.parse.quote(f"Category: {feedback_type}\nFrom: {feedback_name if feedback_name else 'Anonymous'}\n\n{feedback_text}")
    st.markdown(f"""
    <a href="mailto:aipublishingpro@gmail.com?subject={subject}&body={body}" style='display:inline-block;background:#00aa00;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;margin-top:10px'>
        📧 Send Feedback via Email
    </a>
    """, unsafe_allow_html=True)

st.caption("TESTER v1.0")
