# Deep Imaging Group 主页维护说明

这个仓库是实验室主页的静态网站，部署到 GitHub Pages 后直接访问 HTML、CSS、图片和 JSON 数据。日常维护主要改 JSON 和图片，除非需要调整页面样式或交互，一般不需要改 HTML。

## 本地预览

在仓库根目录运行：

```bash
python3 -m http.server 8000
```

然后打开：

```text
http://127.0.0.1:8000/
```

重点检查：

- 首页：News、Research Highlight、团队合照轮播是否正常。
- Members：成员图片、姓名、邮箱、时间、描述是否正常。
- Publication：年份、Journal、Conference、paper/code 链接是否正常。
- 浏览器控制台是否有 JSON 或图片加载错误。

## 数据目录总览

```text
news/                    首页 News 数据
highlight/               首页 Research Highlight 数据和图片
gallery/                 首页团队合照数据和图片
members/                 Members 页面数据和成员图片
publications/            Publication 页面正式论文数据
py_script/               辅助脚本，当前主要用于 BibTeX 转论文候选 JSON
```

注意：GitHub Pages 对文件名大小写敏感，JSON 中写的图片路径必须和真实文件名完全一致。

## News 更新

首页 News 从这里读取：

```text
news/index.json
news/<year>/<month>.json
```

`news/index.json` 控制读取哪些月份：

```json
[
  {
    "year": "2026",
    "month": "06",
    "file": "./news/2026/06.json"
  }
]
```

每个月的 JSON 是一个字符串数组，一条字符串就是一条 news：

```json
[
  "One paper was accepted by AAAI 2026.",
  "Our group released a new project."
]
```

新增 news 时：

1. 如果月份文件不存在，新建 `news/<year>/<month>.json`。
2. 把新消息加入该月份数组。
3. 如果是新月份，把对应条目加入 `news/index.json`。

## Research Highlight 更新

首页 Research Highlight 从这里读取：

```text
highlight/highlights.json
highlight/highlight_images/
```

每条 highlight 的格式：

```json
{
  "title": "Paper Title",
  "author": "First Author et al.",
  "year": "2026",
  "venue": "AAAI",
  "image": "./highlight/highlight_images/example.webp",
  "paper": "https://example.com/paper",
  "code": "https://github.com/example/code"
}
```

字段说明：

- `title`：论文标题。
- `author`：首页展示用作者，建议使用 `First Author et al.`。
- `year`：年份，字符串或数字都可以，建议统一写字符串。
- `venue`：会议或期刊简称，例如 `AAAI`、`ICLR`、`CVPR`。
- `image`：配图路径。
- `paper`：论文链接，没有就留空字符串。
- `code`：代码链接，没有就留空字符串。

新增 highlight 时：

1. 把图片放到 `highlight/highlight_images/`。
2. 在 `highlight/highlights.json` 里新增一条记录。
3. 检查图片能否正常显示，paper/code 按钮是否正常。

## Gallery 更新

首页左侧团队合照从这里读取：

```text
gallery/gallery.json
gallery/gallery_images/
```

每条 gallery 的格式：

```json
{
  "image": "./gallery/gallery_images/group1.webp",
  "alt": "Deep Imaging Group photo 1"
}
```

新增团队合照时：

1. 把图片放到 `gallery/gallery_images/`。
2. 在 `gallery/gallery.json` 里新增一条记录。
3. 建议使用 `.webp`，图片尺寸不要过大，否则 GitHub Pages 首屏加载会变慢。

## Members 更新

成员页从这里读取：

```text
members/members.json
members/member_images/
```

当前分类包括：

```json
{
  "professors": [],
  "post_docs": [],
  "phd_students": [],
  "ms_students": [],
  "undergraduate_students": [],
  "alumni": []
}
```

每个成员的格式：

```json
{
  "image": "./members/member_images/example.webp",
  "name": "Name (中文名)",
  "email": "name@example.com",
  "period": "(Fall 2026 - )",
  "description": "Ph.D.; Current: Example University",
  "link": "https://example.com"
}
```

