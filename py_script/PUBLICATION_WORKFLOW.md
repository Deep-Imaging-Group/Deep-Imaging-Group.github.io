# 论文数据维护流程

本文档说明当前主页 `Publication` 页面的论文数据维护方式。

注意：Google Scholar 自动抓取逻辑已经暂停。原因是 Google Scholar 容易触发反爬限制，结果不稳定。当前不要依赖爬虫生成论文数据，等待后续再决定新的数据来源或半自动方案。

## 1. 当前数据结构

正式网站读取下面的索引文件：

```text
publications/index.json
```

索引里记录每一年、每一类论文对应的 JSON 文件路径。每篇论文单独保存为一个 JSON，例如：

```text
publications/2025/journal/example.json
publications/2025/conference/example.json
```

`publication.html` 会先读取 `publications/index.json`，再加载里面列出的每篇论文 JSON。

## 2. 单篇论文 JSON 格式

正式论文 JSON 推荐保持下面结构：

```json
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
```

字段说明：

- `title`：论文标题。
- `authors`：作者列表，建议使用完整姓名，例如 `Hu Chen`，不要写成 `H Chen`。
- `year`：发表年份。
- `type`：只能使用 `journal` 或 `conference`。
- `venue`：期刊或会议名称。
- `paper`：论文链接。
- `code`：代码链接，没有就留空字符串。
- `order`：同一年同一类别内的显示顺序，数字越小越靠前。

## 3. 临时审核目录

如果后续你手工整理了一批候选论文，但还不想直接放进正式目录，可以先放在：

```text
py_script/temp-pub-raw/<year>/<journal|conference>/
```

例如：

```text
py_script/temp-pub-raw/2026/conference/example.json
```

这里的文件不会被网站读取，只作为人工审核区。

审核重点：

- 论文名是否正确。
- 作者是否完整，尤其是 `Hu Chen` 等姓名是否写全。
- 年份是否正确。
- `type` 是否正确分为 `journal` 或 `conference`。
- 期刊/会议名称格式是否统一。
- `paper` 链接是否可打开。
- `code` 链接是否需要人工补充。
- `order` 是否符合想要的展示顺序。

## 4. 从 BibTeX 生成候选 JSON

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

脚本会生成：

```text
py_script/temp-pub-raw/<year>/<journal|conference>/*.json
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

如果不想清空旧的临时候选目录，可以运行：

```bash
python3 py_script/bib_to_temp_publications.py --no-clean
```

## 5. 发布到正式目录

审核无误后，把候选 JSON 复制到正式目录：

```text
publications/<year>/<journal|conference>/
```

例如：

```bash
cp py_script/temp-pub-raw/2026/conference/example.json publications/2026/conference/
```

然后运行脚本自动更新索引：

```bash
python3 py_script/build_publication_index.py
```

这个脚本会扫描 `publications/`，自动重建：

```text
publications/index.json
publications/<year>/<journal|conference>/index.json
```

默认会尽量保留原来哪一年展开的设置。如果没有旧设置，会默认展开最新年份。

如果想指定默认展开年份，例如 2026：

```bash
python3 py_script/build_publication_index.py --active-year 2026
```

如果只想预览将要生成的索引，不写入文件：

```bash
python3 py_script/build_publication_index.py --dry-run
```

## 6. Google Scholar 抓取已暂停

下面这个脚本目前只是禁用提示，不会访问网络，也不会生成 JSON：

```bash
python3 py_script/fetch_scholar_publications.py --year 2025
```

保留这个文件只是为了避免旧命令误执行真实爬虫逻辑。后续如果改用其他数据源，再重新设计这里的逻辑。

## 7. 本地验证

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

## 8. 提交和部署

确认无误后提交修改：

```bash
git add publications py_script publication.html css/style.css .gitignore
git commit -m "Update publications"
git push
```

推送后等待 GitHub Pages 自动部署。

如果线上页面还是旧内容，通常是缓存或 GitHub Pages 尚未部署完成。可以尝试：

- 等待几分钟。
- 浏览器强制刷新。
- 用带版本参数的 URL 测试，例如：

```text
https://deep-imaging-group.github.io/publication.html?v=20260624
```
