"""Contact sheet of the UI icons (assets/tex) on the panel background: 96 / 48 / 24 / 18 px and a tab bar mock-up.  icon_sheet.py <out.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont
T=__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "assets", "tex") + "/"
names=[("cam","Free cam (alt)"),("photo","Photo (alt)"),("tab_clothes","Clothes"),("tab_outfits","Outfits"),("tab_looks","Looks"),("tab_bag","Backpack"),("tab_hair","Coiffure"),("pose","Poses"),("tab_weapons","Weapons"),("tab_look","Appearance"),("tab_body","Body Shape"),("tab_face","Face"),("tab_mods","Mods"),("tab_options","Options"),("tab_manage","Manage"),("altui","AltUI")]
bg=(38,38,44); col=(220,228,255)
font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf",14)
W=max(len(names)*110+20,1500); im=Image.new("RGB",(W,330),bg); d=ImageDraw.Draw(im)
def paste(n,x,y,s,c=col):
    g=Image.open(T+n+".png").convert("RGBA").resize((s,s),Image.LANCZOS)
    a=g.split()[3]; tint=Image.new("RGB",(s,s),c); im.paste(tint,(x,y),a)
for i,(n,l) in enumerate(names):
    x=20+i*110
    paste(n,x+5,10,96)
    paste(n,x+30,120,48)
    paste(n,x+42,185,24)
    paste(n,x+45,225,18,(255,255,255))
    d.text((x,260),l,fill=(230,230,230),font=font)
# tab bar mockup
y=290; x=20
for n,l in names[2:15]:
    paste(n,x,y,20,(255,255,255)); d.text((x+24,y+2),l,fill=(255,255,255),font=font); x+=int(24+d.textlength(l,font=font)+18)
im.save(sys.argv[1])