字段说明：

- `image`：成员照片路径。没有照片可以留空，会使用默认图。
- `name`：展示姓名。
- `email`：邮箱，没有就留空字符串。
- `period`：在读或在组时间。
- `description`：浅色说明文字，例如身份、方向、毕业去向。
- `link`：个人主页或 Google Scholar，没有就留空字符串。

新增成员时：

1. 把照片放到 `members/member_images/`。
2. 在 `members/members.json` 的对应分类中新增记录。
3. 图片建议裁成接近正方形，使用 `.webp` 优先。

## Publications 更新

论文页正式数据从这里读取：

```text
publications/index.json
publications/<year>.json
```

`publications/index.json` 控制显示哪些年份，以及默认展开哪一年：

```json
{
  "years": [
    {
      "year": 2026,
      "active": true
    },
    {
      "year": 2025,
      "active": false
    }
  ]
}
```

每一年的论文放在一个年度 JSON 中：

```json
{
  "journal": [],
  "conference": []
}
```

单篇论文格式：

```json
{
  "title": "Paper Title",
  "authors": "A Author, B Author, Hu Chen",
  "year": 2026,
  "type": "conference",
  "venue": "Proceedings of the Example Conference 2026",
  "paper": "https://example.com/paper",
  "code": "",
  "order": 1
}
```

字段说明：

- `title`：论文标题。
- `authors`：作者列表。
- `year`：发表年份。
- `type`：只能写 `journal` 或 `conference`。
- `venue`：期刊或会议名称。
- `paper`：论文链接。
- `code`：代码链接，没有就留空字符串。
- `order`：同一年同一类别内的显示顺序，数字越小越靠前。

### BibTeX 转候选 JSON

如果有多篇论文的 BibTeX，可以先放到：

```text
py_script/candidate.bib
```

然后运行：

```bash
python3 py_script/bib_to_temp_publications.py
```

脚本会生成候选文件：

```text
py_script/temp-pub-raw/<year>.json
```

人工检查无误后，再把候选 JSON 中的论文复制到正式的 `publications/<year>.json`。如果是新年份，还要手动更新 `publications/index.json`。

更详细的论文维护流程见：

```text
py_script/PUBLICATION_WORKFLOW.md
```

## JSON 检查

JSON 文件不能有尾逗号，字符串必须使用双引号。改完后可以用 Python 快速检查：

```bash
python3 -m json.tool highlight/highlights.json
python3 -m json.tool gallery/gallery.json
python3 -m json.tool members/members.json
python3 -m json.tool publications/2025.json
```

也可以检查某个目录下所有 JSON：

```bash
find news highlight gallery members publications -name "*.json" -print -exec python3 -m json.tool {} /tmp/json-check.out \;
```

如果命令没有报错，说明 JSON 格式基本正确。

## 图片建议

- 首页首屏图片尽量使用 `.webp`。
- 单张图片建议控制在 300 KB 到 800 KB 内，特别大的图片会拖慢 GitHub Pages 首屏加载。
- 成员头像建议接近正方形。
- highlight 配图建议主体居中，避免文字或关键图形贴边。
- 路径建议只使用英文、数字、空格、横线或下划线，避免特殊符号。

## GitHub Pages 常见问题

- 本地正常、线上不正常，优先检查路径大小写是否完全一致。
- JSON 改了但线上没有立刻变化，可能是浏览器或 GitHub Pages 缓存，稍等一两分钟后强制刷新。
- CSS 或 JavaScript 改了但线上仍是旧效果，可以更新 HTML 中的版本号，例如 `css/style.css?v=20260626`。
- 新增文件后记得确认已经 `git add`，否则本地能看到，线上不会部署。

## 发布流程

常规流程：

```bash
git status
git add .
git commit -m "Update website data"
git push
```

推送后等待 GitHub Pages 部署完成，再打开线上页面检查。
