#!/usr/bin/env python3
"""
Image Table Extractor - Extract structured table data from images using DashScope Qwen-VL

Usage:
    uv run extract_table.py --image image.jpg --output result.csv
    uv run extract_table.py --images img1.jpg img2.jpg --output merged.csv
    uv run extract_table.py --image image.png --output result.md --format markdown
"""

import argparse
import json
import os
import re
import sys
import csv
from pathlib import Path

try:
    import dashscope
    from dashscope import MultiModalConversation
except ImportError:
    print("Installing dashscope...")
    os.system("uv pip install dashscope -q")
    import dashscope
    from dashscope import MultiModalConversation


def extract_table_from_image(image_path: str, api_key: str) -> list:
    """Extract table data from a single image using Qwen-VL."""
    dashscope.api_key = api_key
    
    messages = [{
        'role': 'user',
        'content': [
            {'image': f'file://{os.path.abspath(image_path)}'},
            {'text': '请提取这张图片中表格的完整内容。请以 JSON 数组格式返回所有记录，每个记录包含表格的所有列。确保数据完整准确。'}
        ]
    }]
    
    print(f"📸 Processing: {image_path}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = MultiModalConversation.call(model='qwen-vl-max', messages=messages, timeout=120)
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content[0]
                text = content.get('text', '') if isinstance(content, dict) else content.text
                
                # Extract JSON from response
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    text = json_match.group(1)
                else:
                    # Try to find JSON array directly
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
                    if json_match:
                        text = json_match.group(0)
                
                data = json.loads(text)
                print(f"✅ Extracted {len(data)} records")
                return data
            else:
                print(f"⚠️ API error: {response.code} - {response.message}")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"API error: {response.code}")
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Error: {e}, retrying...")
                continue
            else:
                raise e
    
    return []


def save_to_csv(data: list, output_path: str):
    """Save data to CSV file."""
    if not data:
        print("⚠️ No data to save")
        return
    
    fieldnames = list(data[0].keys())
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"📊 Saved to: {output_path}")


def save_to_markdown(data: list, output_path: str, title: str = "Extracted Table"):
    """Save data to Markdown table."""
    if not data:
        print("⚠️ No data to save")
        return
    
    fieldnames = list(data[0].keys())
    lines = [f"# {title}", ""]
    lines.append("| " + " | ".join(fieldnames) + " |")
    lines.append("| " + " | ".join(["---"] * len(fieldnames)) + " |")
    
    for row in data:
        lines.append("| " + " | ".join(str(row.get(f, '')) for f in fieldnames) + " |")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"📄 Saved to: {output_path}")


def save_to_json(data: list, output_path: str):
    """Save data to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📋 Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Extract table data from images')
    parser.add_argument('--image', '-i', help='Single image path')
    parser.add_argument('--images', '-I', nargs='+', help='Multiple image paths')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--format', '-f', choices=['csv', 'markdown', 'md', 'json'], default='csv',
                        help='Output format (default: csv)')
    parser.add_argument('--title', '-t', default='Extracted Table', help='Title for Markdown output')
    parser.add_argument('--api-key', '-k', help='DashScope API key (or set DASHSCOPE_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ Error: DASHSCOPE_API_KEY not set")
        print("   Set it with: export DASHSCOPE_API_KEY='sk-your-key'")
        print("   Or use: --api-key sk-your-key")
        sys.exit(1)
    
    # Get image paths
    image_paths = []
    if args.image:
        image_paths = [args.image]
    elif args.images:
        image_paths = args.images
    else:
        print("❌ Error: Specify --image or --images")
        sys.exit(1)
    
    # Validate image paths
    for path in image_paths:
        if not os.path.exists(path):
            print(f"❌ Image not found: {path}")
            sys.exit(1)
    
    # Extract data from all images
    all_data = []
    for img_path in image_paths:
        data = extract_table_from_image(img_path, api_key)
        all_data.extend(data)
    
    # Determine output format
    output_format = args.format
    if args.format in ['csv', 'markdown', 'md', 'json']:
        output_format = args.format
    elif args.output.endswith('.md'):
        output_format = 'markdown'
    elif args.output.endswith('.json'):
        output_format = 'json'
    else:
        output_format = 'csv'
    
    # Save output
    if output_format == 'json':
        save_to_json(all_data, args.output)
    elif output_format in ['markdown', 'md']:
        save_to_markdown(all_data, args.output, args.title)
    else:
        save_to_csv(all_data, args.output)
    
    print(f"\n✅ Done! Extracted {len(all_data)} total records from {len(image_paths)} image(s)")


if __name__ == '__main__':
    main()
