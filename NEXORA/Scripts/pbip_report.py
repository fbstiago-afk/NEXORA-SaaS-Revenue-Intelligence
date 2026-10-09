# -*- coding: utf-8 -*-
"""Gera o relatório PBIR do NEXORA (páginas, visuais, bookmarks, tema, recursos)."""
import os, json, hashlib, shutil

VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
BM_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/1.4.0/schema.json"
HTMLV = "htmlContent443BE3AD55E043BF878BED274D3A6855"
DENEB = "deneb7E15AEF80B9E4D4F8E12924291ECE89A"
MED = "_Medidas"

C = dict(navy="#08152F", deep="#050D20", cyan="#00B8F5", blue="#1678FF", violet="#6736F5", teal="#00D7C0",
         red="#FF607A", white="#FFFFFF", sec="#A9BBD8", grid="#1E3462", panel="#0C1C40", amber="#F5A524")


def hid(*k):
    return hashlib.md5("|".join(map(str, k)).encode()).hexdigest()[:20]


def L(v):
    return {"expr": {"Literal": {"Value": v}}}


def Ls(s):
    return L("'" + str(s).replace("'", "''") + "'")


def Lb(b):
    return L("true" if b else "false")


def Ld(n):
    return L(f"{n}D")


def Ll(n):
    return L(f"{n}L")


def col(c):
    return {"solid": {"color": Ls(c)}}


def colm(measure):
    return {"solid": {"color": {"expr": {"Measure": {"Expression": {"SourceRef": {"Entity": MED}}, "Property": measure}}}}}


def fM(name):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": MED}}, "Property": name}}


def fC(t, c):
    return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}


def proj_m(name, disp=None):
    p = {"field": fM(name), "queryRef": f"{MED}.{name}", "nativeQueryRef": name}
    if disp:
        p["displayName"] = disp
    return p


def proj_c(t, c, disp=None, active=True):
    p = {"field": fC(t, c), "queryRef": f"{t}.{c}", "nativeQueryRef": c}
    if active:
        p["active"] = True
    if disp:
        p["displayName"] = disp
    return p


def props(**kw):
    return [{"properties": kw}]


def vco(title=None, tooltip_page=None, bg=False, pad=0, title_size=13, link=None, align="center"):
    o = {
        "background": props(show=Lb(bg)) if not bg else props(show=Lb(True), color=col(C["panel"]), transparency=Ld(100)),
        "border": props(show=Lb(False)),
        "dropShadow": props(show=Lb(False)),
        "visualHeader": props(show=Lb(False)),
        "padding": props(top=Ld(pad), bottom=Ld(pad), left=Ld(pad), right=Ld(pad)),
        "title": props(show=Lb(False)) if not title else props(
            show=Lb(True), text=Ls(title), alignment=Ls(align), fontColor=col(C["white"]), fontSize=Ld(title_size),
            fontFamily=Ls("Segoe UI Semibold"), titleWrap=Lb(True)),
        "subTitle": props(show=Lb(False)),
    }
    if tooltip_page:
        o["visualTooltip"] = props(show=Lb(True), type=Ls("Canvas"), section=Ls(tooltip_page))
    if link:
        o["visualLink"] = link
    return o


def container(page, key, x, y, w, h, z, visual, hidden=False, extra=None):
    name = hid(page, key)
    v = {"$schema": VC_SCHEMA, "name": name,
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}, "visual": visual}
    if hidden:
        v["isHidden"] = True
    if extra:
        v.update(extra)
    return name, v


# ---------------------------------------------------------------- componentes
def html_visual(measure, title=None, tooltip_page=None):
    return {"visualType": HTMLV,
            "query": {"queryState": {"content": {"projections": [proj_m(measure)]}}},
            "objects": {"contentFormatting": props(showRawHtml=Lb(False), fontFamily=Ls("Segoe UI"), fontColour=col(C["white"]))},
            "visualContainerObjects": vco(title, tooltip_page), "drillFilterOtherVisuals": True}


def button(text, link, fill=C["blue"], fill_tr=0, hover=C["violet"], radius=12, size=11, outline=None, show_text=True,
           tooltip=None, transparent=False):
    t_def = dict(text=Ls(text), fontColor=col(C["white"]), fontSize=Ld(size), fontFamily=Ls("Segoe UI Semibold"),
                 horizontalAlignment=Ls("center"), verticalAlignment=Ls("middle"))
    lk = dict(link)
    if tooltip:
        lk["tooltip"] = Ls(tooltip)
    objs = {
        "icon": props(show=Lb(False)),
        "text": [{"properties": {"show": Lb(show_text)}}, {"properties": t_def, "selector": {"id": "default"}},
                 {"properties": t_def, "selector": {"id": "hover"}}],
        "fill": [{"properties": {"show": Lb(True)}},
                 {"properties": {"fillColor": col(fill), "transparency": Ld(100 if transparent else fill_tr)}, "selector": {"id": "default"}},
                 {"properties": {"fillColor": col(hover if not transparent else "#FFFFFF"), "transparency": Ld(88 if transparent else 0)}, "selector": {"id": "hover"}},
                 {"properties": {"fillColor": col(hover if not transparent else "#FFFFFF"), "transparency": Ld(82 if transparent else 0)}, "selector": {"id": "press"}}],
        "outline": [{"properties": {"show": Lb(outline is not None)}},
                    {"properties": {"lineColor": col(outline or C["cyan"]), "weight": Ld(1), "transparency": Ld(30)}, "selector": {"id": "default"}}],
        "shape": props(tileShape=Ls("rectangleRounded"), rectangleRoundedCurve=Ll(radius)),
    }
    return {"visualType": "actionButton", "objects": objs,
            "visualContainerObjects": vco(link=[{"properties": dict(show=Lb(True), **lk)}]), "drillFilterOtherVisuals": True}


def nav_link(page):
    return {"type": Ls("PageNavigation"), "navigationSection": Ls(page)}


def bm_link(bm):
    return {"type": Ls("Bookmark"), "bookmark": Ls(bm)}


def clear_link():
    return {"type": Ls("ClearAllSlicers")}


