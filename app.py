import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
import json
import os

st.set_page_config(page_title="NBA Edge Finder", page_icon="🎯", layout="wide")

# ========== DAILY DATE KEY ==========
today_str = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d")

st.markdown("""
<style>
div[role="radiogroup"] label { cursor: pointer; }
div[role="radiogroup"] label span {
    padding: 8px 18px;
    border-radius: 10px;
    display: inline-block;
    font-weight: 700;
}
div[role="radiogroup"] input:checked + div span { box-shadow: inset 0 0 0 2px white; }
div[role="radiogroup"] label:nth-of-type(1) span {
    background: linear-gradient(135deg, #102a1a, #163a26);
    border: 2px solid #00ff88;
    color: #ccffee;
}
div[role="radiogroup"] label:nth-of-type(2) span {
    background: linear-gradient(135deg, #2a1515, #3a1a1a);
    border: 2px solid #ff4444;
    color: #ffcccc;
}
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

# ========== PAPER TRACKING STORAGE ==========
POSITIONS_FILE = "nba_positions_test.json"

def load_positions():
    try:
        if os.path.exists(POSITIONS_FILE):
            with open(POSITIONS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_positions(positions):
    try:
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(positions, f, indent=2)
    except:
        pass

# ========== SESSION STATE INIT ==========
st.session_state.setdefault("totals_side_radio", "NO (Under)")
st.session_state.setdefault("ml_pick_radio", None)
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if "positions" not in st.session_state:
    st.session_state.positions = load_positions()
if 'default_contracts' not in st.session_state:
    st.session_state.default_contracts = 1
if "selected_side" not in st.session_state:
    st.session_state.selected_side = "NO"
if "selected_threshold" not in st.session_state:
    st.session_state.selected_threshold = 225.5
if "selected_ml_pick" not in st.session_state:
    st.session_state.selected_ml_pick = None

if "snapshot_date" not in st.session_state or st.session_state["snapshot_date"] != today_str:
    st.session_state["snapshot_date"] = today_str
    st.session_state.pop("big_snapshot", None)
    st.session_state.pop("cached_games", None)

if st.session_state.auto_refresh:
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)
    auto_status = "🔄 Auto-refresh ON (30s)"
else:
    auto_status = "⏸️ Auto-refresh OFF"

# ========== TEAM CODES ==========
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
    away_code = KALSHI_CODES.get(away_team, "xxx").upper()
    home_code = KALSHI_CODES.get(home_team, "xxx").upper()
    today = datetime.now(pytz.timezone('US/Eastern'))
    date_str = today.strftime("%y%b%d").upper()
    ticker = f"KXNBATOTAL-{date_str}{away_code}{home_code}"
    return f"https://kalshi.com/markets/KXNBATOTAL/{ticker}"

def build_kalshi_ml_url(away_team, home_team):
    away_code = KALSHI_CODES.get(away_team, "xxx").upper()
    home_code = KALSHI_CODES.get(home_team, "xxx").upper()
    today = datetime.now(pytz.timezone('US/Eastern'))
    date_str = today.strftime("%y%b%d").upper()
    ticker = f"KXNBAGAME-{date_str}{away_code}{home_code}"
    return f"https://kalshi.com/markets/KXNBAGAME/{ticker}"

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🔗 KALSHI")
    st.caption("📝 TEST MODE - Paper Tracking Only")
    st.caption("Track here → Execute on Kalshi web")
    st.divider()
    st.header("📖 LEGEND")
    st.subheader("🎯 ML Signal Tiers")
    st.markdown("🟢 **STRONG BUY** → 8.0+ score\n\n🔵 **BUY** → 6.5 - 7.9 score\n\n🟡 **LEAN** → 5.5 - 6.4 score\n\n⚪ **TOSS-UP** → 4.5 - 5.4 score\n\n🔴 **SKIP** → Below 4.5")
    st.divider()
    st.subheader("🎯 Totals Signal Tiers")
    st.markdown("🟢 **STRONG NO/YES** → 8.0+ score\n\n🔵 **NO/YES** → 6.5 - 7.9 score\n\n🟡 **LEAN NO/YES** → 5.5 - 6.4\n\n⚪ **TOSS-UP** → 4.5 - 5.4\n\n🔴 **SKIP** → Below 4.5")
    st.divider()
    st.subheader("⭐ Star Injury Weights")
    st.markdown("⭐⭐⭐ **Superstar** → 3x weight\n\n⭐⭐ **All-Star** → 2x weight\n\n⭐ **Rotation** → 1x weight\n\n🔥 Offense | 🛡️ Defense | ⚔️ Both")
    st.divider()
    st.subheader("🔥 Pace Labels")
    st.markdown("🟢 **SLOW** → Under 4.5/min\n\n🟡 **AVG** → 4.5 - 4.8/min\n\n🟠 **FAST** → 4.8 - 5.2/min\n\n🔴 **SHOOTOUT** → Over 5.2/min")
    st.divider()
    st.caption("v15.30 TEST")
    st.caption("💾 Paper positions persist")
    st.caption("🔗 View-only mode")

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

# ========== PROPRIETARY ANALYSIS ENGINE (BLACK BOX) ==========
_T = {"Atlanta":{"a":100.5,"b":26,"c":-3.2,"d":0.26,"e":49.5,"f":36.2,"g":0.52,"h":0.35,"i":"Southeast"},"Boston":{"a":99.8,"b":2,"c":11.2,"d":0.24,"e":51.2,"f":38.5,"g":0.78,"h":0.65,"i":"Atlantic"},"Brooklyn":{"a":98.2,"b":22,"c":-4.5,"d":0.23,"e":48.8,"f":35.8,"g":0.42,"h":0.28,"i":"Atlantic"},"Charlotte":{"a":99.5,"b":28,"c":-6.8,"d":0.25,"e":48.2,"f":34.5,"g":0.38,"h":0.22,"i":"Southeast"},"Chicago":{"a":98.8,"b":20,"c":-2.1,"d":0.24,"e":49.8,"f":35.2,"g":0.48,"h":0.32,"i":"Central"},"Cleveland":{"a":97.2,"b":3,"c":8.5,"d":0.27,"e":52.5,"f":36.8,"g":0.75,"h":0.58,"i":"Central"},"Dallas":{"a":99.0,"b":12,"c":4.2,"d":0.26,"e":50.2,"f":37.5,"g":0.62,"h":0.48,"i":"Southwest"},"Denver":{"a":98.5,"b":10,"c":5.8,"d":0.25,"e":51.8,"f":36.5,"g":0.72,"h":0.45,"i":"Northwest"},"Detroit":{"a":97.8,"b":29,"c":-8.2,"d":0.24,"e":48.5,"f":34.2,"g":0.32,"h":0.18,"i":"Central"},"Golden State":{"a":100.2,"b":8,"c":3.5,"d":0.23,"e":50.5,"f":38.2,"g":0.65,"h":0.42,"i":"Pacific"},"Houston":{"a":101.5,"b":18,"c":1.2,"d":0.28,"e":50.8,"f":35.5,"g":0.55,"h":0.38,"i":"Southwest"},"Indiana":{"a":103.5,"b":24,"c":2.8,"d":0.26,"e":49.2,"f":37.8,"g":0.58,"h":0.42,"i":"Central"},"LA Clippers":{"a":98.0,"b":14,"c":1.5,"d":0.25,"e":50.0,"f":36.0,"g":0.55,"h":0.40,"i":"Pacific"},"LA Lakers":{"a":99.5,"b":15,"c":2.2,"d":0.27,"e":51.0,"f":35.8,"g":0.58,"h":0.42,"i":"Pacific"},"Memphis":{"a":100.8,"b":6,"c":4.5,"d":0.26,"e":52.2,"f":35.2,"g":0.68,"h":0.48,"i":"Southwest"},"Miami":{"a":97.5,"b":5,"c":3.8,"d":0.24,"e":50.8,"f":36.5,"g":0.65,"h":0.45,"i":"Southeast"},"Milwaukee":{"a":99.2,"b":9,"c":5.2,"d":0.28,"e":51.5,"f":37.2,"g":0.70,"h":0.52,"i":"Central"},"Minnesota":{"a":98.8,"b":4,"c":7.5,"d":0.25,"e":52.8,"f":36.2,"g":0.72,"h":0.55,"i":"Northwest"},"New Orleans":{"a":100.0,"b":16,"c":1.8,"d":0.27,"e":50.5,"f":36.8,"g":0.55,"h":0.38,"i":"Southwest"},"New York":{"a":98.5,"b":7,"c":6.2,"d":0.25,"e":51.2,"f":37.0,"g":0.68,"h":0.52,"i":"Atlantic"},"Oklahoma City":{"a":99.8,"b":1,"c":12.5,"d":0.26,"e":52.0,"f":37.5,"g":0.82,"h":0.68,"i":"Northwest"},"Orlando":{"a":97.0,"b":11,"c":3.2,"d":0.26,"e":51.5,"f":35.5,"g":0.62,"h":0.45,"i":"Southeast"},"Philadelphia":{"a":98.2,"b":13,"c":2.5,"d":0.28,"e":50.2,"f":36.2,"g":0.58,"h":0.42,"i":"Atlantic"},"Phoenix":{"a":99.0,"b":17,"c":2.0,"d":0.25,"e":49.8,"f":36.8,"g":0.60,"h":0.42,"i":"Pacific"},"Portland":{"a":99.5,"b":27,"c":-5.5,"d":0.24,"e":48.5,"f":35.0,"g":0.40,"h":0.25,"i":"Northwest"},"Sacramento":{"a":101.2,"b":19,"c":0.8,"d":0.25,"e":49.5,"f":36.5,"g":0.55,"h":0.38,"i":"Pacific"},"San Antonio":{"a":100.5,"b":25,"c":-4.8,"d":0.26,"e":49.0,"f":34.8,"g":0.42,"h":0.28,"i":"Southwest"},"Toronto":{"a":98.8,"b":21,"c":-1.5,"d":0.24,"e":49.5,"f":35.5,"g":0.48,"h":0.32,"i":"Atlantic"},"Utah":{"a":100.2,"b":30,"c":-7.5,"d":0.25,"e":48.0,"f":35.2,"g":0.35,"h":0.22,"i":"Northwest"},"Washington":{"a":101.0,"b":23,"c":-6.2,"d":0.27,"e":48.8,"f":34.5,"g":0.38,"h":0.25,"i":"Southeast"}}
_S = {"Atlanta":{"Trae Young":(3,"O"),"Dejounte Murray":(2,"B"),"Jalen Johnson":(2,"B")},"Boston":{"Jayson Tatum":(3,"B"),"Jaylen Brown":(3,"O"),"Derrick White":(2,"D"),"Kristaps Porzingis":(2,"B")},"Brooklyn":{"Mikal Bridges":(2,"B"),"Cam Thomas":(2,"O"),"Ben Simmons":(1,"D")},"Charlotte":{"LaMelo Ball":(3,"O"),"Brandon Miller":(2,"O"),"Miles Bridges":(2,"B")},"Chicago":{"Zach LaVine":(2,"O"),"DeMar DeRozan":(2,"O"),"Coby White":(2,"O")},"Cleveland":{"Donovan Mitchell":(3,"O"),"Darius Garland":(2,"O"),"Evan Mobley":(2,"D"),"Jarrett Allen":(2,"D")},"Dallas":{"Luka Doncic":(3,"O"),"Kyrie Irving":(3,"O"),"PJ Washington":(2,"D"),"Dereck Lively II":(2,"D")},"Denver":{"Nikola Jokic":(3,"B"),"Jamal Murray":(3,"O"),"Aaron Gordon":(2,"D"),"Michael Porter Jr.":(2,"O")},"Detroit":{"Cade Cunningham":(2,"O"),"Jaden Ivey":(2,"O"),"Jalen Duren":(1,"D")},"Golden State":{"Stephen Curry":(3,"O"),"Draymond Green":(2,"D"),"Andrew Wiggins":(2,"B"),"Klay Thompson":(2,"O")},"Houston":{"Jalen Green":(2,"O"),"Alperen Sengun":(2,"B"),"Fred VanVleet":(2,"O"),"Jabari Smith Jr.":(2,"D")},"Indiana":{"Tyrese Haliburton":(3,"O"),"Pascal Siakam":(2,"B"),"Myles Turner":(2,"D"),"Bennedict Mathurin":(2,"O")},"LA Clippers":{"Kawhi Leonard":(3,"B"),"Paul George":(3,"B"),"James Harden":(3,"O"),"Norman Powell":(2,"O")},"LA Lakers":{"LeBron James":(3,"B"),"Anthony Davis":(3,"B"),"Austin Reaves":(2,"O"),"D'Angelo Russell":(2,"O")},"Memphis":{"Ja Morant":(3,"O"),"Desmond Bane":(2,"O"),"Jaren Jackson Jr.":(2,"D"),"Marcus Smart":(2,"D")},"Miami":{"Jimmy Butler":(3,"B"),"Bam Adebayo":(3,"D"),"Tyler Herro":(2,"O"),"Terry Rozier":(2,"O")},"Milwaukee":{"Giannis Antetokounmpo":(3,"B"),"Damian Lillard":(3,"O"),"Khris Middleton":(2,"O"),"Brook Lopez":(2,"D")},"Minnesota":{"Anthony Edwards":(3,"O"),"Karl-Anthony Towns":(2,"O"),"Rudy Gobert":(3,"D"),"Jaden McDaniels":(2,"D")},"New Orleans":{"Zion Williamson":(3,"O"),"Brandon Ingram":(2,"O"),"CJ McCollum":(2,"O"),"Herb Jones":(2,"D")},"New York":{"Jalen Brunson":(3,"O"),"Julius Randle":(2,"B"),"RJ Barrett":(2,"O"),"Mitchell Robinson":(2,"D")},"Oklahoma City":{"Shai Gilgeous-Alexander":(3,"O"),"Chet Holmgren":(3,"D"),"Jalen Williams":(2,"B"),"Lu Dort":(2,"D")},"Orlando":{"Paolo Banchero":(3,"O"),"Franz Wagner":(2,"B"),"Wendell Carter Jr.":(2,"D"),"Jalen Suggs":(2,"D")},"Philadelphia":{"Joel Embiid":(3,"B"),"Tyrese Maxey":(2,"O"),"Tobias Harris":(2,"O")},"Phoenix":{"Kevin Durant":(3,"O"),"Devin Booker":(3,"O"),"Bradley Beal":(2,"O"),"Jusuf Nurkic":(2,"D")},"Portland":{"Anfernee Simons":(2,"O"),"Scoot Henderson":(2,"O"),"Jerami Grant":(2,"B")},"Sacramento":{"De'Aaron Fox":(3,"O"),"Domantas Sabonis":(3,"B"),"Keegan Murray":(2,"O"),"Malik Monk":(2,"O")},"San Antonio":{"Victor Wembanyama":(3,"B"),"Devin Vassell":(2,"O"),"Keldon Johnson":(2,"O")},"Toronto":{"Scottie Barnes":(2,"B"),"Pascal Siakam":(2,"B"),"RJ Barrett":(2,"O")},"Utah":{"Lauri Markkanen":(2,"O"),"Jordan Clarkson":(2,"O"),"Walker Kessler":(2,"D")},"Washington":{"Jordan Poole":(2,"O"),"Kyle Kuzma":(2,"O"),"Bilal Coulibaly":(1,"D")}}

def _d(l1,l2):
    from math import radians,sin,cos,sqrt,atan2
    a1,o1=radians(l1[0]),radians(l1[1]);a2,o2=radians(l2[0]),radians(l2[1])
    da,do=a2-a1,o2-o1;x=sin(da/2)**2+cos(a1)*cos(a2)*sin(do/2)**2
    return 3959*2*atan2(sqrt(x),sqrt(1-x))

def _i(t,inj):
    ti=inj.get(t,[]);st=STAR_PLAYERS.get(t,[]);s=0;o=[]
    for i in ti:
        n=i.get("name","");u=i.get("status","").upper();x=any(p.lower()in n.lower()for p in st)
        if"OUT"in u:s+=4.0 if x else 1.0;o.append(n)if x else None
        elif any(k in u for k in["DAY","GTD","QUEST"]):s+=2.5 if x else 0.5
    return s,o

def _ml(h,a,y,inj):
    H,A=_T.get(h,{}),_T.get(a,{});hl,al=TEAM_LOCATIONS.get(h,(0,0)),TEAM_LOCATIONS.get(a,(0,0))
    sh,sa=0,0
    if a in y and h not in y:sh+=1.0
    elif h in y and a not in y:sa+=1.0
    else:sh+=0.5;sa+=0.5
    nd=H.get('c',0)-A.get('c',0)
    if nd>5:sh+=1.0
    elif nd>2:sh+=0.7
    elif nd>0:sh+=0.5
    elif nd>-2:sa+=0.5
    elif nd>-5:sa+=0.7
    else:sa+=1.0
    hd,ad=H.get('b',15),A.get('b',15)
    if hd<=5:sh+=1.0
    elif hd<=10:sh+=0.7
    elif hd<=15:sh+=0.4
    if ad<=5:sa+=1.0
    elif ad<=10:sa+=0.7
    elif ad<=15:sa+=0.4
    sh+=1.0
    hi,hs=_i(h,inj);ai,ast=_i(a,inj);id=ai-hi
    if id>3:sh+=1.0
    elif id>1:sh+=0.6
    elif id<-3:sa+=1.0
    elif id<-1:sa+=0.6
    else:sh+=0.3;sa+=0.3
    tm=_d(al,hl)
    if tm>2000:sh+=1.0
    elif tm>1500:sh+=0.7
    elif tm>1000:sh+=0.5
    elif tm>500:sh+=0.3
    hw,aw=H.get('g',0.5),A.get('h',0.5)
    if hw>0.65:sh+=0.8
    elif hw>0.55:sh+=0.5
    if aw<0.35:sh+=0.5
    elif aw<0.45:sh+=0.3
    if H.get('i')==A.get('i')and H.get('i'):sh+=0.5
    if h=="Denver":sh+=1.0
    if H.get('c',0)>5:sh+=0.5
    if A.get('c',0)>5:sa+=0.5
    t=sh+sa
    if t>0:hf,af=round((sh/t)*10,1),round((sa/t)*10,1)
    else:hf,af=5.0,5.0
    if hf>=af:return h,hf,round((hf-5)*4,0),hs,ast
    else:return a,af,round((af-5)*4,0),hs,ast

def _tot(h,a,y,inj):
    H,A=_T.get(h,{}),_T.get(a,{});su,so=0,0
    ap=(H.get('a',100)+A.get('a',100))/2
    if ap<98.5:su+=1.5
    elif ap<99.5:su+=1.0
    elif ap>101:so+=1.5
    elif ap>100:so+=1.0
    ad=(H.get('b',15)+A.get('b',15))/2
    if ad<=8:su+=1.5
    elif ad<=12:su+=1.0
    elif ad>=22:so+=1.5
    elif ad>=18:so+=1.0
    hb,ab=h in y,a in y
    if hb and ab:su+=1.5
    elif hb or ab:su+=0.75
    a3=(H.get('f',36)+A.get('f',36))/2
    if a3<35.5:su+=1.0
    elif a3>37.5:so+=1.0
    hi,hs=_i(h,inj);ai,ast=_i(a,inj)
    if hs or ast:su+=1.0
    nd=abs(H.get('c',0)-A.get('c',0))
    if nd>10:so+=0.75
    elif nd<3:su+=0.5
    if h=="Denver":su+=0.75
    af=(H.get('d',0.25)+A.get('d',0.25))/2
    if af>0.27:su+=0.5
    elif af<0.23:so+=0.5
    ar=(H.get('e',50)+A.get('e',50))/2
    if ar>51.5:su+=0.5
    if H.get('g',0.5)>0.65 and H.get('c',0)>5:so+=0.5
    t=su+so
    if t>0:uf,of=round((su/t)*10,1),round((so/t)*10,1)
    else:uf,of=5.0,5.0
    if uf>=of:return"NO",uf
    else:return"YES",of

def _gt(n,t):
    ts=_S.get(t,{})
    for s,(r,p)in ts.items():
        if s.lower()in n.lower()or n.lower()in s.lower():return r,p
    return 0,None

def _sr(t):
    if t==3:return"⭐⭐⭐"
    elif t==2:return"⭐⭐"
    elif t==1:return"⭐"
    return""

def _pt(p):
    if p=="O":return"🔥"
    elif p=="D":return"🛡️"
    elif p=="B":return"⚔️"
    return""

def get_detailed_injuries(team,injuries):
    ti=injuries.get(team,[]);d=[]
    for i in ti:
        n=i.get("name","");u=i.get("status","").upper();t,p=_gt(n,team)
        s=_sr(t);e=_pt(p)
        if"OUT"in u:ss="OUT"
        elif"DAY"in u or"DTD"in u:ss="DTD"
        elif"QUEST"in u or"GTD"in u:ss="GTD"
        else:ss=u[:10]
        d.append({"name":n,"status":ss,"tier":t,"stars":s,"type_emoji":e})
    d.sort(key=lambda x:x['tier'],reverse=True)
    return d

def get_signal_tier(score):
    if score>=8.0:return"🟢 STRONG BUY","#00ff00"
    elif score>=6.5:return"🔵 BUY","#00aaff"
    elif score>=5.5:return"🟡 LEAN","#ffff00"
    elif score>=4.5:return"⚪ TOSS-UP","#888888"
    else:return"🔴 SKIP","#ff0000"

def get_totals_signal_tier(score,pick):
    if score>=8.0:return f"🟢 STRONG {pick}","#00ff00"
    elif score>=6.5:return f"🔵 {pick}","#00aaff"
    elif score>=5.5:return f"🟡 LEAN {pick}","#ffff00"
    elif score>=4.5:return"⚪ TOSS-UP","#888888"
    else:return"🔴 SKIP","#ff0000"

# ========== DATA FETCHERS ==========
def fetch_espn_scores(date_key=None):
    eastern=pytz.timezone('US/Eastern');td=datetime.now(eastern).strftime('%Y%m%d')
    url=f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={td}"
    try:
        r=requests.get(url,timeout=10);d=r.json();g={}
        for e in d.get("events",[]):
            c=e.get("competitions",[{}])[0];cs=c.get("competitors",[])
            if len(cs)<2:continue
            ht,at,hs,aws=None,None,0,0
            for x in cs:
                n=x.get("team",{}).get("displayName","");tn=TEAM_ABBREVS.get(n,n);sc=int(x.get("score",0)or 0)
                if x.get("homeAway")=="home":ht,hs=tn,sc
                else:at,aws=tn,sc
            so=e.get("status",{});st=so.get("type",{}).get("name","STATUS_SCHEDULED")
            cl=so.get("displayClock","");pr=so.get("period",0)
            gk=f"{at}@{ht}";g[gk]={"away_team":at,"home_team":ht,"away_score":aws,"home_score":hs,"total":aws+hs,"period":pr,"clock":cl,"status_type":st}
        return g
    except:return{}

def fetch_yesterday_teams():
    y=(datetime.now(pytz.timezone('US/Eastern'))-timedelta(days=1)).strftime('%Y%m%d')
    url=f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={y}"
    try:
        r=requests.get(url,timeout=10);d=r.json();t=set()
        for e in d.get("events",[]):
            c=e.get("competitions",[{}])[0]
            for x in c.get("competitors",[]):
                fn=x.get("team",{}).get("displayName","");tn=TEAM_ABBREVS.get(fn,fn);t.add(tn)
        return t
    except:return set()

def fetch_espn_injuries():
    inj={}
    try:
        url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
        r=requests.get(url,timeout=10);d=r.json()
        il=d.get("injuries",d.get("teams",[]))
        for td in il:
            tn=td.get("team",{}).get("displayName","")
            if not tn:tn=td.get("team",{}).get("name","")
            if not tn:tn=td.get("displayName","")
            tk=TEAM_ABBREVS.get(tn,tn)
            if not tk:continue
            inj[tk]=[]
            pl=td.get("injuries",td.get("athletes",[]))
            for p in pl:
                n=p.get("athlete",{}).get("displayName","")
                if not n:n=p.get("displayName","")
                if not n:n=p.get("name","")
                s=p.get("status","")
                if not s:s=p.get("type",{}).get("description","")
                if n:inj[tk].append({"name":n,"status":s})
    except:pass
    return inj

def get_minutes_played(period,clock,status_type):
    if status_type=="STATUS_FINAL":return 48 if period<=4 else 48+(period-4)*5
    if status_type=="STATUS_HALFTIME":return 24
    if period==0:return 0
    try:
        cs=str(clock)
        if':'in cs:p=cs.split(':');m=int(p[0]);s=int(float(p[1]))if len(p)>1 else 0
        else:m=0;s=float(cs)if cs else 0
        tl=m+s/60
        if period<=4:return(period-1)*12+(12-tl)
        else:return 48+(period-5)*5+(5-tl)
    except:return(period-1)*12 if period<=4 else 48+(period-5)*5

# ========== FETCH DATA ==========
games=fetch_espn_scores(date_key=today_str)
game_list=sorted(list(games.keys()))
yesterday_teams_raw=fetch_yesterday_teams()
injuries=fetch_espn_injuries()
now=datetime.now(pytz.timezone('US/Eastern'))

today_teams=set()
for gk in games.keys():
    p=gk.split("@");today_teams.add(p[0]);today_teams.add(p[1])
yesterday_teams=yesterday_teams_raw.intersection(today_teams)

# ========== HEADER ==========
st.title("🎯 NBA EDGE FINDER")
st.markdown("**📝 TEST MODE — Paper Tracking Only**")
hdr1,hdr2,hdr3=st.columns([3,1,1])
hdr1.caption(f"{auto_status} | Last update: {now.strftime('%I:%M:%S %p ET')} | v15.30 TEST")

if hdr2.button("🔄 Auto"if not st.session_state.auto_refresh else"⏹️ Stop",use_container_width=True):
    st.session_state.auto_refresh=not st.session_state.auto_refresh;st.rerun()
if hdr3.button("🔄 Refresh",use_container_width=True):st.rerun()

# ========== INJURY REPORT ==========
st.subheader("🏥 INJURY REPORT - TODAY'S GAMES")

if game_list:
    teams_playing=set()
    for gk in game_list:p=gk.split("@");teams_playing.add(p[0]);teams_playing.add(p[1])
    star_injuries=[]
    for team in sorted(teams_playing):
        ti=get_detailed_injuries(team,injuries)
        for i in ti:
            if i['tier']>=2:star_injuries.append((team,i))
    if star_injuries:
        st.markdown("### ⭐ KEY PLAYER INJURIES")
        cols=st.columns(3)
        for idx,(team,i)in enumerate(star_injuries):
            with cols[idx%3]:
                sc="#ff0000"if i['status']=="OUT"else"#ffaa00"
                st.markdown(f"<div style='background:linear-gradient(135deg,#2a1a1a,#1a1a2e);padding:10px;border-radius:8px;border-left:4px solid {sc};margin-bottom:8px'><span style='color:#fff;font-weight:bold'>{i['stars']} {i['name']}</span> {i['type_emoji']}<br><span style='color:{sc};font-size:0.9em'>{i['status']}</span><span style='color:#888;font-size:0.85em'> • {team}</span></div>",unsafe_allow_html=True)
    else:st.info("✅ No key player injuries reported for today's games")
else:st.info("No games scheduled today")

st.divider()
if yesterday_teams:st.info(f"📅 **Back-to-Back Teams Today**: {', '.join(sorted(yesterday_teams))}")
else:st.info("📅 **No B2B teams today** — all teams are rested")
st.divider()

# ========== BIG SNAPSHOT ==========
st.subheader("🎯 BIG SNAPSHOT – TODAY'S ML PICKS")
st.caption(f"📅 Snapshot date: {st.session_state.get('snapshot_date','N/A')}")

ml_results=[]
for gk,g in games.items():
    a,h=g["away_team"],g["home_team"]
    try:
        pick,score,edge,hs,ast=_ml(h,a,yesterday_teams,injuries)
        tier,color=get_signal_tier(score)
        ab2b,hb2b=a in yesterday_teams,h in yesterday_teams
        blowout=ab2b and not hb2b and pick==h
        ml_results.append({"game":f"{a} vs {h}","pick":pick,"score":score,"edge":edge,"tier":tier,"color":color,"away":a,"home":h,"blowout":blowout})
    except:continue

st.session_state["big_snapshot"]=ml_results
ml_results.sort(key=lambda x:x["score"],reverse=True)

tiers={"🟢 STRONG BUY":[],"🔵 BUY":[],"🟡 LEAN":[],"⚪ TOSS-UP":[]}
for r in ml_results:
    if r["score"]>=8.0:tiers["🟢 STRONG BUY"].append(r)
    elif r["score"]>=6.5:tiers["🔵 BUY"].append(r)
    elif r["score"]>=5.5:tiers["🟡 LEAN"].append(r)
    else:tiers["⚪ TOSS-UP"].append(r)

for label,rows in tiers.items():
    if not rows:continue
    st.markdown(f"<div style='font-size:1.1em;font-weight:700;margin:8px 0 4px 0'>{label}</div>",unsafe_allow_html=True)
    for r in rows:
        url=build_kalshi_ml_url(r["away"],r["home"])
        et=f"+{int(r['edge'])}%";bb="🔥 "if r.get("blowout")else""
        st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;background:linear-gradient(135deg,#0f172a,#020617);padding:6px 12px;margin-bottom:4px;border-radius:6px;border-left:3px solid {r['color']}"><div style="flex:1;min-width:0"><span style="color:#fff;font-size:0.9em;font-weight:600">{bb}{r['pick']}</span><span style="color:#666;font-size:0.85em"> vs {r['away']if r['pick']==r['home']else r['home']}</span><span style="color:#38bdf8;font-weight:600;font-size:0.85em;margin-left:8px">{r['score']}/10 | {et}</span></div><a href="{url}" target="_blank" style="background:#16a34a;color:#fff;padding:4px 10px;border-radius:5px;font-size:0.8em;text-decoration:none;font-weight:600;white-space:nowrap">VIEW {r['pick'][:3].upper()}</a></div>""",unsafe_allow_html=True)

