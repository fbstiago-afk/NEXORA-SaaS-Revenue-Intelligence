# -*- coding: utf-8 -*-
"""Monta o PBIP NEXORA: python build_pbip.py <saida_NEXORA> <assets> <pasta_dados_windows>"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from pbip_model import write_model
from pbip_report import write_report
out, assets, pasta = sys.argv[1], sys.argv[2], sys.argv[3]
tabs = write_model(os.path.join(out, "Nexora.SemanticModel"), pasta)
np_, nv, nb = write_report(os.path.join(out, "Nexora.Report"), assets, base_theme_file=True)
from pbip_measures import MEASURES
print(f"tabelas={len(tabs)} medidas={len(MEASURES)} paginas={np_} visuais={nv} bookmarks={nb}")
