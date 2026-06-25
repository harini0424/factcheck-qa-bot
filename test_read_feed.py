import json

with open("sample_posts.json", "r") as f:
    posts = json.load(f)

for post in posts:
    print(f"[{post['id']}] {post['author']}: {post['text']}")