strong_picks=[r for r in ml_results if r["score"]>=6.5]
if strong_picks:
    st.markdown("")
    col_add,col_price=st.columns([2,1])
    default_price=col_price.number_input("Default price ¢",min_value=1,max_value=99,value=50,key="auto_add_price")
    if col_add.button(f"➕ Add All {len(strong_picks)} Picks to Paper Tracker",use_container_width=True):
        added=0
        for r in strong_picks:
            gk=f"{r['away']}@{r['home']}"
            at=any(p.get('game')==gk and p.get('type')=='ml'and p.get('pick')==r['pick']for p in st.session_state.positions)
            if not at:st.session_state.positions.append({"game":gk,"type":"ml","pick":r['pick'],"price":default_price,"contracts":1,"cost":round(default_price/100,2)});added+=1
        if added>0:save_positions(st.session_state.positions);st.success(f"✅ Added {added} picks to paper tracker");st.rerun()
        else:st.info("All picks already in tracker")

st.divider()

# ========== BLOWOUT RISK ==========
st.subheader("🔥 BLOWOUT RISK — Tired Away @ Fresh Home")

blowout_games=[]
for gk,g in games.items():
    a,h=g["away_team"],g["home_team"]
    ab2b,hb2b=a in yesterday_teams,h in yesterday_teams
    if ab2b and not hb2b:
        hs,aws=_T.get(h,{}),_T.get(a,{})
        ne=hs.get('c',0)-aws.get('c',0)
        blowout_games.append({"game":gk,"home":h,"away":a,"net_edge":ne})

