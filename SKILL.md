---
name: china-law-aque
description: 中国大陆现行法律法规规章制度库的获取（aque=acquire）、下载、校验、整理与增量更新全流程工具。覆盖国家法律法规数据库(flk.npc.gov.cn)六类 + 国家规章库(gov.cn)两类，含网宿WAF应对、athenaappkey本地生成、多镜像加速、md转换与涉税/涉会计专题分类。触发词：法律法规下载、法规库更新、flk下载、规章库下载、法规转md、涉税法规、涉会计法规、law library、法规增量更新。
---

# china-law-aque — 中国法规库获取与更新全流程

> 本仓库只含代码与文档，不含任何下载的法规文件（见 docs/RESPONSIBLE_USE.md）。
> 工作目录约定：脚本通过环境变量 `CHINA_LAW_WORK` 或当前目录下的 `work/` 定位清单/下载/校验产物。

2026-10 实战验证的全量获取路径（28,000+ 件现行有效法规规章，含官方 docx 与 markdown 双格式）。
所有踩坑结论已固化在脚本里，**不要重新发明轮子，直接按下文流程走**。

## 数据源与关键结论（必读）

| 库 | 范围 | 接口 | 关键点 |
|---|---|---|---|
| 国家法律法规数据库 flk.npc.gov.cn | 宪法/法律/行政法规/监察法规/地方法规/司法解释（现行有效约 1.7 万件） | `POST /law-search/search/list`、`GET /law-search/download/pc` | ①分类必须用**叶子编码**（法律=110-170，地方性法规=230 等，见 flk_enumerate.py）②空关键词+分类码+sxx=[3] 可分页枚举全量，pageSize≤500 ③下载接口有**网宿WAF**：需 wzws_cid cookie（先 GET 首页；被挑战时用 playwright 真浏览器取 cookie，见 flk_cookie.py）④官方总量接口 `GET /law-search/index/aggregateData` 用于对账 |
| 国家规章库 gov.cn/zhengce/xxgk/gjgzk | 部门规章/地方政府规章（仅现行，约 1 万件） | `POST sousuoht.www.gov.cn/athena/forward/BD8730CDDA12515E2D9E1B21AA11C0D6` | **athenaappkey 可本地生成**（RSA公钥静态加密固定appid，govlib.py 内置，永不过期）。正文可从搜索接口 `f_202321758948` 字段直接拿（HTML 提取失败时的回退） |
| lawtext/legal-data-docx (GitHub) | flk 官方 docx 定期全量备份（3 万件，bbbs 索引+sha256） | raw.githubusercontent.com | GitHub 限速时走 **gh-proxy.com / ghproxy.net** 前缀加速；data-docx.jsonl 是 bbbs→路径→sha256 索引 |
| lawtext/regulations (GitHub) | 地方法规 markdown（bbbs 命名，1.7 万件） | git clone | md→docx 补齐地方法规缺口的快速路径 |
| HuggingFace twang2218/chinese-law-and-regulations | flk 2023-09 全量快照（parquet 含正文） | hf-mirror.com 直链 | 用于：数量交叉校验、扫描版 PDF 的文本回退 |

## 全新获取流程（首次建库）

