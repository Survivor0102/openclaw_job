---
name: image-table-extractor
description: Extract structured table data from images using DashScope Qwen-VL multimodal AI
author: OpenClaw Community
version: 1.0.0
triggers:
  - "extract table from image"
  - "图片提取表格"
  - "image to table"
  - "OCR 表格"
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python3","uv"]},"config":{"env":{"DASHSCOPE_API_KEY":{"description":"DashScope API Key for Qwen-VL model","required":true}}}}}
---

# Image Table Extractor

Extract structured table data from images using DashScope Qwen-VL multimodal AI model.

## Quick Start

```bash
uv run {baseDir}/scripts/extract_table.py --image path/to/image.jpg --output table.csv
```

## Commands

### Single Image
```bash
uv run {baseDir}/scripts/extract_table.py --image image.jpg --output result.csv
uv run {baseDir}/scripts/extract_table.py --image image.png --output result.md --format markdown
```

### Multiple Images (merge into one table)
```bash
uv run {baseDir}/scripts/extract_table.py --images image1.jpg image2.jpg --output merged.csv
```

### JSON Output
```bash
uv run {baseDir}/scripts/extract_table.py --image image.jpg --output result.json --format json
```

## Configuration

**Required:** Set the `DASHSCOPE_API_KEY` environment variable:

```bash
export DASHSCOPE_API_KEY="sk-your-api-key"
```

Or configure in your OpenClaw config.

## Features

- 📸 Extract tables from images (JPG, PNG)
- 📊 Output to CSV, Markdown, or JSON
- 🔀 Merge multiple images into one table
- 🎯 Optimized for Chinese document tables
- 📋 Preserves column structure

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| CSV | .csv | Excel, data analysis |
| Markdown | .md | GitHub, documentation |
| JSON | .json | Programmatic use |

## Example Output

For a student admission table:
```csv
序号，姓名，专业班级，录取院校，录取专业，录取类别
1，韩润哲，电子信息工程 2022-2 班，大连海事大学，人工智能，专业型硕士
2，董艺瑶，电子信息工程 2022-2 班，大连海事大学，通信工程（含宽带网络、移动通信等）,专业型硕士
```

## Troubleshooting

**API Key Error:** Ensure `DASHSCOPE_API_KEY` is set correctly.

**Image Not Found:** Use absolute paths or ensure relative paths are correct.

**Timeout:** Large images may take longer; the script handles retries.

## API

Uses DashScope Qwen-VL-Max multimodal conversation API.
