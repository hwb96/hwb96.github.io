#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -n "${BUNDLE:-}" ]]; then
  BUNDLE_CMD="$BUNDLE"
elif [[ -x "/opt/homebrew/opt/ruby@3.2/bin/bundle" ]]; then
  BUNDLE_CMD="/opt/homebrew/opt/ruby@3.2/bin/bundle"
else
  BUNDLE_CMD="bundle"
fi

"$BUNDLE_CMD" exec jekyll build >/dev/null

BLOG_HTML="$ROOT_DIR/_site/blog/index.html"
if [[ ! -f "$BLOG_HTML" ]]; then
  echo "FAIL: 未找到 $BLOG_HTML（Jekyll build 未生成 blog 页面？）" >&2
  exit 1
fi

# 期望 blog 列表页仅显示标题；不应出现 excerpt / 日期等额外内容。
if grep -q "archive__item-excerpt" "$BLOG_HTML"; then
  echo "FAIL: blog 列表页仍包含摘要（archive__item-excerpt）" >&2
  exit 1
fi
if grep -q "page__date" "$BLOG_HTML"; then
  echo "FAIL: blog 列表页仍包含日期（page__date）" >&2
  exit 1
fi

echo "PASS: blog 列表页已是纯标题列表"

