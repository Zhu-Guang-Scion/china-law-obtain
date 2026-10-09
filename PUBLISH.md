# 发布操作清单（Push 前后逐步执行）

> 本文件是给仓库维护者的操作指引，推送前可删除或保留。

## 1. 推送前（必做）

- [x] 敏感信息剥离：MinerU token 已改环境变量、本机路径已通用化（终审 agent 复核）
- [x] `__pycache__`、被取代脚本（gap_fetch.py）、任何数据文件均不在仓库内
- [x] .gitignore 覆盖 lawlibrary/ work/ lists/ 等（防误提交下载产物）
- [ ] **吊销曾硬编码过的 3 个 MinerU token**（在 https://mineru.net/apiManage/token 逐个删除重建）——它们出现在过本地会话与源 skill 历史中，虽从未进入本仓库 git 历史，吊销最稳妥
- [ ] 通读 docs/RESPONSIBLE_USE.md 一遍确认表述

## 2. 初始化与推送

```bash
cd <本仓库目录 china-law-aque>
git init -b main
git add -A
git status   # 确认只有 25 个左右文本文件，无任何 docx/pdf/jsonl
git commit -m "china-law-aque: full pipeline for acquiring China's current-effective laws & regulations"
# 在 GitHub 建仓后:
git remote add origin git@github.com:<user>/china-law-aque.git
git push -u origin main
```

## 3. 推送后建议

- 加 topics: `china` `law` `legal-data` `open-data` `scraper` `ocr`（自由选择）
- README 徽章（可选）: License MIT
- 若收到源站或平台合规询问，依据 docs/RESPONSIBLE_USE.md 的定位回应（公开领域数据、限速礼貌抓取、无登录/付费墙绕过）
