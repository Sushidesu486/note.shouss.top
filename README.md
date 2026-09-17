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

## 写作语法

正文使用 Markdown，扩展配置见 `mkdocs.yml` 的 `markdown_extensions`。常用写法：

| 效果 | 写法 | 备注 |
| --- | --- | --- |
| 加粗 | `**text**` 或 `<strong>text</strong>` | |
| 斜体 | `*text*` 或 `<em>text</em>` | |
| 下划线 | `<u>text</u>` 或 `<ins>text</ins>` | `++text++` 未启用 |
| 删除线 | `<s>text</s>` 或 `<del>text</del>` | `~~text~~` 未启用 |
| 高亮 | `<mark>text</mark>` | `==text==` 未启用 |
| 上下标 | `x<sup>2</sup>`、`x<sub>i</sub>` | `^2^`、`~i~` 未启用 |
| 键盘按键 | `<kbd>Ctrl</kbd>` | |
| 行内代码 | `` `code` `` | |
| 数学公式 | 行内 `$...$`，独立公式 `$$...$$` | arithmatex + MathJax |
| 提示块 | `!!! tip "标题"`，内容缩进四格 | 可折叠用 `??? tip "标题"` |
| 选项卡 | `=== "Tab 名"`，内容缩进四格 | |
| 脚注 | 正文 `[^1]`，另起 `[^1]: 说明` | |
| Mermaid 图 | ` ```mermaid ` 围栏 | |

下划线、删除线、高亮等没有对应的 Markdown 内建语法，`pymdownx.caret`、`pymdownx.tilde`、`pymdownx.mark` 未启用，因此统一使用原生 HTML 标签（Material 主题自带这些标签的样式）。注意 `<bf>`、`<rm>` 不是有效 HTML 标签，浏览器会忽略并渲染为普通文本，不要使用；Markdown 正文本身就是正体（roman），无需专门标记。

### 插入图片

- 图片放在 `docs/assets/`（全站共享，如 `docs/assets/video_generation/`）或课程目录自己的 `assets/`（如 `docs/zju/theory_of_computation/assets/`），课件、教材 PDF 等附件同理。站内引用一律用相对当前 `.md` 文件的路径。
- 普通插图用 Markdown 语法；需要控制尺寸或对齐时附加属性（`attr_list` 已启用）：

  ```markdown
  ![示意图](../assets/foo.png){ width="360" }
  ```

- 论文截图、需要图注和点击放大的插图，统一使用 `paper-figure` 结构（点击弹窗由 `docs/javascripts/reading.js` 实现，仅对该结构生效）：

  ```markdown
  <figure class="paper-figure" markdown>
  [![图示内容简述](../../assets/video_generation/fig1.png)](../../assets/video_generation/fig1.png)
  <figcaption markdown="span">图注：出处、页码与原文链接。</figcaption>
  </figure>
  ```

  `<figure>` 里的图片写成 `[![替代文字](图片路径)](图片路径)`（图片本身链接到原图），`<figcaption>` 内可再嵌 Markdown 链接；竖版图在 `class` 上追加 `portrait`，限制最大宽度 360px。

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