def shape_panel(color=C["deep"], tr=0, border=C["cyan"], radius=22):
    return {"visualType": "shape",
            "objects": {"shape": props(tileShape=Ls("rectangleRounded"), rectangleRoundedCurve=Ll(radius)),
                        "fill": props(show=Lb(False)), "outline": props(show=Lb(False))},
            "visualContainerObjects": {
                "background": props(show=Lb(True), color=col(color), transparency=Ld(tr)),
                "border": props(show=Lb(True), color=col(border), radius=Ld(radius), width=Ld(1)),
                "dropShadow": props(show=Lb(True), color=col("#000000"), transparency=Ld(40), shadowBlur=Ld(30),
                                    shadowDistance=Ld(0), angle=Ld(0), shadowSpread=Ld(4), preset=Ls("Custom"), position=Ls("Outer")),
                "visualHeader": props(show=Lb(False)), "title": props(show=Lb(False))},
            "drillFilterOtherVisuals": True}


def textbox(runs):
    return {"visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": runs}}]},
            "visualContainerObjects": {"background": props(show=Lb(False)), "border": props(show=Lb(False)),
                                       "visualHeader": props(show=Lb(False)), "title": props(show=Lb(False)),
                                       "dropShadow": props(show=Lb(False))},
            "drillFilterOtherVisuals": True}


def slicer(t, c, header, group):
    return {"visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [proj_c(t, c)]}}},
            "objects": {
                "data": props(mode=Ls("Dropdown")),
                "header": props(show=Lb(True), text=Ls(header), fontColor=col(C["sec"]), textSize=Ld(10),
                                fontFamily=Ls("Segoe UI Semibold"), background=col(C["panel"])),
                "items": props(fontColor=col(C["white"]), background=col(C["panel"]), textSize=Ld(11), fontFamily=Ls("Segoe UI")),
                "selection": props(singleSelect=Lb(False), selectAllCheckboxEnabled=Lb(True), strictSingleSelect=Lb(False))},
            "visualContainerObjects": {
                "background": props(show=Lb(True), color=col(C["panel"]), transparency=Ld(0)),
                "border": props(show=Lb(True), color=col("#22407A"), radius=Ld(10), width=Ld(1)),
                "dropShadow": props(show=Lb(False)), "visualHeader": props(show=Lb(False)), "title": props(show=Lb(False)),
                "padding": props(top=Ld(4), bottom=Ld(4), left=Ld(8), right=Ld(8))},
            "syncGroup": {"groupName": group, "fieldChanges": True, "filterChanges": True},
            "drillFilterOtherVisuals": True}


# ---------------------------------------------------------------- eixos/gráficos nativos
def axis_objs(value_axis=True, sec=False, value_fmt=None, labels=False, legend=False, cat_font=10):
    o = {
        "categoryAxis": props(show=Lb(True), labelColor=col(C["sec"]), fontSize=Ld(cat_font), fontFamily=Ls("Segoe UI"),
                              showAxisTitle=Lb(False), gridlineShow=Lb(False), axisType=Ls("Categorical"), concatenateLabels=Lb(False)),
        "valueAxis": props(show=Lb(value_axis), labelColor=col(C["sec"]), fontSize=Ld(10), fontFamily=Ls("Segoe UI"),
                           showAxisTitle=Lb(False), gridlineShow=Lb(value_axis), gridlineColor=col(C["grid"]),
                           gridlineStyle=Ls("dotted"), **({"secShow": Lb(True), "secLabelColor": col(C["sec"]),
                                                            "secFontSize": Ld(10), "secShowAxisTitle": Lb(False)} if sec else {})),
        "legend": props(show=Lb(legend), position=Ls("TopCenter"), labelColor=col(C["sec"]), fontSize=Ld(10), showTitle=Lb(False)),
        "labels": props(show=Lb(labels), color=col(C["white"]), fontSize=Ld(10), fontFamily=Ls("Segoe UI Semibold"),
                        labelDisplayUnits=Ld(0) if not value_fmt else Ld(value_fmt)),
    }
    return o


def fx_datapoint(measure, metadata=None):
    sel = {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}
    if metadata:
        sel["metadata"] = metadata
    return [{"properties": {"fill": colm(measure)}, "selector": sel}]


# ---------------------------------------------------------------- Deneb
DENEB_CFG = {
    "autosize": {"type": "fit", "contains": "padding"},
    "background": None,
    "view": {"stroke": "transparent"},
    "font": "Segoe UI",
    "padding": {"left": 6, "right": 10, "top": 10, "bottom": 6},
    "axis": {"labelColor": "#A9BBD8", "gridColor": "#1E3462", "domainColor": "#1E3462", "tickColor": "#1E3462",
             "titleColor": "#A9BBD8", "labelFont": "Segoe UI", "labelFontSize": 11, "gridDash": [3, 3]},
    "legend": {"labelColor": "#A9BBD8", "titleColor": "#A9BBD8", "labelFont": "Segoe UI", "titleFont": "Segoe UI"},
    "text": {"color": "#FFFFFF", "font": "Segoe UI"},
}


def deneb_visual(projs, spec, title, tooltip_page=None):
    s = json.dumps(spec, ensure_ascii=False, indent=2)
    cfg = json.dumps({k: v for k, v in DENEB_CFG.items() if v is not None}, ensure_ascii=False, indent=2)
    return {"visualType": DENEB,
            "query": {"queryState": {"dataset": {"projections": projs}}},
            "objects": {"vega": [{"properties": {
                "provider": Ls("vegaLite"), "jsonSpec": Ls(s), "jsonConfig": Ls(cfg), "renderMode": Ls("svg"),
                "enableTooltips": Lb(True), "enableContextMenu": Lb(True), "enableSelection": Lb(False),
                "enableHighlight": Lb(False), "isNewDialogOpen": Lb(False)}}]},
            "visualContainerObjects": vco(title, tooltip_page),
            "drillFilterOtherVisuals": True}


