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

PAGE_INDEX="$ROOT_DIR/_site/index.html"
PAGE_CV="$ROOT_DIR/_site/cv/index.html"
PAGE_BLOG="$ROOT_DIR/_site/blog/index.html"

for f in "$PAGE_INDEX" "$PAGE_CV" "$PAGE_BLOG"; do
  if [[ ! -f "$f" ]]; then
    echo "FAIL: 未找到 $f（Jekyll build 未生成？）" >&2
    exit 1
  fi
done

# 这些关键词不应出现在公开页面中（按需追加）。
BANNED_PATTERNS=(
  "杭州泰格医药"
  "泰格"
  "泰雅"
  "中科大脑"
  "城市大脑"
  "金汇"
  "Hanwenbo_CV_20251215\\.pdf"
  "Hanwenbo_Resume_NLP\\.docx"
)

PAGES=("$PAGE_INDEX" "$PAGE_CV" "$PAGE_BLOG")

fail=0
for page in "${PAGES[@]}"; do
  for pat in "${BANNED_PATTERNS[@]}"; do
    if grep -E -n "$pat" "$page" >/dev/null 2>&1; then
      echo "FAIL: $page 包含不应公开的内容：$pat" >&2
      fail=1
    fi
  done
done

# 不展示 Publications 入口（导航/正文都不应出现）。
if grep -E -n "/publications/|>\\s*Publications\\s*<" "$PAGE_INDEX" "$PAGE_CV" "$PAGE_BLOG" >/dev/null 2>&1; then
  echo "FAIL: 公开页面仍包含 Publications 入口" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "PASS: 公开页面隐私检查通过"

