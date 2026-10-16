# Survey: which pose montages of the installed pose mods loop (section chain back to itself), repeat for a while (segment LoopingCount > 1) or play once.
# Usage: python3 scripts/pose_loop_survey.py <workdir with posemods.txt = one pak path per line>; up to 15 montages per mod. 2026-10-16.
import subprocess, json, sys, os, re, shutil
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S=sys.argv[1]   # the repo (scripts/..)
mods=[l.strip() for l in open(S+"/posemods.txt") if l.strip()]
tot={"loop":0,"long":0,"once":0,"?":0}; lens=[]; per=[]
for m in mods:
    lst=subprocess.run(["python3",W+"/scripts/pak11_extract.py",m,"list"],capture_output=True,text=True).stdout.split()
    mons=sorted({p[:-7] for p in lst if p.endswith("_Montage.uasset")})
    if not mons: continue
    step=max(1,len(mons)//15); sample=mons[::step][:15]
    out=S+"/poses/x"; shutil.rmtree(out, ignore_errors=True)
    rx="|".join(re.escape(p)+r"\.u" for p in sample)
    subprocess.run(["python3",W+"/scripts/pak11_extract.py",m,out,rx],capture_output=True)
    c={"loop":0,"long":0,"once":0,"?":0}; ends=[]
    for p in sample:
        f=out+p+".uasset"
        try:
            d=json.loads(subprocess.run(["python3",W+"/scripts/uasset_props.py",f],capture_output=True,text=True).stdout)
            s=json.dumps(d); i=s.find('"CompositeSections"')
            secs=re.findall(r'"SectionName": "([^"]*)", "NextSectionName": "([^"]*)"', s[i:i+20000])
            nxt=dict(secs)
            if not secs: c["?"]+=1; continue
            cur=secs[0][0]; seen=set(); loop=False
            while cur and cur!="None":
                if cur in seen: loop=True; break
                seen.add(cur); cur=nxt.get(cur)
            lc=[int(x) for x in re.findall(r'"LoopingCount": (\d+)', s)]; L=float((re.findall(r'"SequenceLength": ([0-9.]+)', s) or ["0"])[-1])
            if loop: c["loop"]+=1
            elif max(lc or [1])>1: c["long"]+=1; lens.append(L)
            else: c["once"]+=1; ends.append("%s %.1fs" % (os.path.basename(p), L))
        except Exception as e:
            c["?"]+=1
    shutil.rmtree(out, ignore_errors=True)
    for k in c: tot[k]+=c[k]
    per.append((os.path.basename(m), len(mons), c, ends[:4]))
for row in per: print(row)
print("TOTAL", tot); import statistics
if lens: print("long: min %.0fs median %.0fs max %.0fs" % (min(lens), statistics.median(lens), max(lens)))
