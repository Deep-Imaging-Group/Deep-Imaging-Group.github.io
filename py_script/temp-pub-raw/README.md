# 论文候选数据临时目录

这个目录用于临时存放人工整理或由 BibTeX 转换出来的论文候选 JSON。

Google Scholar 自动抓取逻辑已经暂停。这里的文件不会被网站直接读取，不能直接作为正式网站数据使用。

从 BibTeX 生成候选 JSON：

```bash
python3 py_script/bib_to_temp_publications.py
```

使用流程：

1. 先人工检查论文名、作者、年份、期刊/会议名、paper 链接等字段。
2. 手动补充 `code` 字段。
3. 确认无误后，再复制到正式目录 `publications/`。
4. 运行 `python3 py_script/build_publication_index.py` 更新 `publications/index.json`。

更完整的操作说明见：

```text
py_script/PUBLICATION_WORKFLOW.md
```
