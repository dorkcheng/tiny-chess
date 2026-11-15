"""Tiny Chess Engine (MIT License)"""
import json, os, urllib.request

U = os.environ["MAKEFUN_ENV_URL"].rstrip("/")
V = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

def post(ep, data):
    req = urllib.request.Request(U + ep, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

def parse_fen(fen):
    sqs, col = [], fen.split()[1]
    for ch in fen.split()[0]:
        if ch != "/": sqs.extend("." * int(ch) if ch.isdigit() else ch)
    return sqs, col

def attack(b, s, t):
    p = b[s]
    if p == ".": return False
    fr, fc = divmod(s, 8)
    tr, tc = divmod(t, 8)
    dr, dc = tr - fr, tc - fc
    ar, ac = abs(dr), abs(dc)
    q = p.lower()
    if q == "p": return ac == 1 and dr == (1 if p.isupper() else -1)
    if q == "n": return (ar, ac) in ((1, 2), (2, 1))
    if q == "k": return max(ar, ac) == 1
    if q in ("r", "q") and (dr == 0 or dc == 0):
        step = ((dr > 0) - (dr < 0)) * 8 + ((dc > 0) - (dc < 0))
        return all(b[s + i * step] == "." for i in range(1, max(ar, ac)))
    if q in ("b", "q") and ar == ac:
        step = ((dr > 0) - (dr < 0)) * 8 + ((dc > 0) - (dc < 0))
        return all(b[s + i * step] == "." for i in range(1, ar))
    return False

def count_atk(b, t, col):
    is_w = (col == "w")
    return sum(attack(b, s, t) for s, p in enumerate(b) if p != "." and (p.isupper() == is_w))

def pst(p, c, r, b):
    dc, dr = 4 - abs(3.5 - c), 4 - abs(3.5 - r)
    if p == "p": return r * 7 + dc * 3
    if p == "n": return dc * 8 + dr * 8 + (12 if 3 <= r <= 5 else 0)
    if p == "b": return dc * 4 + dr * 5 + (8 if abs(c - r) in (0, 1, 6, 7) else 0)
    if p == "r": return dc * 3 + (8 if all(x != "P" for x in b[c::8]) else 0)
    return (dc + dr) * (3 if p == "q" else -3)

def sim_mv(b, mv, turn):
    s = (ord(mv[1]) - 49) * 8 + (ord(mv[0]) - 97)
    t = (ord(mv[3]) - 49) * 8 + (ord(mv[2]) - 97)
    p, cap = b[s], b[t]
    nb = list(b)
    nb[t], nb[s] = p, "."
    if p.lower() == "p":
        if t % 8 != s % 8 and cap == ".":
            nb[t - 8 if turn == "w" else t + 8] = "."
            cap = "p"
        if len(mv) > 4: nb[t] = mv[4].upper() if turn == "w" else mv[4].lower()
    if p.lower() == "k" and abs(t - s) == 2:
        rs = 7 if t > s else 0
        rt = t - 1 if t > s else t + 1
        nb[rt], nb[rs] = nb[rs], "."
    return nb, p, cap, t

def choose_move(fen, moves):
    b, turn = parse_fen(fen)
    enemy = "b" if turn == "w" else "w"
    is_w = (turn == "w")
    best_mv, best_sc = moves[0], -10**9

    for mv in moves:
        nb, p, cap, dst = sim_mv(b, mv, turn)
        sc = 0
        for i, q in enumerate(nb):
            if q != ".":
                r, c = divmod(i, 8)
                nr = r if q.isupper() else (7 - r)
                val = V[q.lower()] + pst(q.lower(), c, nr, nb)
                sc += val if q.isupper() else -val
        sc *= (1 if is_w else -1)

        if cap != ".": sc += V[cap.lower()] * 12 - V[p.lower()]
        if len(mv) > 4: sc += 900

        en_atks = count_atk(nb, dst, enemy)
        if en_atks > 0:
            defended = count_atk(nb, dst, turn)
            sc -= V[nb[dst].lower()] * (3 if defended else 7) * en_atks

        my_k = next((i for i, q in enumerate(nb) if q == ("k" if is_w else "K")), -1)
        en_k = next((i for i, q in enumerate(nb) if q == ("K" if is_w else "k")), -1)
        if my_k >= 0 and count_atk(nb, my_k, enemy): sc -= 10000
        if en_k >= 0 and count_atk(nb, en_k, turn): sc += 80

        if sc > best_sc: best_sc, best_mv = sc, mv

    return best_mv

while True:
    g = post("/game", {})
    if g.get("status") == "done": break
    while g.get("status") == "your_move":
        mv = choose_move(g["fen"], g["legal_moves"])
        g = post("/move", {"game": g["game"], "move": mv})

