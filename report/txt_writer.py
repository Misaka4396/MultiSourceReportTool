"""TXT report generator with clean formatting."""

import os
import re
from datetime import datetime

_ILLEGAL_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_stem(stem: str, max_len: int = 80) -> str:
    stem = _ILLEGAL_FILENAME.sub("_", stem or "")
    stem = " ".join(stem.split())
    if len(stem) > max_len:
        stem = stem[:max_len].rstrip()
    return stem or "report"


def generate_txt_report(
    title: str,
    data: list[dict],
    output_dir: str,
    selected_fields: list[str],
    field_labels: dict[str, str],
    extra_notes: str = "",
    filename_stem: str = "",
) -> str:
    """Generate a formatted TXT report.

    Args:
        title: Report title
        data: List of result dicts
        output_dir: Directory to save the file
        selected_fields: List of field keys to include
        field_labels: Mapping of field keys to display labels
        extra_notes: Optional extra notes to append
        filename_stem: Optional explicit file name stem (without extension)

    Returns:
        Path to the generated file
    """
    if not filename_stem:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_stem = _safe_stem(f"{title.replace(' ', '_')}_{timestamp}")
    else:
        filename_stem = _safe_stem(filename_stem)
    filename = f"{filename_stem}.txt"
    filepath = os.path.join(output_dir, filename)

    lines = []
    sep = "=" * 72
    sub_sep = "-" * 60

    # Header
    lines.append(sep)
    lines.append(f"  {title}")
    lines.append(f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  结果数量: {len(data)}")
    lines.append(sep)
    lines.append("")

    if extra_notes:
        lines.append(f"  [备注] {extra_notes}")
        lines.append("")

    # Body
    for i, item in enumerate(data, 1):
        lines.append(sub_sep)
        lines.append(f"  [{i}]")
        for field in selected_fields:
            if field in item and item[field]:
                label = field_labels.get(field, field)
                value = item[field]
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                lines.append(f"  {label}: {value}")
        lines.append("")

    # Footer
    lines.append(sep)
    lines.append("  报告由「多源报告汇总推送工具」自动生成")
    lines.append(sep)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
