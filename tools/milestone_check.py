#!/usr/bin/env python3
"""Milestone checker (locked). Verifies story milestones. Exit 1 on any violation."""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOVEL = ROOT / "novels" / "the-thirteenth-knight-holds-every-sword"
CH = NOVEL / "chapters"

def read_ch(n):
    p = CH / f"chapter-{n:03d}.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def check_mother_truth():
    phrases = ["Aiwa", "the mind of the planet", "she stopped reading me", "Myrrhen through Clara", "I am her eldest"]
    for n in range(1, 400):
        t = read_ch(n)
        for ph in phrases:
            if ph.lower() in t.lower():
                return f"FAIL: mother truth phrase '{ph}' found in ch {n} (before 400)"
    return "OK: mother truth not revealed before ch 400"

def check_confession():
    phrases = ["I love you", "I love Lysette", "confession", "I have loved you"]
    for n in range(1, 500):
        t = read_ch(n)
        for ph in phrases:
            if ph.lower() in t.lower():
                return f"FAIL: confession phrase '{ph}' found in ch {n} (before 500)"
    return "OK: confession not before ch 500"

def check_lewd():
    banned = ["sex", "naked", "breast", "moan", "ecchi", "harem", "seduce", "lust", "arousal"]
    for n in range(1, 51):
        t = read_ch(n).lower()
        for w in banned:
            if w in t:
                return f"FAIL: lewd term '{w}' found in ch {n}"
    return "OK: no lewd content in arc 1"

def check_armor_labels():
    for n in range(1, 51):
        t = read_ch(n)
        battle_kw = ["fight", "battle", "duel", "clash", "attack", "lance", "sword", "armor"]
        if any(kw in t.lower() for kw in battle_kw):
            if "**[" not in t and "armor" not in t.lower():
                return f"FAIL: ch {n} has battle but no armor label"
    return "OK: armor labels present in battle chapters"

def check_weapon_labels():
    for n in range(1, 51):
        t = read_ch(n)
        battle_kw = ["fight", "battle", "duel", "clash", "attack", "lance", "sword"]
        if any(kw in t.lower() for kw in battle_kw):
            if "**[" not in t:
                return f"FAIL: ch {n} has battle but no weapon label"
    return "OK: weapon labels present in battle chapters"

def main():
    checks = [check_mother_truth, check_confession, check_lewd, check_armor_labels, check_weapon_labels]
    failed = False
    for c in checks:
        r = c()
        print(r)
        if r.startswith("FAIL"):
            failed = True
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
