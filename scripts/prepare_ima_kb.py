#!/usr/bin/env python3
"""
把 Serenity 5,857 条推文切分整理成适合 ima 知识库的 markdown 文档。

切分策略：
  - 按月切分（2025-07 → 2026-06，共 12 个月）
  - 每个月分原创 / 转发
  - 文件大小控制在 < 60 KB（ima 友好）
  - 顶部加 YAML frontmatter（topic / period / source）
  - 每条推文带 URL + 时间 + 互动数据
"""
import json
import os
import re
from collections import defaultdict, Counter
from pathlib import Path

INPUT = '/Users/popoya/Documents/serenity-aleabitoreddit/data/aleabitoreddit_tweets.json'
OUTPUT_DIR = Path('/Users/popoya/Documents/serenity-aleabitoreddit/ima_kb')

# ticker regex
TICKER_RE = re.compile(r'\$([A-Z]{1,6})')

# 单条推文 → markdown
def render_tweet_md(t):
    text = (t.get('text') or '').strip()
    iso = t.get('createdAtISO', '')
    date_str = iso[:10] if iso else ''
    time_str = iso[11:16] if iso else ''
    metrics = fmt_metrics(t.get('metrics') or {})
    tweet_id = t.get('id', '')
    url = f'https://x.com/aleabitoreddit/status/{tweet_id}' if tweet_id else ''
    tickers = extract_tickers(text)
    ticker_str = ' '.join(f'`${tk}`' for tk in tickers)

    lines = []
    if tickers:
        lines.append(f'**Ticker**: {ticker_str}  ')
    lines.append(f'**时间**: {date_str} {time_str} UTC  ')
    if metrics:
        lines.append(f'**互动**: {metrics}  ')
    if url:
        lines.append(f'**链接**: <{url}>  ')
    lines.append('')
    lines.append(text)
    return '\n'.join(lines)

# 时间解析
def parse_time(t):
    iso = t.get('createdAtISO')
    if iso:
        return iso[:10], iso[:7]  # date, month
    return None, None

def extract_tickers(text):
    return list(set(TICKER_RE.findall(text or '')))

def safe_num(v, default=0):
    return v if isinstance(v, (int, float)) else default

def fmt_metrics(m):
    if not m:
        return ''
    parts = []
    if safe_num(m.get('likes')): parts.append(f"❤{safe_num(m.get('likes'))}")
    if safe_num(m.get('retweets')): parts.append(f"🔁{safe_num(m.get('retweets'))}")
    if safe_num(m.get('replies')): parts.append(f"💬{safe_num(m.get('replies'))}")
    if safe_num(m.get('views')): parts.append(f"👁{safe_num(m.get('views'))}")
    return ' '.join(parts)

# 读数据
with open(INPUT) as f:
    data = json.load(f)
tweets = data if isinstance(data, list) else data.get('tweets', [])

print(f'总推文: {len(tweets)}')

# 按月份分桶
by_month = defaultdict(lambda: {'original': [], 'retweet': []})
for t in tweets:
    date, month = parse_time(t)
    if not month:
        continue
    bucket = 'retweet' if t.get('isRetweet') else 'original'
    by_month[month][bucket].append(t)

# 排序
for month in by_month:
    for kind in by_month[month]:
        by_month[month][kind].sort(key=lambda x: x.get('createdAtISO', ''))

# 输出
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
manifest = []
MAX_BYTES = 60 * 1024  # 60 KB