SPEC_WATERFALL = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [
        {"filter": "datum.tipo != 'migr' || abs(datum.valor) >= 1"},
        {"window": [{"op": "sum", "field": "valor", "as": "acum"}], "sort": [{"field": "ordem"}]},
        {"calculate": "(datum.tipo == 'fim' || datum.tipo == 'inicio') ? 0 : datum.acum - datum.valor", "as": "y0"},
        {"calculate": "datum.tipo == 'fim' ? datum.valor : datum.acum", "as": "y1"},
        {"window": [{"op": "lead", "field": "etapa", "as": "prox"}], "sort": [{"field": "ordem"}]},
        {"calculate": "max(datum.y0, datum.y1)", "as": "topo"}],
    "encoding": {"x": {"field": "etapa", "type": "nominal", "sort": {"field": "ordem", "op": "min"},
                       "axis": {"title": None, "labelAngle": 0, "labelFontSize": 12.5, "labelColor": "#DCE6F7",
                                "labelFontWeight": 600, "domain": False, "ticks": False, "labelPadding": 12}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadius": 7, "width": {"band": 0.62}},
         "encoding": {"y": {"field": "y0", "type": "quantitative", "axis": None, "scale": {"zero": True, "nice": True}},
                      "y2": {"field": "y1"},
                      "color": {"field": "tipo", "type": "nominal", "legend": None,
                                "scale": {"domain": ["inicio", "ganho", "migr", "perda", "fim"],
                                          "range": ["#1678FF", "#00D7C0", "#6E86B3", "#FF607A", "#6736F5"]}},
                      "tooltip": [{"field": "etapa", "title": "Etapa"}, {"field": "rotulo", "title": "Valor"}]}},
        {"transform": [{"filter": "datum.prox != null"}],
         "mark": {"type": "rule", "color": "#A9BBD8", "opacity": 0.6, "strokeDash": [4, 3], "strokeWidth": 1.4,
                  "xOffset": {"expr": "bandwidth('x') * 0.31"}, "x2Offset": {"expr": "-bandwidth('x') * 0.31"}},
         "encoding": {"x2": {"field": "prox"}, "y": {"field": "y1", "type": "quantitative"}}},
        {"mark": {"type": "text", "dy": -11, "fontSize": 13.5, "fontWeight": 700, "color": "#FFFFFF"},
         "encoding": {"y": {"field": "topo", "type": "quantitative"}, "text": {"field": "rotulo"}}}],
}

SPEC_PLANO = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [{"joinaggregate": [{"op": "max", "field": "mrr", "as": "mx"}]},
                  {"calculate": "datum.mrr / datum.mx * 0.62", "as": "f"}, {"calculate": "0.62", "as": "trilho"}],
    "encoding": {"y": {"field": "plano", "type": "nominal", "sort": {"field": "ordem", "op": "min"},
                       "axis": {"title": None, "labelFontSize": 13.5, "labelColor": "#FFFFFF", "labelFontWeight": 600,
                                "domain": False, "ticks": False, "labelPadding": 12}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadius": 8, "height": {"band": 0.5}, "color": "#1E3462", "opacity": 0.55},
         "encoding": {"x": {"field": "trilho", "type": "quantitative", "scale": {"domain": [0, 1]}, "axis": None}}},
        {"mark": {"type": "bar", "cornerRadius": 8, "height": {"band": 0.5}},
         "encoding": {"x": {"field": "f", "type": "quantitative"}, "color": {"field": "cor", "type": "nominal", "scale": None},
                      "tooltip": [{"field": "plano", "title": "Plano"}, {"field": "rotulo", "title": "MRR · participação"}]}},
        {"mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 13, "fontWeight": 700, "color": "#FFFFFF"},
         "encoding": {"x": {"field": "trilho", "type": "quantitative"}, "text": {"field": "rotulo"}}}],
}

SPEC_COHORT = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [{"filter": "isValid(datum.ret)"}, {"calculate": "'M' + datum.idade", "as": "m"}],
    "encoding": {"x": {"field": "idade", "type": "ordinal",
                       "axis": {"title": None, "orient": "top", "labelExpr": "'M' + datum.value", "labelColor": "#A9BBD8",
                                "domain": False, "ticks": False, "labelFontSize": 11, "labelFontWeight": 600, "labelAngle": 0}},
                 "y": {"field": "cohort", "type": "ordinal", "sort": {"field": "cidx", "op": "min"},
                       "axis": {"title": None, "labelColor": "#A9BBD8", "domain": False, "ticks": False, "labelFontSize": 10,
                                "labelPadding": 6}}},
    "layer": [
        {"mark": {"type": "rect", "cornerRadius": 3, "stroke": "#050D20", "strokeWidth": 1.5},
         "encoding": {"color": {"field": "ret", "type": "quantitative",
                                "scale": {"domain": [0.5, 0.72, 0.86, 1], "range": ["#FF607A", "#6736F5", "#1678FF", "#00D7C0"], "clamp": True},
                                "legend": {"orient": "bottom", "direction": "horizontal", "title": "Retenção de logos",
                                           "format": ".0%", "gradientLength": 320, "gradientThickness": 8, "titleFontSize": 11,
                                           "labelFontSize": 10}},
                      "tooltip": [{"field": "cohort", "title": "Cohort"}, {"field": "m", "title": "Idade"},
                                  {"field": "rot", "title": "Retenção"}, {"field": "base", "title": "Clientes iniciais"},
                                  {"field": "ativos", "title": "Ativos"}]}},
        {"mark": {"type": "text", "fontSize": 9.5, "fontWeight": 600, "color": "#FFFFFF"},
         "encoding": {"text": {"field": "rot"}}}],
}

