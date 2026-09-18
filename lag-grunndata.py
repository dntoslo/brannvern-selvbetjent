#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lager grunndata.js til mobilskjemaet ut fra data.js i Brannvern og vedlikehold.

Kjor:  python lag-grunndata.py "C:\\sti\\til\\data.js"  [ut-mappe]

Skriver grunndata.js og bumper cacheversjonen i sw.js, slik at telefonene
henter ny utgave neste gang de er pa nett.
"""
import json
import os
import re
import sys
from datetime import date

HER = os.path.dirname(os.path.abspath(__file__))


def les_data(sti):
    with open(sti, encoding="utf-8") as f:
        s = f.read()
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


def levende(rad):
    return not rad.get("fjernet")


def bygg_grunndata(d):
    hytter = []
    bygg_per_hytte = {}
    for b in d["bygg"]:
        if not levende(b):
            continue
        bygg_per_hytte.setdefault(b["hytteId"], []).append(b)

    utstyr_per_bygg = {}
    for u in d["utstyr"]:
        if not levende(u):
            continue
        utstyr_per_bygg.setdefault(u["byggId"], []).append(u)

    # siste feiing per bygg, og per hytte for kontroller pa hele anlegget
    feiing_bygg, feiing_hytte = {}, {}
    for k in d["kontroller"]:
        if not levende(k) or not k.get("dato"):
            continue
        if k.get("type") == "feiing" or k.get("feiing"):
            if k.get("byggId"):
                if k["dato"] > feiing_bygg.get(k["byggId"], ""):
                    feiing_bygg[k["byggId"]] = k["dato"]
            if k.get("hytteId"):
                if k["dato"] > feiing_hytte.get(k["hytteId"], ""):
                    feiing_hytte[k["hytteId"]] = k["dato"]

    for h in sorted(d["hytter"], key=lambda x: x["navn"].lower()):
        if not levende(h):
            continue
        bygger = []
        for b in sorted(bygg_per_hytte.get(h["hytteId"], []), key=lambda x: x["navn"].lower()):
            utstyr = []
            for u in utstyr_per_bygg.get(b["byggId"], []):
                utstyr.append({
                    "utstyrId": u["utstyrId"],
                    "type": u["type"],
                    "montertAar": u.get("montertAar"),
                    "levetidAar": u.get("levetidAar"),
                    "antall": u.get("antall"),
                })
            bygger.append({
                "byggId": b["byggId"],
                "navn": b["navn"],
                "beskrivelse": b.get("beskrivelse"),
                "ildsted": bool(b.get("ildsted")),
                "gass": bool(b.get("gass")),
                "harBrannutstyr": bool(b.get("harBrannutstyr")),
                "varslingstype": b.get("varslingstype"),
                "batteritype": b.get("batteritype"),
                "sistFeid": feiing_bygg.get(b["byggId"]) or feiing_hytte.get(h["hytteId"]),
                "utstyr": utstyr,
            })
        hytter.append({
            "hytteId": h["hytteId"],
            "navn": h["navn"],
            "omraade": h.get("omraade"),
            "bygg": bygger,
        })
    return {
        "grunndataVersjon": d.get("versjon"),
        "laget": date.today().isoformat(),
        "hytter": hytter,
    }


def skriv(g, utmappe):
    sti = os.path.join(utmappe, "grunndata.js")
    with open(sti, "w", encoding="utf-8") as f:
        f.write("window.GRUNNDATA = ")
        json.dump(g, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    return sti


def bump_sw(utmappe):
    sti = os.path.join(utmappe, "sw.js")
    if not os.path.exists(sti):
        return None
    s = open(sti, encoding="utf-8").read()
    m = re.search(r'const CACHE = "internkontroll-v(\d+)"', s)
    if not m:
        return None
    ny = int(m.group(1)) + 1
    s = s[:m.start()] + 'const CACHE = "internkontroll-v%d"' % ny + s[m.end():]
    open(sti, "w", encoding="utf-8").write(s)
    return ny


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    utmappe = sys.argv[2] if len(sys.argv) > 2 else HER
    d = les_data(sys.argv[1])
    g = bygg_grunndata(d)
    sti = skriv(g, utmappe)
    ant_bygg = sum(len(h["bygg"]) for h in g["hytter"])
    print("Skrev %s" % sti)
    print("  %d hytter, %d bygg, datafil versjon %s" %
          (len(g["hytter"]), ant_bygg, g["grunndataVersjon"]))
    ny = bump_sw(utmappe)
    if ny:
        print("  sw.js satt til internkontroll-v%d" % ny)
    print("Last opp grunndata.js og sw.js til nettsiden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