```bash
# 0) 环境: python3.11+, pip install requests python-docx pycryptodome pymupdf playwright pyarrow pandas
SKILL=<本仓库>/scripts   # 或安装到 agent skill 目录后的对应路径
WORK=<你的工作目录> && cd $WORK && mkdir -p lists downloads/flk downloads/gov logs verify ../mirrors
# 注意: mirrors/ 与 lawlibrary/ 位于 work/ 的上一级（与 work 平级），不在 work/ 内

# 1) 枚举 flk 全量现行有效（约40页，1分钟）
python $SKILL/flk_enumerate.py                     # -> lists/flk_<类>.jsonl 共约1.7万条

# 2) 枚举规章库两类（athenaappkey 自动生成，无需浏览器）
python $SKILL/govlib.py                            # -> lists/gov_<类>.jsonl 共约1万条

# 3) 下载规章库（HTML→docx，含 API正文回退；断点续下）
python $SKILL/gov_download.py 部门规章 4
python $SKILL/gov_download.py 地方政府规章 5

# 4) 下载 flk 官方 docx（WAF 限制 ~5req/s；被挑战时先 python $SKILL/flk_cookie.py）
python $SKILL/flk_download.py 宪法 3
python $SKILL/flk_download.py 法律 3
python $SKILL/flk_download.py 行政法规 3
python $SKILL/flk_download.py 司法解释 3
python $SKILL/flk_download.py 地方法规 5            # 大头，1.5万件，配合镜像更快

# 5) 镜像补齐与升级（按优先级：官方API > lawtext官方docx > lawtext_md）
curl -sL -o ../mirrors/data-docx.jsonl https://raw.githubusercontent.com/lawtext/legal-data-docx/main/data-docx.jsonl
python $SKILL/gap_fetch_proxy.py                   # 按索引经gh-proxy精准抓缺口(sha256校验)
python $SKILL/mirror_fill.py                       # 本地镜像目录按bbbs复制补齐
git clone --depth 1 https://github.com/lawtext/regulations.git ../mirrors/regulations
python $SKILL/md_fill.py                           # 地方法规缺口 md→docx 兜底
python $SKILL/upgrade_fetch.py 5                   # md来源升级为官方docx(sha256校验)

# 6) 修复与转换
python $SKILL/gov_repair.py                        # 薄内容重提取/附件下载
python $SKILL/redoc.py                             # .doc老格式重取docx

# 7) 校验（对账/完整性/抽样/交叉）
python $SKILL/verify.py all                        # verify/ 下四份报告

# 8) 整理 + md + 涉税涉会计专题
python $SKILL/organize_md.py                       # -> lawlibrary/<库>/<类>/原文件|Markdown + 专题/ + manifest.csv
```

## 乱码/错码复检与修复

全量扫描 `python scripts/mojibake_scan.py`（md 全量；`--docx` 追加 3000 件抽样）+ 修复 `python scripts/moji_fix.py`。检测项与经验：
- **U+FFFD**：厦门系列 gov.cn 页面源站即含坏字节 → 用规章库 API 正文字段整体重建（moji_fix 已内置）
- **PUA U+E003/E004**（flk 老排版 docx 行尾空形符，~130件）与 E5D2/E5CF（公报装饰括号）：直接剥离，docx 逐 run 清洗后重建 md
- **锟斤拷**：检测必须查**序列**「锟斤拷」，不能数单字（公斤的斤、烫烫烫会误报）
- **控制字符**：剥离（保留 
	）
- 扫描 PDF/.doc 无文本层属正常（md 由 OCR 提供），勿当缺陷
- 修复顺序：API正文重建(规章库FFFD/锟斤拷) > docx run清洗+md重建 > 仅md清洗；专题副本最后从主库 md 同步

## 扫描版 PDF 的 md（MinerU OCR）

flk 有少量扫描版 PDF（无文本层，pymupdf 抽不出字）。三层策略：
1. 标题精确匹配 HuggingFace 2023 快照的 content 字段（organize_md.py 的 fallback_content）
2. **MinerU OCR**（对官方扫描件直接识别，provenance 最佳）：`mineru-open-api extract <pdf> -o <dir> -f md --model pipeline --language ch`，需 MINERU_TOKEN（支持配置多个 token 分担配额）；文件名尾部不能带下划线（`_.pdf` 会被 API 判 unsupported file type，先复制成干净临时名）
3. 质量校验后再替换：OCR 中文字数/第X条数 与快照文本量级相当（0.55~1.8倍、条数差≤3 或 OCR 更多）才采纳，否则保留快照版 —— 见 `mineru_upgrade.py`（含 token 轮换、断点、校验、manifest/专题同步）

模型选择：法律文本用 `pipeline`（无幻觉），不用 vlm。

## 辅助工具

- `waf_watch.py`：长跑下载时看护 WAF 状态、自动续传
- `diff_update.py <旧lists> <新lists> [输出]`：增量对账（新增/消失/变更）

## 增量更新流程（后续维护）