SPEC_FUNIL = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [{"filter": "datum.valor > 0"},
                  {"calculate": "log(datum.valor)", "as": "lv"},
                  {"joinaggregate": [{"op": "max", "field": "lv", "as": "lmax"}, {"op": "min", "field": "lv", "as": "lmin"}]},
                  {"calculate": "0.30 + 0.70 * (datum.lv - datum.lmin) / (datum.lmax - datum.lmin)", "as": "w"},
                  {"calculate": "0.5 - datum.w / 2", "as": "x0"}, {"calculate": "0.5 + datum.w / 2", "as": "x1"},
                  {"calculate": "0.5", "as": "xc"}],
    "encoding": {"y": {"field": "etapa", "type": "nominal", "sort": {"field": "ordem", "op": "min"}, "axis": None,
                       "scale": {"paddingInner": 0.42, "paddingOuter": 0.15}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadius": 10},
         "encoding": {"x": {"field": "x0", "type": "quantitative", "scale": {"domain": [0, 1]}, "axis": None}, "x2": {"field": "x1"},
                      "color": {"field": "ordem", "type": "quantitative", "legend": None,
                                "scale": {"domain": [1, 6], "range": ["#00B8F5", "#6736F5"]}},
                      "tooltip": [{"field": "etapa", "title": "Etapa"}, {"field": "rotulo", "title": "Volume"},
                                  {"field": "conv", "title": "Conversão"}]}},
        {"mark": {"type": "text", "fontSize": 12, "fontWeight": 600, "color": "#DCE6F7", "dy": -10},
         "encoding": {"x": {"field": "xc", "type": "quantitative"}, "text": {"field": "etapa"}}},
        {"mark": {"type": "text", "fontSize": 17, "fontWeight": 700, "color": "#FFFFFF", "dy": 10},
         "encoding": {"x": {"field": "xc", "type": "quantitative"}, "text": {"field": "rotulo"}}},
        {"transform": [{"filter": "isValid(datum.conv) && datum.conv != ''"}],
         "mark": {"type": "text", "fontSize": 11, "fontWeight": 600, "color": "#00D7C0", "dy": {"expr": "-bandwidth('y') * 0.86"}},
         "encoding": {"x": {"field": "xc", "type": "quantitative"}, "text": {"field": "conv"}}}],
}

SPEC_CACLTV = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [{"filter": "datum.ltv > 0"},
                  {"joinaggregate": [{"op": "max", "field": "ltv", "as": "mx"}]},
                  {"calculate": "datum.ltv / datum.mx * 0.58", "as": "fl"}, {"calculate": "datum.cac / datum.mx * 0.58", "as": "fc"},
                  {"calculate": "0.58", "as": "trilho"}, {"calculate": "0.60", "as": "xr"}, {"calculate": "0.67", "as": "xt"},
                  {"calculate": "'LTV ' + datum.ltvTxt + '  ·  CAC ' + datum.cacTxt", "as": "det"}],
    "encoding": {"y": {"field": "canal", "type": "nominal", "sort": {"field": "ratio", "op": "max", "order": "descending"},
                       "axis": {"title": None, "labelFontSize": 12.5, "labelColor": "#FFFFFF", "labelFontWeight": 600,
                                "domain": False, "ticks": False, "labelPadding": 12}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadius": 6, "height": {"band": 0.62}, "color": "#1E3462", "opacity": 0.45},
         "encoding": {"x": {"field": "trilho", "type": "quantitative", "scale": {"domain": [0, 1]}, "axis": None}}},
        {"mark": {"type": "bar", "cornerRadius": 6, "height": {"band": 0.62}, "opacity": 0.92},
         "encoding": {"x": {"field": "fl", "type": "quantitative"}, "color": {"field": "cor", "type": "nominal", "scale": None},
                      "tooltip": [{"field": "canal", "title": "Canal"}, {"field": "ltvTxt", "title": "LTV estimado"},
                                  {"field": "cacTxt", "title": "CAC"}, {"field": "rotulo", "title": "LTV:CAC"}]}},
        {"mark": {"type": "bar", "cornerRadius": 3, "height": {"band": 0.2}, "color": "#FFFFFF", "opacity": 0.92},
         "encoding": {"x": {"field": "fc", "type": "quantitative"}}},
        {"mark": {"type": "text", "align": "left", "fontSize": 15, "fontWeight": 700},
         "encoding": {"x": {"field": "xr", "type": "quantitative"}, "text": {"field": "rotulo"},
                      "color": {"field": "cor", "type": "nominal", "scale": None}}},
        {"mark": {"type": "text", "align": "left", "fontSize": 11.5, "color": "#A9BBD8"},
         "encoding": {"x": {"field": "xt", "type": "quantitative"}, "text": {"field": "det"}}}],
}


# ---------------------------------------------------------------- tema
def theme():
    return {
        "name": "NEXORA Dark",
        "dataColors": ["#00B8F5", "#1678FF", "#6736F5", "#00D7C0", "#FF607A", "#F5A524", "#A9BBD8", "#6E86B3", "#8C6CFF", "#4FD8FF"],
        "background": "#050D20", "foreground": "#FFFFFF", "tableAccent": "#00B8F5",
        "good": "#00D7C0", "neutral": "#F5A524", "bad": "#FF607A", "maximum": "#00B8F5", "center": "#1678FF", "minimum": "#0C1C40",
        "textClasses": {
            "callout": {"fontSize": 28, "fontFace": "Segoe UI Semibold", "color": "#FFFFFF"},
            "title": {"fontSize": 13, "fontFace": "Segoe UI Semibold", "color": "#FFFFFF"},
            "header": {"fontSize": 11, "fontFace": "Segoe UI Semibold", "color": "#FFFFFF"},
            "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": "#A9BBD8"}},
        "visualStyles": {
            "*": {"*": {
                "background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}],
                "visualHeader": [{"show": False}],
                "title": [{"show": True, "alignment": "center", "fontColor": {"solid": {"color": "#FFFFFF"}}, "fontSize": 13,
                           "fontFamily": "Segoe UI Semibold"}],
                "visualTooltip": [{"titleFontColor": {"solid": {"color": "#FFFFFF"}}, "valueFontColor": {"solid": {"color": "#FFFFFF"}},
                                   "background": {"solid": {"color": "#08152F"}}, "fontSize": 10}],
                "categoryAxis": [{"labelColor": {"solid": {"color": "#A9BBD8"}}, "showAxisTitle": False}],
                "valueAxis": [{"labelColor": {"solid": {"color": "#A9BBD8"}}, "gridlineColor": {"solid": {"color": "#1E3462"}},
                               "showAxisTitle": False}],
                "legend": [{"labelColor": {"solid": {"color": "#A9BBD8"}}}]}},
            "page": {"*": {"outspace": [{"color": {"solid": {"color": "#050D20"}}, "transparency": 0}],
                           "background": [{"color": {"solid": {"color": "#050D20"}}, "transparency": 0}]}},
            "tableEx": {"*": {
                "columnHeaders": [{"alignment": "Center", "fontColor": {"solid": {"color": "#A9BBD8"}},
                                   "backColor": {"solid": {"color": "#0C1C40"}}, "fontFamily": "Segoe UI Semibold", "fontSize": 10}],
                "values": [{"fontColorPrimary": {"solid": {"color": "#FFFFFF"}}, "backColorPrimary": {"solid": {"color": "#08152F"}},
                            "fontColorSecondary": {"solid": {"color": "#FFFFFF"}}, "backColorSecondary": {"solid": {"color": "#0B1A3A"}},
                            "fontSize": 10}],
                "grid": [{"gridHorizontal": True, "gridHorizontalColor": {"solid": {"color": "#1E3462"}}, "gridVertical": False,
                          "outlineColor": {"solid": {"color": "#1E3462"}}, "rowPadding": 4}],
                "total": [{"fontColor": {"solid": {"color": "#FFFFFF"}}, "backColor": {"solid": {"color": "#0C1C40"}}}]}},
            "pivotTable": {"*": {
                "columnHeaders": [{"alignment": "Center", "fontColor": {"solid": {"color": "#A9BBD8"}},
                                   "backColor": {"solid": {"color": "#0C1C40"}}}],
                "values": [{"fontColorPrimary": {"solid": {"color": "#FFFFFF"}}, "backColorPrimary": {"solid": {"color": "#08152F"}}}]}},
            "slicer": {"*": {"items": [{"fontColor": {"solid": {"color": "#FFFFFF"}}, "background": {"solid": {"color": "#0C1C40"}}}],
                             "header": [{"fontColor": {"solid": {"color": "#A9BBD8"}}}]}},
        },
    }


