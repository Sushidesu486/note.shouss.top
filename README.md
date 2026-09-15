# note.shouss.top

个人学习笔记站点，使用 MkDocs Material 构建，通过 GitHub Actions 自动部署。

## 地址

[note.shouss.top](https://note.shouss.top)

## 目录

- `docs/index.md`：站点首页。
- `docs/cmu_15_445/`：CMU 数据库课程。
- `docs/zju/`：ZJU 课程，各课程有独立的 `index.md`。
- `docs/research/`：研究专题。
- `docs/assets/`、`docs/stylesheets/`、`docs/javascripts/`：图片、样式和交互脚本。
- `mkdocs.yml`：导航、主题、扩展和链接检查配置。
- `tools/`：页面检查与论文插图提取工具。
- `site/`：生成目录，不直接编辑或提交。

## 本地预览

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

访问 http://127.0.0.1:8000

CI 使用 Python 3.12；构建依赖及中文分词依赖统一在 `requirements.txt` 中固定版本。

## 添加页面

1. 在对应栏目下新建小写 `snake_case.md` 文件。
2. 在 `mkdocs.yml` 的 `nav` 和栏目 `index.md` 中添加入口。
3. 站内链接使用相对 `.md` 路径，附件使用相对文件路径；保留已有页面 URL。
4. 正文优先使用 Markdown。学习路线使用 Markdown 有序列表，外面仅保留 `<div class="study-route" markdown="block">` 容器以应用样式；只在容器、交互组件或语义化图注确有需要时嵌入 HTML。

公开的辅助页面若有意不进入菜单，使用 MkDocs 的 `not_in_nav` 显式列出；不发布的草稿使用 `draft_docs`，不要仅从导航移除。

## 检查与发布

```bash
python -m mkdocs build --strict
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

在一个终端预览构建产物：

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory site
```

在另一个已激活虚拟环境的终端执行：

```bash
python tools/check_reading_site.py --output /tmp/notes-site-qa
```

检查覆盖所有生成页面的桌面与手机布局、图片、公式、站内链接和锚点，并验证栏目入口、学习路线、中文与英文搜索、计算器、图片弹窗和暗色模式。报告与截图保存在输出目录；可通过 `--base-url` 指定预览地址，通过 `--site-dir` 指定构建目录。

PR 和 main 推送都会运行严格构建与页面检查，只有 main 检查通过后才部署 GitHub Pages。GitHub Actions 的 `site-qa` artifact 包含报告与截图。更新依赖时同步修改版本并重新运行上述检查。

MathJax 和 Mermaid 的浏览器资源固定到具体版本，仍需联网访问 unpkg；构建成功并不代表这些资源在所有访问网络中都可用。

## 论文插图工具

`tools/extract_paper_figures.py` 从本地论文 PDF 提取指定区域，并生成带论文版本、页码和校验值的清单。调用方式和输入目录要求见脚本开头；它不是日常构建依赖。