for month in sorted(by_month.keys()):
    for kind in ['original', 'retweet']:
        items = by_month[month][kind]
        if not items:
            continue
        # 切片
        chunks = []
        cur = []
        cur_size = 0
        for t in items:
            block = render_tweet_md(t)
            block_size = len(block.encode('utf-8'))
            if cur and cur_size + block_size > MAX_BYTES:
                chunks.append(cur)
                cur = []
                cur_size = 0
            cur.append(t)
            cur_size += block_size
        if cur:
            chunks.append(cur)

        kind_zh = '原创' if kind == 'original' else '转发'
        for idx, chunk in enumerate(chunks):
            suffix = f'_part{idx+1}' if len(chunks) > 1 else ''
            fname = f'serenity_{month}_{kind}{suffix}.md'
            fpath = OUTPUT_DIR / fname

            # 统计 ticker
            tickers = Counter()
            for t in chunk:
                for tk in extract_tickers(t.get('text', '')):
                    tickers[tk] += 1
            top_tickers = ', '.join(f'${tk}' for tk, _ in tickers.most_common(15)) or '无 $ticker'

            # 统计互动
            total_views = sum(safe_num((t.get('metrics') or {}).get('views')) for t in chunk)
            total_likes = sum(safe_num((t.get('metrics') or {}).get('likes')) for t in chunk)

            with open(fpath, 'w', encoding='utf-8') as f:
                # frontmatter
                f.write('---\n')
                f.write(f'topic: Serenity 推文归档 - {month} {kind_zh}\n')
                f.write(f'subject: AI/半导体供应链投资观点\n')
                f.write(f'period: {month}\n')
                f.write(f'source: @aleabitoreddit (X/Twitter)\n')
                f.write(f'tweet_count: {len(chunk)}\n')
                f.write(f'top_tickers: {top_tickers}\n')
                f.write(f'total_views: {total_views}\n')
                f.write(f'total_likes: {total_likes}\n')
                f.write('---\n\n')

                f.write(f'# Serenity 推文 · {month} · {kind_zh}（{idx+1}/{len(chunks)}）\n\n')
                f.write(f'> 来源：X @aleabitoreddit（AI/半导体供应链分析师）\n')
                f.write(f'> 时间范围：{chunk[0].get("createdAtISO", "")[:10]} → {chunk[-1].get("createdAtISO", "")[:10]}\n')
                f.write(f'> 本文件含 **{len(chunk)} 条**推文\n\n')
                if top_tickers != '无 $ticker':
                    f.write(f'**主要 ticker**: {top_tickers}\n\n')
                f.write('---\n\n')

                for t in chunk:
                    f.write(render_tweet_md(t))
                    f.write('\n---\n\n')

            manifest.append({
                'file': fname,
                'month': month,
                'kind': kind_zh,
                'count': len(chunk),
                'tickers': [tk for tk, _ in tickers.most_common(10)],
                'size_kb': round(fpath.stat().st_size / 1024, 1)
            })
            print(f'  ✓ {fname} ({len(chunk)} 条, {round(fpath.stat().st_size/1024, 1)} KB)')

# 写清单
with open(OUTPUT_DIR / 'MANIFEST.md', 'w', encoding='utf-8') as f:
    f.write('# Serenity 推文归档 · 导入清单\n\n')
    f.write(f'> 自动生成，共 {len(manifest)} 个 markdown 文件，总计 {sum(m["count"] for m in manifest)} 条推文\n\n')
    f.write('## 使用方法\n\n')
    f.write('1. 在 ima.copilot 客户端打开「知识库」\n')
    f.write('2. 新建知识库，命名「Serenity 推文归档」\n')
    f.write('3. 把 `ima_kb/` 目录下所有 `.md` 文件**整批拖入**（支持多文件导入）\n')
    f.write('4. 等待 ima 索引完成（5,857 条推文通常需要 5-15 分钟）\n')
    f.write('5. 索引完成后可以问：\n')
    f.write('   - 「Serenity 怎么看 CPO/光模块？」\n')
    f.write('   - 「2025年10月他最看多哪个标的？」\n')
    f.write('   - 「他为什么看好 $AAOI？」\n\n')
    f.write('---\n\n## 文件清单\n\n')
    f.write('| 文件 | 月份 | 类型 | 推文数 | 大小 | 主要 ticker |\n')
    f.write('|---|---|---|---|---|---|\n')
    for m in manifest:
        tickers = ', '.join(f'${tk}' for tk in m['tickers'][:5]) or '—'
        f.write(f'| `{m["file"]}` | {m["month"]} | {m["kind"]} | {m["count"]} | {m["size_kb"]} KB | {tickers} |\n')

print(f'\n✅ 完成！{len(manifest)} 个文件已生成到 {OUTPUT_DIR}')
print(f'清单: {OUTPUT_DIR}/MANIFEST.md')