# ---------------------------------------------------------------- páginas
PAGES = [("home", "Início"), ("executive", "Executive SaaS"), ("revenue", "Revenue Intelligence"),
         ("customer", "Customer & Retention"), ("growth", "Growth & Unit Economics")]
TT = [("ttMRR", "TT MRR", "HTML TT MRR"), ("ttClientes", "TT Clientes", "HTML TT Clientes"), ("ttCanal", "TT Canal", "HTML TT Canal")]
BG = {"home": "bg_home.png", "executive": "bg_exec.png", "revenue": "bg_revenue.png", "customer": "bg_customer.png", "growth": "bg_growth.png"}
NAV_Y0, NAV_H, NAV_GAP = 196, 60, 10
KX = [280, 688, 1096, 1504]
KY, KW, KH = 150, 386, 160


def page_json(name, disp, bg=None, w=1920, h=1080, tooltip=False):
    p = {"$schema": PAGE_SCHEMA, "name": name, "displayName": disp, "displayOption": "FitToPage", "height": h, "width": w}
    objs = {"outspace": props(color=col(C["deep"]), transparency=Ld(0))}
    if bg:
        objs["background"] = [{"properties": {"image": {"image": {
            "name": Ls(bg), "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": bg}}},
            "scaling": Ls("Fit")}}, "transparency": Ld(0)}}]
    else:
        objs["background"] = props(color=col(C["navy"]), transparency=Ld(0))
    p["objects"] = objs
    if tooltip:
        p["type"] = "Tooltip"
        p["pageBinding"] = {"name": "pb" + hid(name, "pb")[:16], "type": "Tooltip", "parameters": []}
        p["visibility"] = "HiddenInViewMode"
    return p


def chart_vco(title, tt=None):
    return vco(title, tt, pad=8, title_size=13)


