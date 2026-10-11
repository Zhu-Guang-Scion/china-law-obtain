# china-law-obtain

**Acquire, verify and maintain a local library of all current-effective laws & regulations of mainland China — straight from the two official databases, with mirrors, OCR and four-layer verification.**

中国大陆现行法律法规规章制度库的全流程获取工具：官方库枚举 → 多源下载（官方 API / 公开镜像 / OCR）→ 四层校验 → 分类整理 + Markdown 双格式 + 涉税/涉会计专题 → 增量更新。全部踩坑结论已固化，开箱即用。

> **obtain** — 一次配好获取路径，以后更新法规不再走弯路。

## What it does

| Source | Coverage (2026-10 measured) | Notes |
|---|---|---|
| 国家法律法规数据库 [flk.npc.gov.cn](https://flk.npc.gov.cn) | 宪法 · 法律 · 行政法规 · 监察法规 · 地方法规 · 司法解释 — 17,261 current-effective items | Full enumeration via leaf category codes + `sxx=3`; official docx/pdf download |
| 国家规章库 [gov.cn/gjgzk](https://www.gov.cn/zhengce/xxgk/gjgzk/) | 部门规章 · 地方政府规章 — 10,523 items | Detail-page text extraction with 3-level fallback (standard div → generic CJK paragraphs → search-API content field) |
| Public mirrors (cross-validation) | lawtext/legal-data-docx (official docx snapshots, sha256-verified), lawtext/regulations, HuggingFace snapshot | Faster than official API when throttled; used for gap-fill and cross-checks |
| 会计准则与执业准则 (MOF + CICPA) | 企业会计准则 · 政府及行业会计制度 · CPA practice standards — 268 items | Dedicated downloaders for kjs.mof.gov.cn / fgk.mof.gov.cn / CICPA; full doc numbers (文号) recorded |
| MinerU OCR | scanned PDFs | Official scans → Markdown with quality validation against reference text |

End-to-end result on a full build: **27,784 / 27,784 items (100%)**, each with the original file (docx/pdf/doc) **and** a Markdown version with front matter, plus dedicated folders for tax-related (涉税) and accounting-related (涉会计) laws.

## Repository layout

```
china-law-obtain/
├── SKILL.md                 # Full pipeline manual (agent-skill format, also human-readable)
├── scripts/                 # 28 standalone Python scripts (resumable, idempotent, path-portable)
│   ├── flk_enumerate.py     #   enumerate flk.npc.gov.cn current-effective corpus
│   ├── govlib.py            #   enumerate gov.cn rules library (self-generated auth key)
│   ├── flk_download.py      #   official docx/pdf downloads (WAF cookie pool)
│   ├── flk_cookie.py        #   harvest WAF cookies via headless browser
│   ├── gov_download.py      #   rules library HTML → docx (with API-content fallback)
│   ├── gap_fetch_proxy.py / upgrade_fetch.py / mirror_fill.py / md_fill.py
│   │                        #   mirror-based gap-fill & upgrade (sha256-verified)
│   ├── gov_repair.py / redoc.py / mojibake_scan.py / moji_fix.py
│   │                        #   repairs: thin content, legacy .doc, garbled text
│   ├── verify.py            #   4-layer verification (counts/integrity/sampling/cross-mirror)
│   ├── organize_md.py       #   final library: categorized folders + Markdown + topic folders
│   ├── kjs_enum.py / kjs_cas_download.py / fgk_search.py / std_gov_acct.py
│   │                        #   accounting standards (MOF) downloaders
│   ├── cicpa_enum.py / cicpa_std_download.py / cicpa_guide_supp.py
│   │                        #   CPA practice standards (CICPA) downloaders
│   ├── standards_organize.py #  standards library: categorized folders + Markdown + manifest
│   ├── build_catalog.py     #   multi-dimension catalog index (6 dimensions, agent-friendly)
│   ├── diff_update.py       #   incremental update diff (new / removed / changed)
│   ├── mineru_upgrade.py    #   scanned-PDF OCR upgrade (tokens via env, validated)
│   └── waf_watch.py / xmlfallback.py  # helpers
├── docs/RESPONSIBLE_USE.md  # scope, data policy & responsible-use notes
├── requirements.txt
└── LICENSE                  # MIT (code only — see data policy)
```

**Path conventions** — all scripts locate the repo root relative to their own location; override with `CHINALAW_ROOT` (repo root) or `CHINA_LAW_WORK` (work dir, default `<repo>/work/`). No hardcoded machine paths.

## Quick start

```bash
pip install -r requirements.txt
python -m pip install playwright && python -m playwright install chromium  # optional, for WAF cookies

# Layout convention: one base dir holds work/ (lists, downloads, logs, verify);
# mirrors/ (optional local mirror copies) and the output lawlibrary/ live BESIDE work/.
export CHINA_LAW_WORK=/path/to/base/work   # or run from a base dir containing ./work
mkdir -p $CHINA_LAW_WORK/{lists,downloads/flk,downloads/gov,logs,verify} \
         $(dirname $CHINA_LAW_WORK)/mirrors

AQ=/path/to/china-law-obtain   # 克隆的仓库(含 scripts/)                 # the cloned repo (where scripts/ lives)
python $AQ/scripts/flk_enumerate.py        # 1. enumerate national laws DB (~17k items, ~1 min)
python $AQ/scripts/govlib.py               # 2. enumerate rules library (~10k items)
python $AQ/scripts/gov_download.py 部门规章 4   # 3. download (resumable)
python $AQ/scripts/flk_download.py 法律 3
python $AQ/scripts/verify.py all           # 4. verify
python $AQ/scripts/organize_md.py          # 5. organize + Markdown + topics (-> ../lawlibrary)
python $AQ/scripts/build_catalog.py        # 6. optional: multi-dimension catalog index (-> ../法规目录索引)
```

Incremental update later:

```bash
cd $CHINA_LAW_WORK && cp -r lists lists_old
python $AQ/scripts/flk_enumerate.py && python $AQ/scripts/govlib.py
python $AQ/scripts/diff_update.py lists_old lists .   # new / removed / changed
# ...download only the new items (resumable), re-verify, re-organize
```

## Output library shape

Created beside `work/` (i.e. `$(dirname $CHINA_LAW_WORK)/lawlibrary`):

```
lawlibrary/
├── manifest.csv                       # every item: category / issuer / date / topic / source / dual-format paths / official link
├── 国家法律法规数据库/<category>/{原文件, Markdown}/
├── 国家规章库/<category>/{原文件, Markdown}/
├── 会计准则与执业准则/<三类>/{原文件, Markdown}/   # MOF standards + CICPA practice standards (268 items)
├── 专题/{涉税法规, 涉会计法规, 税务案例}/...      # topic copies (keyword-classified, editable list)
└── (平级) 法规目录索引/                              # catalog: 索引总表.csv + 6-dimension Markdown indexes
```

## Highlights (the hard-won parts)

- **flk leaf category codes** — top-level codes return 0 rows; you need the leaf codes (法律 = 110–170, 地方性法规 = 230 …), enumerated in `flk_enumerate.py`
- **Full enumeration without a keyword** — empty `searchContent` + category codes + `sxx:[3]`, `pageSize` up to 500
- **Wangsu WAF (wzws) cookie pool** — burst downloads trigger a JS challenge; `flk_cookie.py` harvests cookies with a real browser and the downloader rotates them with adaptive backoff
- **gov.cn rules-library auth key is statically derivable** — `athenaappkey = urlEncode(base64(RSA_PKCS1v15(pubkey, appid)))`, both constants public in the site's own frontend JS → generated locally, no browser needed
- **GitHub throttling workaround** — `gh-proxy.com`/`ghproxy.net` prefixes speed raw file fetch ~10×; every mirror file is sha256-verified against the upstream index
- **Scanned PDFs** — MinerU OCR with quality gates (char-count and article-count ratios vs reference text before replacing)
- **Garbled-text sweep** — U+FFFD rebuilds from the rules-library API text; PUA glyph stripping; sequence-based 锟斤拷 detection (counting single chars like 斤 false-positives on 公斤)

All of these are documented in `SKILL.md` (Chinese) with a "known pitfalls" section so nobody re-derives them.

## Data policy & responsible use

This repository **contains code and documentation only — no legal texts or downloaded documents**. See [docs/RESPONSIBLE_USE.md](docs/RESPONSIBLE_USE.md):

- PRC laws and regulations are not copyrightable (著作权法第五条); the official databases are the authoritative source — this tool fetches public-domain content from them for personal research/archival use
- Built-in rate limiting (0.2–1 s per request plus adaptive backoff, bounded workers); do not remove it
- The auth-key derivation and WAF-cookie harvesting reproduce what the sites' own public JavaScript does in a normal browser session — provided for interoperability with public data, not for accessing anything non-public
- Respect the source websites' terms of service; do not use this for commercial redistribution of database compilations

## License

MIT for the code. The downloaded legal texts belong to their official publishers (public domain per PRC copyright law); this project does not claim any rights over them and does not redistribute them.

## Acknowledgements

Cross-validation mirrors used (and recommended): [lawtext](https://github.com/lawtext) automated flk backups, [LawRefBook/Laws](https://github.com/LawRefBook/Laws), [twang2218/chinese-law-and-regulations](https://huggingface.co/datasets/twang2218/chinese-law-and-regulations) (HuggingFace), [MinerU](https://mineru.net) for OCR.