```bash
# 1) 重新枚举（生成新清单）
python $SKILL/flk_enumerate.py && python $SKILL/govlib.py
# 2) 与旧清单 diff（bbbs/url 集合差）——新增件走下载，消失件标记核查（可能已废止/修订）
# 3) 只下载新增：flk_download/gov_download 自动跳过进度ok的旧件
# 4) 重新校验+整理（organize_md 按 标题_日期 命名，已存在即跳过；manifest 全量重建）
python $SKILL/verify.py counts && python $SKILL/organize_md.py
```

注意：flk 的 bbbs 对同一法规每次修订是**不同 bbbs**；判断"同一部法规的新版本"用 标题+施行日期。
废止检测：旧 bbbs 的 sxx 会从 3 变 1/2 —— 对账时用 aggregateData 与清单 diff。

## 校验体系（四层）

1. **数量对账** `verify.py counts`：枚举数 vs aggregateData 官方数 vs 磁盘文件数 vs 进度ok数（允许镜像 dup 时文件数>条目数）
2. **完整性** `verify.py integrity`：docx=有效ZIP含document.xml、pdf=%PDF头、大小阈值
3. **抽样** `verify.py sample`：标题命中/中文字数/第X条结构（注意：批复/修正案天然短小，规则已放宽）
4. **交叉** `verify.py cross`：LawRefBook条数比对（镜像版本可能滞后）、HF快照标题集合比对（差异应可被 立法事件 解释）、lawtext bbbs覆盖率

## 已知坑（全部踩过，勿重复）

- flk 分类用顶级码(101/201/221/311)查到 0 条 —— 必须**叶子码**
- flk 空关键词必须配合分类码才有效；`sxx:[3]`=现行有效
- flk 网宿WAF：burst 后返回 JS 挑战页(HTML)；对策=flk_cookie.py 用 playwright 取 cookie（playwright 装法：`python -m pip install playwright && python -m playwright install chromium`）
- 规章库部分 doc_pub_url 指向**地方政府官网**（非 gov.cn），页面结构各异 → extract_body_generic 通用提取 + API 正文字段回退
- 老页面正文可能是 PDF 附件（`files/*.pdf`）→ gov_repair.py 下载附件
- flk 有 24 件左右 2020-2021 司法解释官方只有**扫描版 PDF/旧 .doc** → md 用 HF parquet 回退（organize_md.py 已内置 content_fallback.json 逻辑）
- GitHub 直连限速 ~60KB/s → gh-proxy.com/ghproxy.net 前缀提速 10 倍+
- 规章库存在 ~26 组**同题同日不同URL**的重复条目（源库问题），一份文件服务两条记录
- 文件名长度：标题截 100 字符（Windows 长路径安全）

## 专题分类（organize_md.py）

- 涉税：税收/税务/增值税/消费税/企业所得税/个人所得税/关税/车船税/印花税/契税/土地增值税/房产税/资源税/环境保护税/耕地占用税/烟叶税/船舶吨税/车辆购置税/城市维护建设税/发票/出口退税/国际税收/涉税/税收征收管理
- 涉会计：会计/审计/注册会计师/总会计师/财务
- 关键词表在 organize_md.py 头部，可自行增删后重跑（幂等）

## 输出库结构

```
lawlibrary/
├── manifest.csv                    # 总清单: 库/类别/标题/机关/日期/专题/来源/原文件/Markdown/链接
├── 国家法律法规数据库/<类别>/{原文件,Markdown}/
├── 国家规章库/<部门规章|地方政府规章>/{原文件,Markdown}/
└── 专题/{涉税法规,涉会计法规}/<库>/<类别>/     # 原文件+md 双格式副本
```

md 带 front matter（title/库/类别/公布机关/公布日期/时效性/来源/原文链接），第X条加粗，表格转 markdown 表。

## 进度文件格式（断点续做）

- `lists/flk_dl_progress_<类>.jsonl`：每行 `{bbbs, ok, file, source?, bytes?, sha256_ok?}`，append-only，**最新一行为准**
- `lists/gov_dl_progress_<类>.jsonl`：同上，键为 url
- source 取值：官方API / lawtext（官方docx镜像）/ lawtext_md（md转的docx，可被升级）/ api_content（规章库API正文）/ gov.cn详情页