def build_pages():
    pages = {}  # name -> (page_json, [visuals])
    bookmarks = []
    # ------------------------------------------------ HOME
    vis = []
    vis.append(container("home", "iniciar", 505, 660, 452, 94, 1000,
                         button("", nav_link("executive"), transparent=True, radius=47, show_text=False,
                                tooltip="Iniciar dashboard · Executive SaaS")))
    pages["home"] = (page_json("home", "Início", BG["home"]), vis)

    for pi, (pg, disp) in enumerate(PAGES[1:], start=1):
        vis = []
        z = 1000
        # navegação lateral (botões transparentes sobre o menu desenhado no background)
        for i, (target, _) in enumerate(PAGES):
            if target == pg:
                continue
            vis.append(container(pg, f"nav{i}", 26, NAV_Y0 + i * (NAV_H + NAV_GAP), 196, NAV_H, 30000 + i,
                                 button("", nav_link(target), transparent=True, radius=14, show_text=False, tooltip=f"Ir para {PAGES[i][1]}")))
        hdr = {"executive": "Executive", "revenue": "Revenue", "customer": "Customer", "growth": "Growth"}[pg]
        vis.append(container(pg, "header", 280, 20, 1080, 104, z, html_visual(f"HTML Header {hdr}")))
        vis.append(container(pg, "chips", 280, 118, 1300, 30, z + 1, html_visual("HTML Filtros Ativos")))
        # botões do cabeçalho
        bm_open, bm_close = hid(pg, "bm_open"), hid(pg, "bm_close")
        vis.append(container(pg, "btnFiltros", 1762, 44, 128, 42, z + 2,
                             button("⚙  Filtros", bm_link(bm_open), fill=C["blue"], hover=C["violet"], radius=21, tooltip="Abrir painel de filtros")))
        # cards
        cards = {"executive": ["HTML Card MRR", "HTML Card ARR", "HTML Card Clientes", "HTML Card NRR"],
                 "revenue": ["HTML Card New MRR", "HTML Card Expansion", "HTML Card Churned", "HTML Card Net New"],
                 "customer": ["HTML Card Clientes R", "HTML Card Logo Churn", "HTML Card NRR R", "HTML Card Risco"],
                 "growth": ["HTML Card CAC", "HTML Card LTV", "HTML Card LTV CAC", "HTML Card Payback"]}[pg]
        for i, m in enumerate(cards):
            vis.append(container(pg, f"card{i}", KX[i], KY, KW, KH, z + 10 + i, html_visual(m)))

        # gráficos
        if pg == "executive":
            q = {"Category": {"projections": [proj_c("dCalendario", "MesAno")]},
                 "Y": {"projections": [proj_m("Ending MRR", "MRR")]},
                 "Y2": {"projections": [proj_m("MRR MoM % Gráfico", "Crescimento mensal")]}}
            objs = axis_objs(value_axis=True, sec=True, legend=True)
            objs["dataPoint"] = fx_datapoint("Cor Coluna MRR") + [
                {"properties": {"fill": col(C["teal"])}, "selector": {"metadata": f"{MED}.MRR MoM % Gráfico"}}]
            objs["lineStyles"] = [{"properties": {"strokeWidth": Ld(2.5), "lineStyle": Ls("solid"), "showMarker": Lb(True),
                                                  "markerSize": Ld(4), "markerShape": Ls("circle")},
                                   "selector": {"metadata": f"{MED}.MRR MoM % Gráfico"}}]
            vis.append(container(pg, "chartMRR", 292, 344, 1038, 696, z + 20, {
                "visualType": "lineClusteredColumnComboChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fC("dCalendario", "MesAno"), "direction": "Ascending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Evolução do MRR  ·  colunas: MRR no fim do mês  ·  linha: crescimento mensal", "ttMRR"),
                "drillFilterOtherVisuals": True}))
            vis.append(container(pg, "denebPlano", 1378, 344, 500, 326, z + 21, deneb_visual(
                [proj_c("dPlano", "Plano", "plano"), proj_m("Ordem Plano", "ordem"), proj_m("Ending MRR", "mrr"),
                 proj_m("Cor Plano", "cor"), proj_m("Rótulo MRR Plano", "rotulo")], SPEC_PLANO, "MRR por Plano  ·  valor e participação")))
            q = {"Category": {"projections": [proj_c("dTipoMovimento", "Movimento")]},
                 "Y": {"projections": [proj_m("MRR Movimentado", "MRR")]}}
            objs = axis_objs(value_axis=False, labels=True, cat_font=11)
            objs["dataPoint"] = fx_datapoint("Cor Movimento")
            vis.append(container(pg, "chartCresc", 1378, 714, 500, 326, z + 22, {
                "visualType": "clusteredBarChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fC("dTipoMovimento", "Movimento"), "direction": "Ascending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Crescimento vs. Retenção  ·  ganhos e perdas de MRR no período"),
                "drillFilterOtherVisuals": True}, extra={"filterConfig": grupo_filter()}))
        elif pg == "revenue":
            vis.append(container(pg, "denebWF", 292, 344, 1038, 390, z + 20, deneb_visual(
                [proj_c("dEtapaWaterfall", "Etapa", "etapa"), proj_c("dEtapaWaterfall", "OrdemEtapa", "ordem"),
                 proj_c("dEtapaWaterfall", "TipoEtapa", "tipo"), proj_m("Valor Etapa Waterfall", "valor"),
                 proj_m("Rótulo Etapa Waterfall", "rotulo")], SPEC_WATERFALL,
                "MRR Waterfall  ·  MRR inicial + novo + expansão + reativação − contração − churn = MRR final")))
            q = {"Category": {"projections": [proj_c("dCalendario", "MesAno")]},
                 "Series": {"projections": [proj_c("dTipoMovimento", "Movimento")]},
                 "Y": {"projections": [proj_m("MRR Movimentado", "MRR")]}}
            objs = axis_objs(value_axis=True, legend=True, cat_font=9)
            objs["dataPoint"] = series_colors()
            vis.append(container(pg, "chartMov", 292, 776, 1038, 266, z + 21, {
                "visualType": "columnChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fC("dCalendario", "MesAno"), "direction": "Ascending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Evolução dos Movimentos de MRR  ·  ganhos acima, perdas abaixo de zero", "ttMRR"),
                "drillFilterOtherVisuals": True}, extra={"filterConfig": grupo_filter()}))
            q = {"Category": {"projections": [proj_c("dPlano", "Plano")]}, "Y": {"projections": [proj_m("Expansion MRR", "Expansion MRR")]}}
            objs = axis_objs(value_axis=False, labels=True, cat_font=12)
            objs["dataPoint"] = fx_datapoint("Cor Destaque Expansion")
            vis.append(container(pg, "chartExp", 1378, 344, 500, 326, z + 22, {
                "visualType": "clusteredBarChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fM("Expansion MRR"), "direction": "Descending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Expansion MRR por Plano  ·  destaque no maior contribuidor"),
                "drillFilterOtherVisuals": True}))
            vis.append(container(pg, "tblPlano", 1378, 714, 500, 326, z + 23, table_visual(
                [proj_c("dPlano", "Plano", "Plano", active=False), proj_m("Tbl Novo", "Novo"), proj_m("Tbl Expansão", "Expansão"),
                 proj_m("Tbl Contração", "Contração"), proj_m("Tbl Churn", "Churn"), proj_m("Tbl Net New", "Net New")],
                "Movimentação de MRR por Plano  ·  R$ mil", sort=("c", "dPlano", "Plano", "Ascending"))))
        elif pg == "customer":
            vis.append(container(pg, "denebCohort", 292, 344, 1038, 696, z + 20, deneb_visual(
                [proj_c("dCohort", "Cohort", "cohort"), proj_c("dCohort", "CohortIdx", "cidx"),
                 proj_c("fCohortMensal", "IdadeCohort", "idade"), proj_m("Cohort Retenção Heatmap", "ret"),
                 proj_m("Rótulo Cohort", "rot"), proj_m("Clientes Iniciais Cohort", "base"), proj_m("Clientes Ativos Cohort", "ativos")],
                SPEC_COHORT, "Cohort Retention  ·  % de clientes ativos por mês de aquisição (M0–M12)")))
            q = {"Category": {"projections": [proj_c("dCalendario", "AnoTrimestre")]},
                 "Y": {"projections": [proj_m("Clientes Cancelados", "Perdidos"), proj_m("Clientes Reativados", "Recuperados")]}}
            objs = axis_objs(value_axis=True, legend=True, cat_font=9)
            objs["dataPoint"] = [{"properties": {"fill": col(C["red"])}, "selector": {"metadata": f"{MED}.Clientes Cancelados"}},
                                 {"properties": {"fill": col(C["teal"])}, "selector": {"metadata": f"{MED}.Clientes Reativados"}}]
            vis.append(container(pg, "chartPerd", 1378, 344, 500, 326, z + 21, {
                "visualType": "clusteredColumnChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fC("dCalendario", "AnoTrimestre"), "direction": "Ascending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Clientes Perdidos e Recuperados por trimestre", "ttClientes"),
                "drillFilterOtherVisuals": True}))
            q = {"Category": {"projections": [proj_c("dFaixaHealth", "FaixaHealth")]},
                 "Y": {"projections": [proj_m("Clientes Monitorados", "Clientes")]},
                 "Tooltips": {"projections": [proj_m("% da Base (Health)", "% da base"), proj_m("Health Score Médio", "Health médio")]}}
            objs = axis_objs(value_axis=False, labels=True, cat_font=12)
            objs["dataPoint"] = fx_datapoint("Cor Faixa Health")
            vis.append(container(pg, "chartHealth", 1378, 714, 500, 326, z + 22, {
                "visualType": "clusteredBarChart",
                "query": {"queryState": q, "sortDefinition": {"sort": [{"field": fM("Clientes Monitorados"), "direction": "Descending"}]}},
                "objects": objs, "visualContainerObjects": chart_vco("Health Score por Faixa  ·  contas ativas no último mês"),
                "drillFilterOtherVisuals": True}))
        elif pg == "growth":
            vis.append(container(pg, "denebCAC", 292, 344, 1038, 320, z + 20, deneb_visual(
                [proj_c("dCanalAquisicao", "Canal", "canal"), proj_m("CAC", "cac"), proj_m("LTV Estimado", "ltv"),
                 proj_m("LTV:CAC", "ratio"), proj_m("Rótulo LTV CAC", "rotulo"), proj_m("Rótulo CAC", "cacTxt"),
                 proj_m("Rótulo LTV", "ltvTxt"), proj_m("Cor LTV CAC", "cor")], SPEC_CACLTV,
                "CAC vs. LTV por Canal  ·  barra colorida = LTV estimado · barra branca = CAC · rótulo = LTV:CAC")))
            vis.append(container(pg, "tblCanal", 292, 706, 1038, 336, z + 21, table_visual(
                [proj_c("dCanalAquisicao", "Canal", "Canal", active=False), proj_m("Investimento Marketing", "Investimento"),
                 proj_m("SVG Barra CAC", "CAC"), proj_m("Trial → Paid %", "Trial → Paid"), proj_m("SVG Barra LTV CAC", "LTV:CAC"),
                 proj_m("CAC Payback", "Payback")],
                "Eficiência dos Canais  ·  ordenado por investimento", sort=("m", "Investimento Marketing", "Descending"), tt="ttCanal", img=True)))
            vis.append(container(pg, "denebFunil", 1378, 344, 500, 696, z + 22, deneb_visual(
                [proj_c("dEtapaFunil", "EtapaFunil", "etapa"), proj_c("dEtapaFunil", "OrdemFunil", "ordem"),
                 proj_m("Valor Etapa Funil", "valor"), proj_m("Rótulo Etapa Funil", "rotulo"), proj_m("Rótulo Conversão Funil", "conv")],
                SPEC_FUNIL, "Funil de Aquisição  ·  largura em escala log")))

        # ---------------- painel de filtros (oculto)
        panel_names = []
        PX = 1490
        n, v = container(pg, "fp_bg", PX, 12, 418, 1056, 50000, shape_panel(), hidden=True)
        vis.append((n, v)); panel_names.append(n)
        n, v = container(pg, "fp_title", PX + 26, 34, 300, 70, 50001, textbox([
            {"textRuns": [{"value": "Filtros", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "22pt", "color": "#FFFFFF"}}]},
            {"textRuns": [{"value": "Aplicados em todas as páginas", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#A9BBD8"}}]}]),
            hidden=True)
        vis.append((n, v)); panel_names.append(n)
        sl = [("dCalendario", "Ano", "Ano", "Ano"), ("dCalendario", "MesAno", "Mês", "Mes"), ("dPlano", "Plano", "Plano", "Plano"),
              ("dCanalAquisicao", "Canal", "Canal de aquisição", "Canal"), ("dSegmento", "Segmento", "Segmento", "Segmento"),
              ("dPorte", "Porte", "Porte", "Porte"), ("dCliente", "TipoCobranca", "Tipo de cobrança", "Cobranca"),
              ("dCohort", "CohortAno", "Cohort (ano de aquisição)", "Cohort")]
        for i, (t, c_, h_, g) in enumerate(sl):
            n, v = container(pg, f"fp_sl{i}", PX + 26, 120 + i * 80, 366, 68, 50010 + i, slicer(t, c_, h_, g), hidden=True)
            vis.append((n, v)); panel_names.append(n)
        n, v = container(pg, "fp_clear", PX + 26, 790, 366, 42, 50030,
                         button("Limpar filtros", clear_link(), fill=C["panel"], hover=C["red"], radius=21, outline=C["cyan"]), hidden=True)
        vis.append((n, v)); panel_names.append(n)
        n, v = container(pg, "fp_apply", PX + 26, 844, 366, 46, 50031,
                         button("Aplicar e fechar", bm_link(bm_close), fill=C["blue"], hover=C["violet"], radius=23), hidden=True)
        vis.append((n, v)); panel_names.append(n)
        n, v = container(pg, "fp_x", PX + 360, 36, 36, 36, 50032,
                         button("✕", bm_link(bm_close), fill=C["panel"], hover=C["red"], radius=18, size=12, tooltip="Fechar painel"), hidden=True)
        vis.append((n, v)); panel_names.append(n)
        types = {n: v["visual"]["visualType"] for n, v in vis}
        for bm, disp_, hide in [(bm_open, f"Filtros abertos · {disp}", False), (bm_close, f"Filtros fechados · {disp}", True)]:
            vc_ = {}
            for n in panel_names:
                sv = {"visualType": types[n], "objects": {}}
                if hide:
                    sv["display"] = {"mode": "hidden"}
                vc_[n] = {"singleVisual": sv}
            bookmarks.append({"$schema": BM_SCHEMA, "displayName": disp_, "name": bm,
                              "options": {"targetVisualNames": panel_names, "suppressData": True, "applyOnlyToTargetVisuals": True},
                              "explorationState": {"version": "1.0", "activeSection": pg, "sections": {pg: {"visualContainers": vc_}}}})
        pages[pg] = (page_json(pg, disp, BG[pg]), vis)

    # ------------------------------------------------ tooltips
    for name, disp, m in TT:
        vis = [container(name, "html", 0, 0, 360, 240, 1000, html_visual(m))]
        pages[name] = (page_json(name, disp, "bg_tooltip.png", 360, 240, tooltip=True), vis)
    return pages, bookmarks


def grupo_filter():
    return {"filters": [{"name": hid("flt", "grupo"), "field": fC("dTipoMovimento", "GrupoMovimento"), "type": "Categorical",
                         "filter": {"Version": 2, "From": [{"Name": "d", "Entity": "dTipoMovimento", "Type": 0}],
                                    "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "GrupoMovimento"}}],
                                                                    "Values": [[{"Literal": {"Value": "'Ganho'"}}], [{"Literal": {"Value": "'Perda'"}}]]}}}]},
                         "howCreated": "User"}]}


