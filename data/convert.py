import json
import os
import html

# Define paths
json_path = "/Users/popoya/Documents/serenity-aleabitoreddit/data/aleabitoreddit_tweets.json"
txt_path = "/Users/popoya/Documents/serenity-aleabitoreddit/data/aleabitoreddit_tweets.txt"
html_path = "/Users/popoya/Documents/serenity-aleabitoreddit/data/aleabitoreddit_tweets.html"

def convert_tweets():
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    print("Reading JSON file...")
    with open(json_path, 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    print(f"Loaded {len(tweets)} tweets.")

    # 1. Export to TXT
    print("Exporting to TXT...")
    with open(txt_path, 'w', encoding='utf-8') as f_txt:
        f_txt.write(f"=== Serenity (@aleabitoreddit) Historical Tweets ===\n")
        f_txt.write(f"Total Tweets: {len(tweets)}\n")
        f_txt.write(f"Export Date: 2026-06-09\n")
        f_txt.write("=" * 60 + "\n\n")

        for i, tweet in enumerate(tweets, 1):
            created_at = tweet.get('createdAtLocal', tweet.get('createdAt', 'N/A'))
            text = tweet.get('text', '')
            metrics = tweet.get('metrics', {})
            likes = metrics.get('likes', 0)
            retweets = metrics.get('retweets', 0)
            replies = metrics.get('replies', 0)
            views = metrics.get('views', 0)

            f_txt.write(f"[{i}] 时间: {created_at}\n")
            f_txt.write(f"    数据: {likes} 点赞 | {retweets} 转发 | {replies} 回复 | {views} 阅读\n")
            f_txt.write(f"    内容: {text.strip()}\n")

            quoted = tweet.get('quotedTweet')
            if quoted:
                q_author = quoted.get('author', {}).get('screenName', 'unknown')
                q_text = quoted.get('text', '')
                f_txt.write(f"    [引用推文 @{q_author}]: {q_text.strip()}\n")
            
            media = tweet.get('media', [])
            if media:
                media_urls = [m.get('url') for m in media if m.get('url')]
                if media_urls:
                    f_txt.write(f"    媒体: {', '.join(media_urls)}\n")

            f_txt.write("-" * 50 + "\n\n")

    # 2. Export to HTML (for PDF printing)
    print("Exporting to HTML...")
    html_content = []
    html_content.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Serenity (@aleabitoreddit) 历史推文备份</title>
    <style>
        :root {
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --border-color: #e5e7eb;
            --accent-color: #1d9bf0;
            --quote-bg: #f3f4f6;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
        }

        h1 {
            margin: 0 0 10px 0;
            font-size: 28px;
            color: #111;
        }

        .meta-info {
            color: var(--text-muted);
            font-size: 14px;
        }

        .tweet-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            page-break-inside: avoid;
        }

        .tweet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 14px;
            color: var(--text-muted);
        }

        .tweet-index {
            font-weight: bold;
            color: var(--accent-color);
        }

        .tweet-date {
            font-family: monospace;
        }

        .tweet-text {
            font-size: 16px;
            white-space: pre-wrap;
            word-break: break-word;
            margin-bottom: 14px;
        }

        .quoted-card {
            background-color: var(--quote-bg);
            border-left: 4px solid var(--border-color);
            padding: 12px 16px;
            margin-top: 10px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
            font-size: 14px;
        }

        .quoted-author {
            font-weight: bold;
            margin-bottom: 4px;
            color: #333;
        }

        .tweet-media {
            margin-top: 12px;
        }

        .media-link {
            display: inline-block;
            margin-right: 10px;
            color: var(--accent-color);
            text-decoration: none;
            font-size: 13px;
        }

        .media-link:hover {
            text-decoration: underline;
        }

        .tweet-footer {
            margin-top: 15px;
            padding-top: 12px;
            border-top: 1px dashed var(--border-color);
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .metric-item span {
            font-weight: bold;
            color: var(--text-main);
        }

        @media print {
            body {
                background-color: #fff;
                padding: 0;
            }
            .tweet-card {
                border: 1px solid #ccc;
                box-shadow: none;
                page-break-inside: avoid;
                margin-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Serenity (@aleabitoreddit) 历史推文备份</h1>
            <div class="meta-info">
                <span>总计推文数量: """ + str(len(tweets)) + """ 条</span> &nbsp;|&nbsp;
                <span>生成日期: 2026-06-09</span>
            </div>
        </header>
        <div class="tweets-list">
""")

    for i, tweet in enumerate(tweets, 1):
        created_at = tweet.get('createdAtLocal', tweet.get('createdAt', 'N/A'))
        text = tweet.get('text', '')
        metrics = tweet.get('metrics', {})
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0)
        replies = metrics.get('replies', 0)
        views = metrics.get('views', 0)

        html_text = html.escape(text)
        # Simple URL link replacement for text
        # If there are links starting with http or https, make them clickable
        # (Very basic regex-like logic or keep plain text. Let's do simple escaping first)

        card_html = f"""
            <div class="tweet-card">
                <div class="tweet-header">
                    <span class="tweet-index">#{i}</span>
                    <span class="tweet-date">{created_at}</span>
                </div>
                <div class="tweet-text">{html_text}</div>
        """

        quoted = tweet.get('quotedTweet')
        if quoted:
            q_author = html.escape(quoted.get('author', {}).get('screenName', 'unknown'))
            q_text = html.escape(quoted.get('text', ''))
            card_html += f"""
                <div class="quoted-card">
                    <div class="quoted-author">@{q_author} 说道:</div>
                    <div>{q_text}</div>
                </div>
            """

        media = tweet.get('media', [])
        if media:
            card_html += '<div class="tweet-media">'
            for m in media:
                m_url = m.get('url')
                if m_url:
                    m_url_esc = html.escape(m_url)
                    card_html += f'<a class="media-link" href="{m_url_esc}" target="_blank">🖼️ 查看图片/媒体</a>'
            card_html += '</div>'

        card_html += f"""
                <div class="tweet-footer">
                    <div class="metric-item">👍 点赞 <span>{likes}</span></div>
                    <div class="metric-item">🔁 转发 <span>{retweets}</span></div>
                    <div class="metric-item">💬 回复 <span>{replies}</span></div>
                    <div class="metric-item">👁️ 阅读 <span>{views}</span></div>
                </div>
            </div>
        """
        html_content.append(card_html)

    html_content.append("""
        </div>
    </div>
</body>
</html>
""")

    with open(html_path, 'w', encoding='utf-8') as f_html:
        f_html.writelines(html_content)

    print("Successfully completed conversion!")
    print(f"TXT File: {txt_path}")
    print(f"HTML File: {html_path}")

if __name__ == "__main__":
    convert_tweets()
