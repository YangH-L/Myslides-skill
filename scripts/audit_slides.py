#!/usr/bin/env python3
"""
Automated Slide Deck & Speaker Notes Quality Auditor (`audit_slides.py`).

Audits any `.pptx` file (and optional `--notes-md` Markdown notes file) against
the 6 machine-verifiable checks of `Myslides-skill`:
  1. Habit 1: Trailing Chinese period `。` residuals on slide body text
  2. Habit 2: Bottom conclusion bar prefix (`本页核心结论`/`核心结论`/`小结`) or non-centered alignment
  3. Habit 3: Banned AI buzzwords and discouraged terms (`探针`, `金标准`, `金标`, `锁稿`, `全绿`, etc.)
  4. Habit 6: Low-contrast light-gray text colors (`#B8B8B8`, `#9CA3AF`, `#667085`, etc.)
  5. Habit 4: Explicit Latin font slot check (`Times New Roman` expected when Latin/digits appear)
  6. Habit 8 & 5: Speaker notes ordering & Arabic-numeral spoken style — spoken script
     (`现场汇报口播参考` / `口播参考`) MUST appear ABOVE plain-language breakdown (`白话拆解`) with
     a separator line between them, use Arabic numerals (`96.5%`, `12.4 倍`, `4.5 分钟`) instead of
     spelled-out Chinese percentages/decimals (`百分之...`, `...点...`, `...分半钟`), and end with
     parenthesized provenance `（...来源：...）` at the bottom.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}
EMU_PER_PX = 9525.0

BANNED_TERMS_PATTERNS = [
    r"探针",
    r"人工金标准",
    r"金标准",
    r"金标",
    r"锁稿",
    r"正式锁稿",
    r"准投",
    r"全绿验收",
    r"绿灯验收",
    r"测试全绿",
    r"全绿",
    r"架构翻转",
    r"范式翻转",
    r"跃升",
    r"倒挂",
    r"底座",
    r"排雷",
    r"闭环",
    r"一审一护",
    r"同尺桥接",
    r"同尺",
    r"零重叠论文矩阵",
    r"论文矩阵",
    r"锚定",
    r"咬合",
    r"兑现里程碑",
    r"硬核",
    r"假世界",
    r"裸用",
    r"裸模型",
    r"引擎\s*2\.0",
    r"系统\s*2\.0",
    r"2\.0\s*升级",
]
BANNED_RE = re.compile("|".join(BANNED_TERMS_PATTERNS))

TAKEAWAY_PREFIX_RE = re.compile(r"^(本页核心结论|核心结论|本页结论|本页小结|小结)\s*[:：]")

LIGHT_GRAY_HEXES = {
    "B8B8B8",
    "9CA3AF",
    "667085",
    "94A3B8",
    "CBD5E1",
    "D1D5DB",
    "A1A1AA",
    "9E9E9E",
}

LATIN_OR_DIGIT_RE = re.compile(r"[A-Za-z0-9]")

# Habit 8: Flag spelled-out quantitative Chinese numerals in spoken script
SPOKEN_CHINESE_NUMERAL_RE = re.compile(
    r"百分之[零一二三四五六七八九十百千万点两]+"
    r"|[零一二三四五六七八九十百两]+点[零一二三四五六七八九十]+"
    r"|[一二三四五六七八九十两]+分半钟?"
    r"|[一二三四五六七八九十两][百千][零一二三四五六七八九十百千万两]*"
)


def audit_note_block(label: str, note_text: str) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    txt = note_text.strip()
    if not txt:
        issues.append({"location": label, "check": "notes_structure", "severity": "error", "message": "Speaker note is empty"})
        return issues

    m_banned = BANNED_RE.findall(txt)
    if m_banned:
        issues.append(
            {
                "location": label,
                "check": "banned_terms",
                "severity": "error",
                "message": f"Banned terms in speaker note: {sorted(set(m_banned))}",
            }
        )

    spoken_m = re.search(r"(现场汇报口播参考|口播参考)", txt)
    plain_m = re.search(r"白话拆解", txt)
    source_m = re.search(r"[（(][^（）()]*来源[:：][^（）()]*[）)]", txt)

    if not spoken_m:
        issues.append(
            {
                "location": label,
                "check": "notes_structure",
                "severity": "error",
                "message": "Missing top spoken-script section header (e.g., 【一、现场汇报口播参考】)",
            }
        )
    if not plain_m:
        issues.append(
            {
                "location": label,
                "check": "notes_structure",
                "severity": "error",
                "message": "Missing plain-language breakdown section header (e.g., 【二、本页白话拆解】)",
            }
        )
    if spoken_m and plain_m:
        if spoken_m.start() > plain_m.start():
            issues.append(
                {
                    "location": label,
                    "check": "notes_order",
                    "severity": "error",
                    "message": "Habit 8 violation: 【现场汇报口播参考】 must appear ABOVE 【白话拆解】",
                }
            )
        else:
            between = txt[spoken_m.end() : plain_m.start()]
            if not re.search(r"(---|───|===|___)", between):
                issues.append(
                    {
                        "location": label,
                        "check": "notes_separator",
                        "severity": "warning",
                        "message": "Expected a clear visual divider line (e.g., ---) between spoken script and breakdown",
                    }
                )
            cn_num_hits = SPOKEN_CHINESE_NUMERAL_RE.findall(between)
            if cn_num_hits:
                issues.append(
                    {
                        "location": label,
                        "check": "spoken_chinese_numeral",
                        "severity": "error",
                        "message": (
                            f"Habit 8 violation: use Arabic numerals & '%' in spoken script instead of "
                            f"spelled-out Chinese numbers: {sorted(set(cn_num_hits))}"
                        ),
                    }
                )
    elif spoken_m:
        cn_num_hits = SPOKEN_CHINESE_NUMERAL_RE.findall(txt[spoken_m.end() :])
        if cn_num_hits:
            issues.append(
                {
                    "location": label,
                    "check": "spoken_chinese_numeral",
                    "severity": "error",
                    "message": (
                        f"Habit 8 violation: use Arabic numerals & '%' in spoken script instead of "
                        f"spelled-out Chinese numbers: {sorted(set(cn_num_hits))}"
                    ),
                }
            )
    if not source_m:
        issues.append(
            {
                "location": label,
                "check": "notes_provenance",
                "severity": "error",
                "message": "Missing parenthesized provenance at bottom of note: （图表与数据来源：...）",
            }
        )
    elif plain_m and source_m.start() < plain_m.start():
        issues.append(
            {
                "location": label,
                "check": "notes_order",
                "severity": "warning",
                "message": "Parenthesized source note should appear at the bottom after 【白话拆解】",
            }
        )
    return issues


def audit_pptx(pptx_path: Path) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX not found: {pptx_path}")

    with zipfile.ZipFile(pptx_path, "r") as zf:
        slide_names = sorted(
            [n for n in zf.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)],
            key=lambda s: int(re.search(r"slide(\d+)\.xml$", s).group(1)),
        )
        slide_h_px = 720.0
        if "ppt/presentation.xml" in zf.namelist():
            pres_root = ET.fromstring(zf.read("ppt/presentation.xml"))
            sldSz = pres_root.find("p:sldSz", NS)
            if sldSz is not None and sldSz.get("cy"):
                slide_h_px = int(sldSz.get("cy", "6858000")) / EMU_PER_PX

        has_closing_thanks = False

        for s_name in slide_names:
            s_num = int(re.search(r"slide(\d+)\.xml$", s_name).group(1))
            root = ET.fromstring(zf.read(s_name))
            is_hidden = root.get("show") == "0"
            s_label = f"Slide {s_num}" + (" (hidden)" if is_hidden else "")

            slide_all_text_parts: List[str] = []

            for sp in root.findall(".//p:sp", NS):
                cNvPr = sp.find("p:nvSpPr/p:cNvPr", NS)
                sh_name = cNvPr.get("name", "shape") if cNvPr is not None else "shape"
                xfrm = sp.find("p:spPr/a:xfrm", NS)
                y_px = 0.0
                if xfrm is not None:
                    off = xfrm.find("a:off", NS)
                    if off is not None and off.get("y") is not None:
                        y_px = int(off.get("y", "0")) / EMU_PER_PX

                txBody = sp.find("p:txBody", NS)
                if txBody is None:
                    continue

                for p_el in txBody.findall("a:p", NS):
                    p_text = "".join(t.text or "" for t in p_el.findall(".//a:t", NS)).strip()
                    if not p_text:
                        continue
                    slide_all_text_parts.append(p_text)

                    # Check 1: Trailing Chinese period on visible slide text
                    if not is_hidden and p_text.endswith("。"):
                        issues.append(
                            {
                                "location": f"{s_label} [{sh_name}]",
                                "check": "trailing_period",
                                "severity": "warning",
                                "message": f"Slide outline line ends with '。': {p_text[-36:]!r}",
                            }
                        )

                    # Check 2: Bottom takeaway band (0.80*H <= y <= 0.90*H)
                    if not is_hidden and (0.80 * slide_h_px) <= y_px <= (0.90 * slide_h_px) and len(p_text) >= 10:
                        if TAKEAWAY_PREFIX_RE.search(p_text):
                            issues.append(
                                {
                                    "location": f"{s_label} [{sh_name}]",
                                    "check": "takeaway_prefix",
                                    "severity": "error",
                                    "message": f"Bottom takeaway contains forbidden prefix: {p_text[:28]!r}",
                                }
                            )
                        pPr = p_el.find("a:pPr", NS)
                        algn = pPr.get("algn") if pPr is not None else None
                        if algn != "ctr":
                            issues.append(
                                {
                                    "location": f"{s_label} [{sh_name}]",
                                    "check": "takeaway_alignment",
                                    "severity": "warning",
                                    "message": f"Bottom takeaway alignment is {algn!r} (expected 'ctr' centered)",
                                }
                            )

                    # Check 4 & 5: Run-level color contrast & Times New Roman Latin slot
                    for r_el in p_el.findall("a:r", NS):
                        r_txt = "".join(t.text or "" for t in r_el.findall("a:t", NS))
                        if not r_txt.strip():
                            continue
                        rPr = r_el.find("a:rPr", NS)
                        if rPr is None:
                            continue
                        srgb = rPr.find("a:solidFill/a:srgbClr", NS)
                        if srgb is not None:
                            val = (srgb.get("val") or "").upper()
                            if val in LIGHT_GRAY_HEXES and not is_hidden:
                                issues.append(
                                    {
                                        "location": f"{s_label} [{sh_name}]",
                                        "check": "low_contrast_gray",
                                        "severity": "error",
                                        "message": f"Forbidden low-contrast gray #{val} on text {r_txt[:24]!r}",
                                    }
                                )
                        if not is_hidden and LATIN_OR_DIGIT_RE.search(r_txt):
                            lat = rPr.find("a:latin", NS)
                            face = lat.get("typeface") if lat is not None else None
                            if face and face != "Times New Roman":
                                issues.append(
                                    {
                                        "location": f"{s_label} [{sh_name}]",
                                        "check": "latin_font",
                                        "severity": "warning",
                                        "message": f"Latin/digit run {r_txt[:20]!r} uses latin typeface {face!r} instead of 'Times New Roman'",
                                    }
                                )

            joined_slide_txt = "\n".join(slide_all_text_parts)
            if "感谢聆听" in joined_slide_txt:
                has_closing_thanks = True

            # Check 3: Banned AI terms on slide
            hits = BANNED_RE.findall(joined_slide_txt)
            if hits:
                issues.append(
                    {
                        "location": s_label,
                        "check": "banned_terms",
                        "severity": "error",
                        "message": f"Banned terms on slide: {sorted(set(hits))}",
                    }
                )

            # Check 6: Speaker note for this slide
            note_part = f"ppt/notesSlides/notesSlide{s_num}.xml"
            if note_part in zf.namelist():
                n_root = ET.fromstring(zf.read(note_part))
                note_paras: List[str] = []
                for sp in n_root.findall(".//p:sp", NS):
                    ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
                    if ph is not None and ph.get("type") in ("sldImg", "sldNum", "hdr", "ftr", "dt"):
                        continue
                    for p_el in sp.findall(".//a:p", NS):
                        ptxt = "".join(t.text or "" for t in p_el.findall(".//a:t", NS))
                        if ptxt.strip():
                            note_paras.append(ptxt)
                issues.extend(audit_note_block(f"{s_label} Notes", "\n".join(note_paras)))
            elif not is_hidden:
                issues.append(
                    {
                        "location": f"{s_label} Notes",
                        "check": "notes_missing",
                        "severity": "error",
                        "message": "Visible slide has no speaker notes part",
                    }
                )

        if not has_closing_thanks:
            issues.append(
                {
                    "location": "Deck",
                    "check": "closing_slide",
                    "severity": "warning",
                    "message": "Habit 9: No closing '感谢聆听' slide detected in presentation",
                }
            )

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    return {
        "file": str(pptx_path),
        "slides_checked": len(slide_names),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "status": "passed" if not errors else "failed",
        "issues": issues,
    }


def audit_notes_markdown(md_path: Path) -> Dict[str, Any]:
    raw = md_path.read_text(encoding="utf-8")
    # Split top-level `# slide_slug` sections
    parts = re.split(r"(?m)^#\s+([^\n]+)\n", raw)
    issues: List[Dict[str, Any]] = []
    section_count = 0
    for i in range(1, len(parts), 2):
        sec_title = parts[i].strip()
        sec_body = parts[i + 1]
        section_count += 1
        issues.extend(audit_note_block(f"MD[{sec_title}]", sec_body))
    errors = [x for x in issues if x["severity"] == "error"]
    return {
        "notes_md": str(md_path),
        "sections_checked": section_count,
        "error_count": len(errors),
        "warning_count": len(issues) - len(errors),
        "status": "passed" if not errors else "failed",
        "issues": issues,
    }


def run_self_test() -> int:
    good_note = (
        "【一、现场汇报口播参考】\n各位老师好，第一点汇报动态图流实验：在 1,200 组查询上吞吐率达 96.5%、"
        "提速 12.4 倍，全程耗时 4.5 分钟。\n\n"
        "---\n\n"
        "【二、本页白话拆解（供会前自己看懂）】\n把局部未变化子图跳过重算，吞吐率提升 12.4 倍。\n\n"
        "（图表与数据来源：公开基准 Cora 与 Reddit-Stream 实测记录，样本量 n = 1,200）"
    )
    assert audit_note_block("self-test-good", good_note) == []

    bad_order_note = (
        "【一、白话拆解】\n先放白话。\n---\n【二、现场汇报口播参考】\n后放口播。\n（图表与数据来源：实验台账）"
    )
    bad_issues = audit_note_block("self-test-bad", bad_order_note)
    assert any(i["check"] == "notes_order" for i in bad_issues)

    bad_cn_num_note = (
        "【一、现场汇报口播参考】\n准确率达百分之九十六点五，耗时四分半钟，覆盖一千二百组样本。\n\n"
        "---\n\n"
        "【二、本页白话拆解】\n拆解内容。\n\n"
        "（图表与数据来源：公开基准实测记录）"
    )
    cn_issues = audit_note_block("self-test-cn-num", bad_cn_num_note)
    assert any(i["check"] == "spoken_chinese_numeral" for i in cn_issues)
    print("[OK] audit_slides.py --self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit academic .pptx decks and speaker notes against Myslides-skill guidelines."
    )
    parser.add_argument("pptx", nargs="?", help="Path to the .pptx presentation to audit")
    parser.add_argument("--notes-md", help="Optional path to notes/total.md to audit")
    parser.add_argument("--json", action="store_true", help="Print full report as JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.pptx and not args.notes_md:
        parser.print_help()
        return 1

    reports: Dict[str, Any] = {}
    has_error = False
    if args.pptx:
        rep = audit_pptx(Path(args.pptx))
        reports["pptx"] = rep
        has_error = has_error or (rep["error_count"] > 0)
    if args.notes_md:
        mrep = audit_notes_markdown(Path(args.notes_md))
        reports["notes_md"] = mrep
        has_error = has_error or (mrep["error_count"] > 0)

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for key, rep in reports.items():
            print(f"[{rep['status'].upper()}] {key}: errors={rep['error_count']}, warnings={rep['warning_count']}")
            for item in rep["issues"]:
                print(f"  - [{item['severity'].upper()}] {item['location']} ({item['check']}): {item['message']}")

    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