def series_colors():
    cores = [("Novo", "#00B8F5"), ("Expansão", "#00D7C0"), ("Reativação", "#1678FF"), ("Contração", "#FFA3B3"), ("Churn", "#FF607A")]
    out = []
    for v, c in cores:
        out.append({"properties": {"fill": col(c)},
                    "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": fC("dTipoMovimento", "Movimento"),
                                                                      "Right": {"Literal": {"Value": f"'{v}'"}}}}}]}})
    return out


def table_visual(projs, title, sort=None, tt=None, img=False):
    q = {"queryState": {"Values": {"projections": projs}}}
    if sort:
        if sort[0] == "c":
            q["sortDefinition"] = {"sort": [{"field": fC(sort[1], sort[2]), "direction": sort[3]}]}
        else:
            q["sortDefinition"] = {"sort": [{"field": fM(sort[1]), "direction": sort[2]}]}
    center = []
    for p in projs:
        center.append({"properties": {"alignment": Ls("Center")}, "selector": {"metadata": p["queryRef"]}})
    objs = {
        "grid": props(gridVertical=Lb(False), gridHorizontal=Lb(True), gridHorizontalColor=col(C["grid"]), gridHorizontalWeight=Ld(1),
                      rowPadding=Ld(2 if img else 6), outlineColor=col(C["grid"]), outlineWeight=Ld(1), textSize=Ld(11),
                      **({"imageHeight": Ld(22), "imageWidth": Ld(180)} if img else {})),
        "columnHeaders": props(fontColor=col(C["sec"]), backColor=col(C["panel"]), fontSize=Ld(10.5), fontFamily=Ls("Segoe UI Semibold"),
                               alignment=Ls("Center"), wordWrap=Lb(True)),
        "values": props(fontColorPrimary=col(C["white"]), backColorPrimary=col("#08152F"), fontColorSecondary=col(C["white"]),
                        backColorSecondary=col("#0B1A3A"), fontSize=Ld(11), wordWrap=Lb(False)),
        "total": props(totals=Lb(True), fontColor=col(C["white"]), backColor=col(C["panel"]), fontSize=Ld(11), fontFamily=Ls("Segoe UI Semibold")),
        "columnFormatting": center,
    }
    return {"visualType": "tableEx", "query": q, "objects": objs, "visualContainerObjects": chart_vco(title, tt),
            "drillFilterOtherVisuals": True}


