#!/usr/bin/env python3
"""财政法规管理系统 fgk.mof.gov.cn 检索工具。"""
import json
import sys
import time

sys.path.insert(0, r'E:\ai_coding_xiangmu\China_Law\work\scripts')
import gov_download as gd

SEARCH = 'http://fgk.mof.gov.cn/dev/lawFile/searchLawFile'
FILEGET = 'http://fgk.mof.gov.cn/file/f/get'


def search(s, kw, size=30, current=1, retries=3):
    body = {"queryMap": {"lfgcc": "", "lkeyword": kw, "searchContent": kw,
                         "linvalid": "0"},
            "size": size, "current": str(current)}
    for i in range(retries):
        try:
            r = s.post(SEARCH, json=body, timeout=25)
            j = r.json()
            return (j.get('data') or {}).get('records') or [], (j.get('data') or {}).get('total')
        except Exception as e:
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(1 + i)
    return [], 0


def get_files(s, info_id):
    r = s.get(FILEGET, params={'infoId': info_id, 'fileType': '90'}, timeout=25)
    j = r.json()
    return j.get('data') or []


if __name__ == '__main__':
    s = gd.make_session()
    kws = sys.argv[1:]
    for kw in kws:
        recs, total = search(s, kw)
        print(f"== {kw} (total {total})")
        for rec in recs:
            t = rec.get('title') or ''
            print(f"  {rec.get('id')} | {t[:60]} | {rec.get('wh')} | {rec.get('lBuDate')}")
        time.sleep(0.5)
