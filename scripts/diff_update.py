#!/usr/bin/env python3
# ============================================================
# Copyright (c) 2026 Zhu-Guang-Scion <Zhu-Guang-Scion@users.noreply.github.com>
# China_Law 法规库与税务案例库工具链 · github.com/Zhu-Guang-Scion · 水印 CLAW-ZGS-2026
# MIT License（见仓库 LICENSE）；数据不入库，仅元数据索引
# ============================================================
"""增量更新 diff：对比新旧清单，输出 新增/消失/变更 件列表。

用法:
  python diff_update.py <旧lists目录> <新lists目录> [输出目录]

对比 flk_*.jsonl（键=bbbs）与 gov_*.jsonl（键=url）：
- new.jsonl     新清单有、旧清单无（新增法规，待下载）
- removed.jsonl 旧清单有、新清单无（可能废止/被新版替换，人工核查）
- changed.jsonl 同键但 标题/公布日期/时效 变化
"""

__author__ = "Zhu-Guang-Scion"
__copyright__ = "Copyright (c) 2026 Zhu-Guang-Scion (github.com/Zhu-Guang-Scion), MIT"
import json
import os
import sys

KEYS = {"flk": "bbbs", "gov": "url"}


def load_all(lists_dir):
    data = {}
    for fn in os.listdir(lists_dir):
        if not fn.endswith(".jsonl") or ("_dl_progress" in fn):
            continue
        kind = "flk" if fn.startswith("flk_") else ("gov" if fn.startswith("gov_") else None)
        if not kind:
            continue
        key = KEYS[kind]
        for line in open(os.path.join(lists_dir, fn), encoding="utf-8"):
            line = line.strip()
            if line:
                rec = json.loads(line)
                data[(kind, rec[key])] = rec
    return data


def main():
    old_dir, new_dir = sys.argv[1], sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    old = load_all(old_dir)
    new = load_all(new_dir)
    old_keys, new_keys = set(old), set(new)

    added = [new[k] for k in sorted(new_keys - old_keys)]
    removed = [old[k] for k in sorted(old_keys - new_keys)]
    changed = []
    for k in sorted(old_keys & new_keys):
        a, b = old[k], new[k]
        if (a.get("title"), a.get("gbrq") or a.get("date"), a.get("sxx")) != \
           (b.get("title"), b.get("gbrq") or b.get("date"), b.get("sxx")):
            changed.append({"old": a, "new": b})

    for name, rows in [("new.jsonl", added), ("removed.jsonl", removed), ("changed.jsonl", changed)]:
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"新增 {len(added)} | 消失 {len(removed)} | 变更 {len(changed)} -> {out_dir}/{{new,removed,changed}}.jsonl")


if __name__ == "__main__":
    main()