# ---------------------------------------------------------------- escrita
def write_report(root, assets_dir, base_theme_file=None):
    d = os.path.join(root, "definition")
    if os.path.exists(os.path.join(d, "pages")):
        shutil.rmtree(os.path.join(d, "pages"))
    if os.path.exists(os.path.join(d, "bookmarks")):
        shutil.rmtree(os.path.join(d, "bookmarks"))
    os.makedirs(os.path.join(d, "pages"), exist_ok=True)
    os.makedirs(os.path.join(d, "bookmarks"), exist_ok=True)
    rr = os.path.join(root, "StaticResources", "RegisteredResources")
    os.makedirs(rr, exist_ok=True)
    items = []
    for f in ["bg_home.png", "bg_exec.png", "bg_revenue.png", "bg_customer.png", "bg_growth.png", "bg_tooltip.png"]:
        shutil.copy(os.path.join(assets_dir, f), os.path.join(rr, f))
        items.append({"name": f, "path": f, "type": "Image"})
    json.dump(theme(), open(os.path.join(rr, "NEXORA_Dark.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    items.append({"name": "NEXORA_Dark.json", "path": "NEXORA_Dark.json", "type": "CustomTheme"})
    report = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {"customTheme": {"name": "NEXORA_Dark.json",
                                            "reportVersionAtImport": {"visual": "2.13.0", "report": "3.4.0", "page": "2.3.1"},
                                            "type": "RegisteredResources"}},
        "objects": {"outspacePane": [{"properties": {"expanded": Lb(False)}}],
                    "section": [{"properties": {"verticalAlignment": Ls("Top")}}]},
        "publicCustomVisuals": [HTMLV, DENEB],
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items": items}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized", "defaultDrillFilterOtherVisuals": True,
                     "allowChangeFilterTypes": True, "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True},
    }
    if base_theme_file:
        report["themeCollection"]["baseTheme"] = {"name": "Fluent2-CY26SU09",
                                                  "reportVersionAtImport": {"visual": "2.13.0", "report": "3.4.0", "page": "2.3.1"},
                                                  "type": "SharedResources"}
        report["resourcePackages"].insert(0, {"name": "SharedResources", "type": "SharedResources",
                                              "items": [{"name": "Fluent2-CY26SU09", "path": "BaseThemes/Fluent2-CY26SU09.json", "type": "BaseTheme"}]})
    json.dump(report, open(os.path.join(d, "report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    pages, bms = build_pages()
    order = [p for p, _ in PAGES] + [t[0] for t in TT]
    json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
               "pageOrder": order, "activePageName": "home"},
              open(os.path.join(d, "pages", "pages.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    nvis = 0
    for name, (pj, vis) in pages.items():
        pd_ = os.path.join(d, "pages", name)
        os.makedirs(os.path.join(pd_, "visuals"), exist_ok=True)
        json.dump(pj, open(os.path.join(pd_, "page.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        for vn, vj in vis:
            os.makedirs(os.path.join(pd_, "visuals", vn), exist_ok=True)
            json.dump(vj, open(os.path.join(pd_, "visuals", vn, "visual.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            nvis += 1
    for b in bms:
        json.dump(b, open(os.path.join(d, "bookmarks", f"{b['name']}.bookmark.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json",
               "items": [{"name": b["name"]} for b in bms]},
              open(os.path.join(d, "bookmarks", "bookmarks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(pages), nvis, len(bms)