blowout_games.sort(key=lambda x:x['net_edge'],reverse=True)

if blowout_games:
    for bg in blowout_games:
        url=build_kalshi_ml_url(bg["away"],bg["home"])
        ec="#00ff00"if bg['net_edge']>5 else"#ffff00"if bg['net_edge']>0 else"#ff8800"
        st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;background:linear-gradient(135deg,#2a1a0a,#1a0a0a);padding:8px 12px;margin-bottom:4px;border-radius:6px;border-left:3px solid #ff6600"><div style="flex:1"><span style="color:#ff6600;font-weight:700">🔥 {bg['home']}</span><span style="color:#888"> vs tired {bg['away']}</span><span style="color:{ec};font-size:0.85em;margin-left:10px">Net: {bg['net_edge']:+.1f}</span></div><a href="{url}" target="_blank" style="background:#ff6600;color:#fff;padding:4px 10px;border-radius:5px;font-size:0.8em;text-decoration:none;font-weight:600">VIEW {bg['home'][:3].upper()}</a></div>""",unsafe_allow_html=True)
else:st.info("No blowout setups today — no tired away teams @ fresh home teams")

st.divider()

# ========== ADD NEW POSITION ==========
st.subheader("➕ ADD PAPER POSITION")

game_options=["Select a game..."]+[gk.replace("@"," @ ")for gk in game_list]
selected_game=st.selectbox("🏀 Game",game_options,key="game_select")

if selected_game!="Select a game...":
    parts=selected_game.replace(" @ ","@").split("@")
    at,ht=parts[0],parts[1]
    c1,c2=st.columns(2)
    c1.link_button(f"🔗 ML on Kalshi",build_kalshi_ml_url(at,ht),use_container_width=True)
    c2.link_button(f"🔗 Totals on Kalshi",build_kalshi_totals_url(at,ht),use_container_width=True)

market_type=st.radio("📈 Market Type",["Moneyline (Winner)","Totals (Over/Under)"],horizontal=True,key="mkt_type")

p1,p2,p3=st.columns(3)

if market_type=="Totals (Over/Under)":
    with p1:
        st.caption("📊 Side")
        yn=st.radio("",["NO (Under)","YES (Over)"],horizontal=True,key="totals_side_radio")
        st.session_state.selected_side="NO"if yn.startswith("NO")else"YES"
    st.session_state.selected_threshold=st.number_input("🎯 Threshold",min_value=180.0,max_value=280.0,value=st.session_state.selected_threshold,step=0.5)
else:
    with p1:
        if selected_game!="Select a game...":
            parts=selected_game.replace(" @ ","@").split("@")
            st.caption("📊 Pick Winner")
            st.session_state.selected_ml_pick=st.radio("",[parts[1],parts[0]],horizontal=True,key="ml_pick_radio")
        else:st.session_state.selected_ml_pick=None;st.warning("⚠️ Select a game first")

price_paid=p2.number_input("💵 Price (¢)",min_value=1,max_value=99,value=50,step=1)
contracts=p3.number_input("📄 Contracts",min_value=1,value=st.session_state.default_contracts,step=1)

if st.button("✅ ADD PAPER POSITION",use_container_width=True,type="primary"):
    if selected_game=="Select a game...":st.error("Select a game first!")
    else:
        gk=selected_game.replace(" @ ","@");parts=gk.split("@");at,ht=parts[0],parts[1]
        if market_type=="Moneyline (Winner)":
            if st.session_state.selected_ml_pick is None:st.error("Pick a team first!")
            else:
                st.session_state.positions.append({"game":gk,"type":"ml","pick":st.session_state.selected_ml_pick,"price":price_paid,"contracts":contracts,"cost":round(price_paid*contracts/100,2)})
                save_positions(st.session_state.positions);st.success(f"✅ Paper position added: {st.session_state.selected_ml_pick} ML @ {price_paid}¢");st.rerun()
        else:
            st.session_state.positions.append({"game":gk,"type":"totals","side":st.session_state.selected_side,"threshold":st.session_state.selected_threshold,"price":price_paid,"contracts":contracts,"cost":round(price_paid*contracts/100,2)})
            save_positions(st.session_state.positions);st.success(f"✅ Paper position added: {st.session_state.selected_side} {st.session_state.selected_threshold} @ {price_paid}¢");st.rerun()

st.divider()

# ========== ACTIVE POSITIONS ==========
st.subheader("📈 PAPER POSITIONS")

if st.session_state.positions:
    for idx,pos in enumerate(st.session_state.positions):
        gk=pos['game'];g=games.get(gk)
        price=pos.get('price',50);contracts=pos.get('contracts',1);cost=pos.get('cost',round(price*contracts/100,2))
        pt=pos.get('type','totals');pw=round((100-price)*contracts/100,2);pl=cost
        
        if g:
            total=g['total'];mins=get_minutes_played(g['period'],g['clock'],g['status_type'])
            is_final=g['status_type']=="STATUS_FINAL";gs="FINAL"if is_final else f"Q{g['period']} {g['clock']}"
            
            if pt=='ml':
                pick=pos.get('pick','');parts=gk.split("@");at,ht=parts[0],parts[1]
                hs,aws=g['home_score'],g['away_score'];ps=hs if pick==ht else aws;os=aws if pick==ht else hs;lead=ps-os
                if is_final:
                    won=ps>os
                    if won:sl,sc="✅ WON!","#00ff00";pd,pc=f"+${pw:.2f}","#00ff00"
                    else:sl,sc="❌ LOST","#ff0000";pd,pc=f"-${pl:.2f}","#ff0000"
                elif mins>0:
                    if lead>=15:sl,sc="🟢 CRUISING","#00ff00"
                    elif lead>=8:sl,sc="🟢 LEADING","#00ff00"
                    elif lead>=1:sl,sc="🟡 AHEAD","#ffff00"
                    elif lead>=-5:sl,sc="🟠 CLOSE","#ff8800"
                    else:sl,sc="🔴 BEHIND","#ff0000"
                    pd,pc=f"Win: +${pw:.2f}","#888888"
                else:sl,sc="⏳ WAITING","#888888";lead=0;pd,pc=f"Win: +${pw:.2f}","#888888"
                st.markdown(f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:10px;border:2px solid {sc};margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><div><span style='color:#fff;font-size:1.2em;font-weight:bold'>{gk.replace('@',' @ ')}</span><span style='color:#888;margin-left:10px'>{gs}</span><span style='color:#ffaa00;margin-left:10px;font-size:0.85em'>📝 Paper</span></div><span style='color:{sc};font-size:1.3em;font-weight:bold'>{sl}</span></div><div style='margin-top:10px;display:flex;gap:30px;flex-wrap:wrap'><span style='color:#aaa'>🎯 <b style=\"color:#fff\">ML: {pick}</b></span><span style='color:#aaa'>💵 <b style=\"color:#fff\">{contracts}x @ {price}¢</b> (${cost:.2f})</span><span style='color:#aaa'>📊 Score: <b style=\"color:#fff\">{ps}-{os}</b></span><span style='color:#aaa'>📈 Lead: <b style=\"color:{sc}\">{lead:+d}</b></span><span style='color:{pc}'>{pd}</span></div></div>",unsafe_allow_html=True)
            else:
                proj=round((total/mins)*48)if mins>0 else None
                cushion=(pos['threshold']-proj)if pos.get('side')=="NO"and proj else((proj-pos['threshold'])if proj else 0)
                if is_final:
                    won=(total<pos['threshold'])if pos.get('side')=="NO"else(total>pos['threshold'])
                    if won:sl,sc="✅ WON!","#00ff00";pd,pc=f"+${pw:.2f}","#00ff00"
                    else:sl,sc="❌ LOST","#ff0000";pd,pc=f"-${pl:.2f}","#ff0000"
                elif proj:
                    if cushion>=15:sl,sc="🟢 VERY SAFE","#00ff00"
                    elif cushion>=8:sl,sc="🟢 LOOKING GOOD","#00ff00"
                    elif cushion>=3:sl,sc="🟡 ON TRACK","#ffff00"
                    elif cushion>=-3:sl,sc="🟠 WARNING","#ff8800"
                    else:sl,sc="🔴 AT RISK","#ff0000"
                    pd,pc=f"Win: +${pw:.2f}","#888888"
                else:sl,sc="⏳ WAITING","#888888";pd,pc=f"Win: +${pw:.2f}","#888888"
                st.markdown(f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:15px;border-radius:10px;border:2px solid {sc};margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><div><span style='color:#fff;font-size:1.2em;font-weight:bold'>{gk.replace('@',' @ ')}</span><span style='color:#888;margin-left:10px'>{gs}</span><span style='color:#ffaa00;margin-left:10px;font-size:0.85em'>📝 Paper</span></div><span style='color:{sc};font-size:1.3em;font-weight:bold'>{sl}</span></div><div style='margin-top:10px;display:flex;gap:30px;flex-wrap:wrap'><span style='color:#aaa'>📊 <b style=\"color:#fff\">{pos.get('side','NO')} {pos.get('threshold',0)}</b></span><span style='color:#aaa'>💵 <b style=\"color:#fff\">{contracts}x @ {price}¢</b> (${cost:.2f})</span><span style='color:#aaa'>📈 Proj: <b style=\"color:#fff\">{proj if proj else '—'}</b></span><span style='color:#aaa'>🎯 Cushion: <b style=\"color:{sc}\">{cushion:+.0f}</b></span><span style='color:{pc}'>{pd}</span></div></div>",unsafe_allow_html=True)
            
            b1,b2=st.columns([3,1]);parts=gk.split("@")
            if pt=='ml':url=build_kalshi_ml_url(parts[0],parts[1])
            else:url=build_kalshi_totals_url(parts[0],parts[1])
            b1.link_button(f"🔗 View on Kalshi",url,use_container_width=True)
            if b2.button("🗑️ Remove",key=f"del_{idx}"):st.session_state.positions.pop(idx);save_positions(st.session_state.positions);st.rerun()
        else:
            if pt=='ml':dt=f"ML: {pos.get('pick','?')}"
            else:dt=f"{pos.get('side','NO')} {pos.get('threshold',0)}"
            st.markdown(f"<div style='background:#1a1a2e;padding:15px;border-radius:10px;border:1px solid #444;margin-bottom:10px'><span style='color:#888'>{gk.replace('@',' @ ')} — {dt} — {contracts}x @ {price}¢</span><span style='color:#666;margin-left:15px'>⏳ Game not started</span></div>",unsafe_allow_html=True)
            if st.button("🗑️ Remove",key=f"del_{idx}"):st.session_state.positions.pop(idx);save_positions(st.session_state.positions);st.rerun()
    
    if st.button("🗑️ Clear All Paper Positions",use_container_width=True):st.session_state.positions=[];save_positions(st.session_state.positions);st.rerun()
else:st.info("No paper positions tracked — use the form above to add your first position")

st.divider()

# ========== PACE SCANNER ==========
st.subheader("🔥 PACE SCANNER")

pace_data=[]
for gk,g in games.items():
    mins=get_minutes_played(g['period'],g['clock'],g['status_type'])
    if mins>=6:
        pace=round(g['total']/mins,2);proj=round(pace*48)
        pace_data.append({"game":gk,"pace":pace,"proj":proj,"total":g['total'],"mins":mins,"period":g['period'],"clock":g['clock'],"final":g['status_type']=="STATUS_FINAL"})

pace_data.sort(key=lambda x:x['pace'])

if pace_data:
    for p in pace_data:
        if p['pace']<4.5:lbl,clr="🟢 SLOW","#00ff00"
        elif p['pace']<4.8:lbl,clr="🟡 AVG","#ffff00"
        elif p['pace']<5.2:lbl,clr="🟠 FAST","#ff8800"
        else:lbl,clr="🔴 SHOOTOUT","#ff0000"
        status="FINAL"if p['final']else f"Q{p['period']} {p['clock']}"
        st.markdown(f"**{p['game'].replace('@',' @ ')}** — {p['total']} pts in {p['mins']:.0f} min — **{p['pace']}/min** <span style='color:{clr}'>**{lbl}**</span> — Proj: **{p['proj']}** — {status}",unsafe_allow_html=True)
else:st.info("No games with 6+ minutes played yet")

st.divider()

# ========== CUSHION SCANNER ==========
st.subheader("🎯 CUSHION SCANNER")

THRESHOLDS=[210.5,215.5,220.5,225.5,230.5,235.5,240.5,245.5,250.5,255.5]

cc1,cc2=st.columns(2)
min_minutes=cc1.selectbox("Min Minutes",[6,9,12,15,18],index=0,key="cush_min_select")
cush_side=cc2.selectbox("Side",["NO (Under)","YES (Over)"],key="cush_side_select")
is_no_side="NO"in cush_side

cushion_data=[]
for gk,g in games.items():
    mins=get_minutes_played(g['period'],g['clock'],g['status_type'])
    if mins<min_minutes:continue
    if g['status_type']=="STATUS_FINAL":continue
    total=g['total'];pace=total/mins if mins>0 else 0;proj=round(pace*48)
    if is_no_side:
        cands=[t for t in THRESHOLDS if t>proj]
        if len(cands)>=2:bl=cands[1]
        elif len(cands)==1:bl=cands[0]
        else:continue
        cushion=bl-proj
    else:
        cands=[t for t in THRESHOLDS if t<proj]
        if len(cands)>=2:bl=cands[-2]
        elif len(cands)==1:bl=cands[-1]
        else:continue
        cushion=proj-bl
    if cushion<6:continue
    if is_no_side:
        if pace<4.5:ps="✅ SLOW"
        elif pace<4.8:ps="⚠️ AVG"
        else:ps="❌ FAST"
    else:
        if pace>5.0:ps="✅ FAST"
        elif pace>4.7:ps="⚠️ AVG"
        else:ps="❌ SLOW"
    cushion_data.append({"game":gk,"status":f"Q{g['period']} {g['clock']}","total":total,"proj":proj,"bet_line":bl,"cushion":cushion,"pace":pace,"pace_status":ps,"mins":mins})

cushion_data.sort(key=lambda x:x['cushion'],reverse=True)

if cushion_data:
    for c in cushion_data:
        sl="NO"if is_no_side else"YES"
        st.markdown(f"""<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:12px 16px;margin-bottom:8px;border-radius:10px;border-left:4px solid #00ff00"><div style="display:flex;justify-content:space-between;align-items:center"><div><span style="color:#fff;font-weight:bold;font-size:1.1em">{c['game'].replace('@',' @ ')}</span><span style="color:#888;margin-left:10px">{c['status']}</span></div><span style="color:#00ff00;font-weight:bold;font-size:1.2em">+{c['cushion']:.0f} cushion</span></div><div style="margin-top:8px;display:flex;gap:25px;flex-wrap:wrap"><span style="color:#aaa">📊 Total: <b style="color:#fff">{c['total']}</b></span><span style="color:#aaa">📈 Proj: <b style="color:#fff">{c['proj']}</b></span><span style="color:#ff8800;font-weight:bold">🎯 {sl} {c['bet_line']}</span><span style="color:#aaa">🔥 {c['pace']:.2f}/min {c['pace_status']}</span></div></div>""",unsafe_allow_html=True)
else:st.info(f"No games with {min_minutes}+ minutes and 6+ cushion found")

st.divider()

# ========== ALL GAMES ==========
st.subheader("📺 ALL GAMES")
if games:
    cols=st.columns(4)
    for i,(k,g)in enumerate(games.items()):
        with cols[i%4]:
            st.write(f"**{g['away_team']}** {g['away_score']}")
            st.write(f"**{g['home_team']}** {g['home_score']}")
            status="FINAL"if g['status_type']=="STATUS_FINAL"else f"Q{g['period']} {g['clock']}"
            st.caption(f"{status} | {g['total']} pts")
else:st.info("No games today")

st.divider()
st.caption("⚠️ For entertainment only. Not financial advice.")
st.caption("v15.30 TEST - Paper tracking only (no live trading)")
