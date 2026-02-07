# hwb96.github.io

个人主页源码，当前使用 **Jekyll（AcademicPages / Minimal Mistakes fork）** 构建，并通过 GitHub Pages 自动部署。

## 本地预览（macOS）

说明：macOS 自带的系统 Ruby 通常版本较老，建议使用 Homebrew 的 Ruby（本文以 `ruby@3.2` 为例）。

1. 安装 Ruby

```bash
brew install ruby@3.2
```

2. 安装依赖

```bash
/opt/homebrew/opt/ruby@3.2/bin/bundle install
```

3. 启动开发服务器

```bash
/opt/homebrew/opt/ruby@3.2/bin/bundle exec jekyll serve --livereload --host 127.0.0.1 --port 4000
```

浏览器访问 `http://127.0.0.1:4000/`。

如果端口占用，把 `--port 4000` 改成 `--port 4001`（或其它端口）。

## 本地构建

```bash
/opt/homebrew/opt/ruby@3.2/bin/bundle exec jekyll build
```

构建产物输出到 `_site/`。

## 回归脚本（可选）

```bash
./scripts/test_blog_titles_only.sh
./scripts/test_public_profile_privacy.sh
```

## 写文章

在 `_posts/` 下新增 `YYYY-MM-DD-slug.md`，使用 YAML Front Matter，例如：

```yaml
---
title: "文章标题"
date: 2026-02-07
tags: [llm, agent]
---
```

文章中的图片建议放在 `images/`。

## 备注

仓库中保留了一些历史 Hugo 文件（例如 `content/`、`static/`、`hugo.toml` 等），但当前本地预览与 GitHub Pages 构建以 Jekyll 为准。
