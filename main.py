import json,os,urllib.request
U=os.environ["MAKEFUN_ENV_URL"].rstrip("/")
V=dict(zip("pnbrqk",(100,320,330,500,900,20000)))

def post(path,data):
    r=urllib.request.Request(U+path,json.dumps(data).encode(),
                            {"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r).read())

def board(fen):
    b=[]
    for c in fen.split()[0]:
        if c!="/": b.extend("."*int(c) if c.isdigit() else c)
    return b,fen.split()[1]

def attack(b,s,t):
    p=b[s]
    if p==".": return False
    r,f=divmod(s,8)
    y,x=divmod(t,8)
    dr,df=y-r,x-f
    q=p.lower()
    a,c=abs(dr),abs(df)
    if q=="p": return c==1 and dr==(1 if p.isupper() else -1)
    if q=="n": return (a,c) in ((1,2),(2,1))
    if q=="k": return max(a,c)==1
    if not (q in "rq" and (not dr or not df) or q in "bq" and a==c):
        return False
    step=((dr>0)-(dr<0))*8+(df>0)-(df<0)
    return all(b[s+i*step]=="." for i in range(1,max(a,c)))

def count(b,t,turn):
    return sum(attack(b,s,t) for s,p in enumerate(b)
               if p!="." and p.isupper()==(turn=="w"))

def pst(p,f,r,b):
    c,d=4-abs(3.5-f),4-abs(3.5-r)
    if p=="p": return r*7+c*3
    if p=="n": return c*8+d*8+12*(3<=r<=5)
    if p=="b": return c*4+d*5+8*(abs(f-r) in (0,1,6,7))
    if p=="r": return c*3+8*all(x!="P" for x in b[f::8])
    return (c+d)*(3 if p=="q" else -3)

def apply(b,m,turn):
    s=(ord(m[1])-49)*8+ord(m[0])-97
    t=(ord(m[3])-49)*8+ord(m[2])-97
    p,cap=b[s],b[t]
    b=b[:]
    b[t],b[s]=p,"."
    if p.lower()=="p":
        if t%8!=s%8 and cap==".":
            b[t-8 if turn=="w" else t+8]="."
            cap="p"
        if len(m)>4: b[t]=m[4].upper() if turn=="w" else m[4].lower()
    if p.lower()=="k" and abs(t-s)==2:
        rs=7 if t>s else 0
        rt=t-1 if t>s else t+1
        b[rt],b[rs]=b[rs],"."
    return b,p,cap,t

def choose(fen,moves):
    b,turn=board(fen)
    enemy="b" if turn=="w" else "w"
    sign=1 if turn=="w" else -1
    best,bs=moves[0],-10**9
    for m in moves:
        x,p,cap,t=apply(b,m,turn)
        z=0
        for i,q in enumerate(x):
            if q!=".":
                r,f=divmod(i,8)
                z+=(V[q.lower()]+pst(q.lower(),f,r if q.isupper() else 7-r,x))*(1 if q.isupper() else -1)
        z*=sign
        if cap!=".": z+=V[cap.lower()]*12-V[p.lower()]
        if len(m)>4: z+=900
        a=count(x,t,enemy)
        if a: z-=V[x[t].lower()]*(3 if count(x,t,turn) else 7)*a
        k=next((i for i,q in enumerate(x) if q==("k" if turn=="w" else "K")),-1)
        ek=next((i for i,q in enumerate(x) if q==("K" if turn=="w" else "k")),-1)
        if k>=0 and count(x,k,enemy): z-=10000
        if ek>=0 and count(x,ek,turn): z+=80
        if z>bs: bs,best=z,m
    return best

while True:
    g=post("/game",{})
    if g["status"]=="done": break
    while g["status"]=="your_move":
        g=post("/move",{"game":g["game"],"move":choose(g["fen"],g["legal_moves"])})