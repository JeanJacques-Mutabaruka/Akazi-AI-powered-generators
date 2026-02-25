"""
DIAGNOSTIC AKAZI — HF Preset Engine
=====================================
Exécuter depuis le dossier racine du projet :
    python DIAGNOSTIC_RUN_ME.py

Ce script teste chaque étape du pipeline HF preset et affiche
exactement où ça plante, avec le traceback complet.
"""

import sys, traceback, yaml
from pathlib import Path

# ── Adapter ces chemins à ta machine ──────────────────────────────────────
PROJECT_ROOT   = Path(__file__).parent
PRESET_PATH    = PROJECT_ROOT / "hf_presets" / "combined" / "Akazi_header_Footer_01.yaml"
# Si le fichier s'appelle différemment, change ci-dessus

RESULTS = []

def ok(step, msg=""): 
    RESULTS.append(("✅", step, msg))
    print(f"  ✅ {step}" + (f" — {msg}" if msg else ""))

def fail(step, err, tb=""):
    RESULTS.append(("❌", step, err))
    print(f"  ❌ {step}")
    print(f"     ERREUR : {err}")
    if tb: print(f"     TRACEBACK :\n{tb}")

print("=" * 60)
print("DIAGNOSTIC AKAZI HF PRESET ENGINE")
print("=" * 60)

# ── ÉTAPE 1 : Trouver le preset ───────────────────────────────────────────
print("\n[1] Recherche du preset YAML")
preset_file = None
for p in PROJECT_ROOT.rglob("*.yaml"):
    if "Akazi_header_Footer" in p.name or "akazi_header" in p.name.lower():
        print(f"  Trouvé : {p}")
        preset_file = p
        break
if not PRESET_PATH.exists():
    if preset_file:
        ok("Preset trouvé (chemin alternatif)", str(preset_file))
    else:
        fail("Preset YAML", f"Fichier introuvable : {PRESET_PATH}")
        print("\n  Fichiers YAML disponibles :")
        for p in PROJECT_ROOT.rglob("*.yaml"):
            print(f"    {p}")
        sys.exit(1)
else:
    ok("Preset trouvé", str(PRESET_PATH))
    preset_file = PRESET_PATH

# ── ÉTAPE 2 : Charger le YAML ─────────────────────────────────────────────
print("\n[2] Chargement du YAML")
try:
    with open(preset_file, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    ok("YAML chargé")
    print(f"  Clés racine : {list(cfg.keys())}")
    for section in ['header', 'footer']:
        if section in cfg:
            print(f"  {section} keys : {list(cfg[section].keys())}")
            for key in ['_col_widths', '_top_line', '_bottom_line', '_distance_cm']:
                val = cfg[section].get(key)
                status = "✅" if val is not None else "⚠️  absent"
                print(f"    {key} : {status} {val if val is not None else ''}")
except Exception as e:
    fail("Chargement YAML", str(e), traceback.format_exc())
    sys.exit(1)

# ── ÉTAPE 3 : Import docx_header_engine ──────────────────────────────────
print("\n[3] Import docx_header_engine")
try:
    import docx_header_engine
    import os
    pkg_path = os.path.dirname(docx_header_engine.__file__)
    ok("Package importé", pkg_path)
    
    # Vérifier les sous-modules
    for submod in ['engine', 'config.parser', 'zone_manager', 'section_manager']:
        mod_path = pkg_path
        for part in submod.split('.'):
            mod_path = os.path.join(mod_path, part + '.py' if '.' not in part else part)
        # Check file exists
        actual = os.path.join(pkg_path, submod.replace('.', '/') + '.py')
        if os.path.exists(actual):
            print(f"  ✅ {submod}.py trouvé")
        else:
            print(f"  ⚠️  {submod}.py introuvable à {actual}")
except ImportError as e:
    fail("Import docx_header_engine", str(e))
    sys.exit(1)

# ── ÉTAPE 4 : Tester ConfigParser ────────────────────────────────────────
print("\n[4] Test ConfigParser.parse()")
try:
    from docx_header_engine.config.parser import ConfigParser
    # Vérifier que SPECIAL_KEYS contient les bonnes clés
    sk = getattr(ConfigParser, 'SPECIAL_KEYS', set())
    print(f"  SPECIAL_KEYS : {sk}")
    for key in ['_col_widths', '_top_line', '_bottom_line', '_distance_cm']:
        if key in sk:
            print(f"    ✅ {key}")
        else:
            print(f"    ❌ {key} MANQUANT — v2 non déployée !")
    
    # Test parse réel
    cfg_test = yaml.safe_load(open(preset_file, encoding='utf-8').read())
    parsed = ConfigParser.parse(cfg_test)
    print(f"  Parsed keys : {list(parsed.keys())}")
    for section in ['header', 'footer']:
        if section in parsed:
            print(f"  {section} parsed keys : {list(parsed[section].keys())}")
            for key in ['_col_widths', '_top_line']:
                val = parsed[section].get(key)
                if val is not None:
                    print(f"    ✅ {key} = {val}")
                else:
                    print(f"    ❌ {key} ABSENT après parsing !")
    ok("ConfigParser.parse() exécuté")
except Exception as e:
    fail("ConfigParser", str(e), traceback.format_exc())

# ── ÉTAPE 5 : Tester engine.apply_yaml() complet ─────────────────────────
print("\n[5] Test engine.apply_yaml() complet")
try:
    from docx import Document
    from docx_header_engine.engine import HeaderFooterEngine
    
    doc = Document()
    doc.add_paragraph("Test content")
    engine = HeaderFooterEngine(doc)
    engine.apply_yaml(str(preset_file))
    
    # Vérifier le résultat
    footer = doc.sections[0].footer
    import lxml.etree as etree
    footer_xml = etree.tostring(footer._element, pretty_print=True).decode()
    
    has_pBdr  = 'pBdr' in footer_xml
    has_red   = 'C00000' in footer_xml.upper()
    has_table = '<w:tbl' in footer_xml
    
    if has_pBdr:  print("  ✅ _top_line (pBdr) présente dans le footer XML")
    else:         print("  ❌ _top_line ABSENTE — zone_manager v3 non déployé ?")
    if has_red:   print("  ✅ Couleur C00000 présente")
    else:         print("  ⚠️  Couleur C00000 absente")
    if has_table: print("  ✅ Tableau 3 colonnes présent")
    else:         print("  ❌ Tableau absent — zone_manager cassé ?")
    
    doc.save("test_engine_output.docx")
    ok("engine.apply_yaml() OK", "test_engine_output.docx généré")
    print("\n  → Ouvrir test_engine_output.docx pour vérifier visuellement")

except Exception as e:
    fail("engine.apply_yaml()", str(e), traceback.format_exc())

# ── RÉCAP ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RÉSUMÉ")
print("=" * 60)
for status, step, msg in RESULTS:
    print(f"  {status} {step}" + (f" : {msg}" if msg else ""))

n_fail = sum(1 for s,_,_ in RESULTS if s == "❌")
if n_fail == 0:
    print("\n✅ Tout fonctionne — si le Word n'a toujours pas le bon HF,")
    print("   le problème est dans base_generator._apply_header_footer()")
    print("   → Ajoute print(str(e)) dans le except pour voir l'erreur exacte")
else:
    print(f"\n❌ {n_fail} problème(s) détecté(s) — corriger dans l'ordre ci-dessus")

