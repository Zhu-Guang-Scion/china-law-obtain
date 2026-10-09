# Responsible Use & Data Policy

## What this project is

`china-law-obtain` is a set of scripts that **acquire** the current-effective corpus of PRC laws, administrative regulations, supervisory regulations, judicial interpretations, local regulations and government rules from the two official public databases, convert them to a tidy local library (original files + Markdown), and keep that library up to date incrementally.

## What this repository contains

**Code and documentation only.** No legal texts, no downloaded documents, no databases, no generated manifests are committed or distributed by this project (enforced by `.gitignore`). Users run the scripts themselves against the official sources.

## Data & copyright position

- Article 5 of the PRC Copyright Law excludes **laws and regulations, resolutions, decisions and other documents of a legislative, administrative or judicial nature** from copyright protection. The legal texts themselves are public domain.
- The **authoritative source** is and remains the official databases:
  - 国家法律法规数据库 <https://flk.npc.gov.cn>
  - 国家规章库 <https://www.gov.cn/zhengce/xxgk/gjgzk/>
- This project is for **personal research, archiving and lawful use**. It is not affiliated with, endorsed by, or connected to any of the source websites.
- Database **compilations** (selection/arrangement) and site interfaces may enjoy separate protection. Do not use this tool to build commercial redistributions of a source database's compilation. If you publish derivatives (e.g., a curated corpus), cite the official source.

## Rate limits & server friendliness

All download scripts ship with deliberate throttling (0.2–1 s per request, bounded worker counts, adaptive back-off, WAF-trigger cooldowns). Please keep them. Do not run multi-machine farms against these government websites. If a source site blocks you, wait — the scripts are fully resumable.

## About the auth-key derivation and cookie harvesting

Two techniques in this repo interact with client-side access mechanisms of public pages:

1. **Rules-library `athenaappkey`** — both the RSA public key and the app id are static constants inside the rules library's own public frontend JavaScript; the scripts merely perform the same computation a visitor's browser performs. It grants access to nothing that is not already publicly served.
2. **WAF cookies (`wzws_cid`)** — when the anti-bot layer challenges, `flk_cookie.py` loads the site in a real headless browser and uses the cookies that browser obtained, i.e. it passes the challenge the way any JavaScript-enabled browser does.

These are interoperability measures for **public-domain content on public pages**, comparable to existing open-source crawlers for the same databases. They do not bypass authentication, payment, or access control on any non-public resource. If the site operators publish an official open API or object to this access pattern, follow their preference.

## Miners / OCR

MinerU OCR is optional; if used, set your own token via the `MINERU_TOKEN` environment variable (get one at <https://mineru.net/apiManage/token>). No tokens are shipped in this repository.

## No warranty

Provided as-is under the MIT License. The maintainers take no responsibility for completeness, accuracy or fitness of any output; always verify critical legal citations against the official databases.
