# 论文数据维护流程

本文档说明当前主页 `Publication` 页面的论文数据维护方式。

注意：Google Scholar 自动抓取逻辑已经暂停。原因是 Google Scholar 容易触发反爬限制，结果不稳定。当前不要依赖爬虫生成论文数据。

## 1. 当前数据结构

正式网站先读取年份索引：

```text
publications/index.json
```

索引只负责控制显示哪些年份，以及哪一年默认展开：

```json
{
  "years": [
    {
      "year": 2025,
      "active": true
    },
    {
      "year": 2024,
      "active": false
    }
  ]
}
```

每一年的论文放在一个年度 JSON 中：

```text
publications/2025.json
publications/2024.json
```

年度 JSON 包含两个字段：`journal` 和 `conference`。它们分别是论文数组：

```json
{
  "journal": [
    {
      "title": "Paper Title",
      "authors": "A Author, B Author, Hu Chen",
      "year": 2025,
      "type": "journal",
      "venue": "IEEE Transactions on Medical Imaging",
      "paper": "https://example.com/paper",
      "code": "",
      "order": 1
    }
  ],
  "conference": []
}
```

## 2. 单篇论文字段

- `title`：论文标题。
- `authors`：作者列表，建议使用完整姓名，例如 `Hu Chen`。
- `year`：发表年份。
- `type`：只能使用 `journal` 或 `conference`。
- `venue`：期刊或会议名称。
- `paper`：论文链接。
- `code`：代码链接，没有就留空字符串。
- `order`：同一年同一类别内的显示顺序，数字越小越靠前。

## 3. 从 BibTeX 生成候选 JSON

把候选论文的 BibTeX 放到：

```text
py_script/candidate.bib
```

一个文件里可以放多篇论文，例如：

```bibtex
@article{example2026,
  title = {Example Paper Title},
  author = {First Author and Hu Chen and Yi Zhang},
  journal = {IEEE Transactions on Medical Imaging},
  year = {2026},
  url = {https://example.com/paper}
}

@inproceedings{exampleconf2026,
  title = {Example Conference Paper},
  author = {First Author and Second Author and Hu Chen},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year = {2026},
  doi = {10.0000/example}
}
```

然后运行：

```bash
python3 py_script/bib_to_temp_publications.py
```

脚本会生成候选年度 JSON：

```text
py_script/temp-pub-raw/2026.json
```

这个文件的结构和正式的 `publications/2026.json` 一致。人工审核后，把里面的论文复制到正式年度 JSON 的 `journal` 或 `conference` 数组中。

如果只想转换某一年：

```bash
python3 py_script/bib_to_temp_publications.py --year 2026
```

如果不想清空旧的候选年度 JSON：

```bash
python3 py_script/bib_to_temp_publications.py --no-clean
```

转换规则：

- `@article` 默认转成 `journal`。
- `@inproceedings` / `@conference` / `@proceedings` 默认转成 `conference`。
- `journal` 字段作为期刊名。
- `booktitle` 字段作为会议名。
- `url` 优先作为 `paper` 链接。
- 如果没有 `url`，但有 `doi`，会自动生成 `https://doi.org/<doi>`。
- `code` 默认留空，需要人工补充。
- 同一年同一类别内，按 BibTeX 中出现顺序生成 `order`。

## 4. 发布到正式数据

人工审核候选 JSON 后：

1. 如果是新年份，在 `publications/` 下新建 `publications/<year>.json`。
2. 把候选论文复制到对应年度 JSON 的 `journal` 或 `conference` 数组。
3. 手动维护 `order`。
4. 如果是新年份，把该年份加入 `publications/index.json`。

`publications/index.json` 需要手工维护，不再使用脚本自动重建。

## 5. Google Scholar 抓取已暂停

下面这个脚本目前只是禁用提示，不会访问网络，也不会生成 JSON：

```bash
python3 py_script/fetch_scholar_publications.py --year 2025
```

保留这个文件只是为了避免旧命令误执行真实爬虫逻辑。

## 6. 本地验证

启动本地静态服务器：

```bash
python3 -m http.server 8000
```

然后打开：

```text
http://127.0.0.1:8000/publication.html
```

检查内容：

- Journal 是否正常显示。
- Conference 是否正常显示。
- 年份折叠是否正常。
- paper/code 链接是否正常。
- 浏览器控制台是否有 JSON 加载错误。

验证完成后，可以用 `Ctrl+C` 停止本地服务器。

## 7. 提交和部署

确认无误后提交修改：

```bash
git add publications py_script publication.html css/style.css .gitignore
git commit -m "Update publications"
git push
```
