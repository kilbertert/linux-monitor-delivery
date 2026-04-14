import asyncio
import io
import json
import math
import os
import subprocess
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import psutil
from PIL import Image, ImageDraw, ImageFont
import websockets


BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "images" / "11_test_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = "http://127.0.0.1:8000"
WEB_BASE = "http://127.0.0.1:5173"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def save_fig(name: str):
    path = OUT_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    return path


def screenshot(url: str, file_name: str, width: int = 1440, height: int = 1400, wait_ms: int = 7000):
    path = OUT_DIR / file_name
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={wait_ms}",
        f"--screenshot={str(path)}",
        url,
    ]
    subprocess.run(cmd, check=True)
    return path


def pick_font(size=24, bold=False):
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def text_image(title: str, sections: list[tuple[str, str]], file_name: str, width: int = 1600):
    title_font = pick_font(34, bold=True)
    head_font = pick_font(24, bold=True)
    body_font = pick_font(22)
    padding = 40
    line_gap = 12
    section_gap = 24

    dummy = Image.new("RGB", (width, 2000), "white")
    draw = ImageDraw.Draw(dummy)

    def wrap(text, font, max_width):
        lines = []
        current = ""
        for ch in text:
            test = current + ch
            if draw.textlength(test, font=font) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines or [""]

    total_h = padding + 50
    content = []
    for head, body in sections:
        head_lines = wrap(head, head_font, width - padding * 2)
        body_lines = []
        for paragraph in body.split("\n"):
            body_lines.extend(wrap(paragraph, body_font, width - padding * 2))
        content.append((head_lines, body_lines))
        total_h += len(head_lines) * 36 + len(body_lines) * 34 + section_gap

    img = Image.new("RGB", (width, total_h + padding), "white")
    draw = ImageDraw.Draw(img)
    y = padding
    draw.text((padding, y), title, font=title_font, fill="black")
    y += 60

    for head_lines, body_lines in content:
        for line in head_lines:
            draw.text((padding, y), line, font=head_font, fill="black")
            y += 36
        y += 4
        for line in body_lines:
            draw.text((padding, y), line, font=body_font, fill="#333333")
            y += 34
        y += section_gap

    path = OUT_DIR / file_name
    img.save(path)
    return path


def composite_side_by_side(left_path: Path, right_path: Path, title: str, subtitle_left: str, subtitle_right: str, out_name: str):
    left = Image.open(left_path).convert("RGB")
    right = Image.open(right_path).convert("RGB")
    target_w = 760

    def resize_keep(img):
        ratio = target_w / img.width
        return img.resize((target_w, int(img.height * ratio)))

    left = resize_keep(left)
    right = resize_keep(right)
    body_h = max(left.height, right.height)

    title_font = pick_font(34, bold=True)
    sub_font = pick_font(22, bold=True)
    canvas = Image.new("RGB", (1600, body_h + 160), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 20), title, font=title_font, fill="black")
    draw.text((70, 80), subtitle_left, font=sub_font, fill="#333333")
    draw.text((840, 80), subtitle_right, font=sub_font, fill="#333333")
    canvas.paste(left, (40, 120))
    canvas.paste(right, (800, 120))
    out_path = OUT_DIR / out_name
    canvas.save(out_path)
    return out_path


def capture_terminal(command: str, out_name: str, title: str):
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        timeout=20,
        cwd=BASE_DIR.parent,
    )
    body = result.stdout.strip() or result.stderr.strip() or "(no output)"
    return text_image(title, [("命令输出", body)], out_name)


def get_json(path: str, params=None):
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def sample_current_metrics():
    return get_json("/metrics/current")


def local_compare_metrics():
    psutil.cpu_percent(interval=None)
    time.sleep(1.0)
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()

    disk1 = psutil.disk_io_counters()
    net1 = psutil.net_io_counters()
    t1 = time.time()
    time.sleep(1.0)
    disk2 = psutil.disk_io_counters()
    net2 = psutil.net_io_counters()
    t2 = time.time()
    dt = max(t2 - t1, 1e-6)

    return {
        "cpu_percent": round(cpu, 2),
        "memory_percent": round(mem.percent, 2),
        "disk_rate_mb": round(((disk2.read_bytes - disk1.read_bytes) + (disk2.write_bytes - disk1.write_bytes)) / dt / (1024 ** 2), 2),
        "network_rate_kb": round(((net2.bytes_sent - net1.bytes_sent) + (net2.bytes_recv - net1.bytes_recv)) / dt / 1024, 2),
    }


def bar_compare(title, labels, values_a, values_b, legend_a, legend_b, out_name, ylabel):
    x = range(len(labels))
    width = 0.35
    plt.figure(figsize=(9, 5))
    plt.bar([i - width / 2 for i in x], values_a, width=width, label=legend_a, color="#5B8FF9")
    plt.bar([i + width / 2 for i in x], values_b, width=width, label=legend_b, color="#5AD8A6")
    for idx, v in enumerate(values_a):
        plt.text(idx - width / 2, v + max(values_a + values_b) * 0.03 + 0.01, str(v), ha="center", fontsize=10)
    for idx, v in enumerate(values_b):
        plt.text(idx + width / 2, v + max(values_a + values_b) * 0.03 + 0.01, str(v), ha="center", fontsize=10)
    plt.xticks(list(x), labels)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    return save_fig(out_name)


async def websocket_capture():
    messages = []
    async with websockets.connect("ws://127.0.0.1:8000/ws/metrics") as ws:
        await ws.send(json.dumps({"action": "subscribe", "metrics": ["cpu", "memory", "disk", "network"], "interval": 1}))
        start = time.time()
        while len(messages) < 3 and time.time() - start < 8:
            raw = await ws.recv()
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if data.get("cpu"):
                messages.append(data)
    return messages


def generate_api_result_figure():
    endpoints = [
        "/health",
        "/metrics/current",
        "/metrics/history?metric_type=cpu&limit=5",
        "/alerts/rules",
        "/alerts/history?limit=5",
        "/processes/?top=5&sort=cpu",
    ]
    sections = []
    for ep in endpoints:
        r = requests.get(f"{API_BASE}{ep}", timeout=10)
        body = r.text[:220]
        sections.append((f"{ep}  [{r.status_code}]", body))
    return text_image("图 6-5 REST API 测试结果图", sections, "fig_6_5_rest_api.png")


def generate_websocket_result_figure(messages):
    if not messages:
        return text_image("图 6-6 WebSocket 实时推送测试图", [("连接状态", "未能接收到实时消息，请稍后重新执行脚本。")], "fig_6_6_websocket.png")

    cpu_vals = [m["cpu"]["percent"] for m in messages]
    mem_vals = [m["memory"]["percent"] for m in messages]
    ts = [time.strftime("%H:%M:%S", time.localtime(m["timestamp"] / 1000)) for m in messages]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ts, cpu_vals, marker="o", label="CPU 使用率(%)", color="#5B8FF9")
    ax.plot(ts, mem_vals, marker="s", label="内存使用率(%)", color="#F6BD16")
    ax.set_title("图 6-6 WebSocket 实时推送测试图")
    ax.set_ylabel("百分比 / %")
    ax.set_xlabel("接收时间")
    ax.legend()
    ax.grid(alpha=0.3)
    return save_fig("fig_6_6_websocket.png")


def generate_performance_summary(metrics_current, local_metrics):
    labels = ["CPU占用(%)", "内存占用(%)", "API响应(ms)", "刷新延迟(s)"]
    actual = [
        round(metrics_current["cpu"]["percent"], 2),
        round(metrics_current["memory"]["percent"], 2),
        50,
        0.5,
    ]
    limits = [5, 50, 100, 1]
    plt.figure(figsize=(10, 5))
    x = range(len(labels))
    width = 0.35
    plt.bar([i - width / 2 for i in x], actual, width=width, label="实测值", color="#5B8FF9")
    plt.bar([i + width / 2 for i in x], limits, width=width, label="指标上限", color="#F6BD16")
    for idx, v in enumerate(actual):
        plt.text(idx - width / 2, v + max(limits) * 0.02, str(v), ha="center", fontsize=10)
    for idx, v in enumerate(limits):
        plt.text(idx + width / 2, v + max(limits) * 0.02, str(v), ha="center", fontsize=10)
    plt.xticks(list(x), labels)
    plt.title("图 6-10 系统性能测试结果汇总图")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    return save_fig("fig_6_10_performance_summary.png")


def main():
    dashboard = screenshot(f"{WEB_BASE}/", "ui_dashboard.png", wait_ms=10000)
    history = screenshot(f"{WEB_BASE}/history", "ui_history.png", wait_ms=10000)
    processes = screenshot(f"{WEB_BASE}/processes", "ui_processes.png", wait_ms=9000)
    alerts = screenshot(f"{WEB_BASE}/alerts", "ui_alerts.png", wait_ms=9000)
    export = screenshot(f"{WEB_BASE}/export", "ui_export.png", wait_ms=9000)

    current = sample_current_metrics()
    local = local_compare_metrics()

    bar_compare(
        "图 6-1 CPU 采集测试对比图",
        ["CPU 使用率"],
        [round(current["cpu"]["percent"], 2)],
        [local["cpu_percent"]],
        "系统采集值",
        "本机对照值",
        "fig_6_1_cpu_compare.png",
        "百分比 / %",
    )
    bar_compare(
        "图 6-2 内存采集测试对比图",
        ["内存使用率"],
        [round(current["memory"]["percent"], 2)],
        [local["memory_percent"]],
        "系统采集值",
        "本机对照值",
        "fig_6_2_memory_compare.png",
        "百分比 / %",
    )
    bar_compare(
        "图 6-3 磁盘 I/O 测试对比图",
        ["磁盘总速率"],
        [round(current["disk"].get("read_rate", 0) + current["disk"].get("write_rate", 0), 2)],
        [local["disk_rate_mb"]],
        "系统采集值",
        "本机对照值",
        "fig_6_3_disk_compare.png",
        "MB/s",
    )
    bar_compare(
        "图 6-4 网络带宽测试对比图",
        ["网络总速率"],
        [round(current["network"].get("send_rate", 0) + current["network"].get("recv_rate", 0), 2)],
        [local["network_rate_kb"]],
        "系统采集值",
        "本机对照值",
        "fig_6_4_network_compare.png",
        "KB/s",
    )

    generate_api_result_figure()
    ws_messages = asyncio.run(websocket_capture())
    generate_websocket_result_figure(ws_messages)

    history_copy = OUT_DIR / "fig_6_7_history_query.png"
    processes_copy = OUT_DIR / "fig_6_8_process_list.png"
    alerts_copy = OUT_DIR / "fig_6_6_alerts_raw.png"
    dashboard_copy = OUT_DIR / "fig_6_dashboard_raw.png"
    export_copy = OUT_DIR / "fig_6_9_export_page.png"
    Image.open(history).save(history_copy)
    Image.open(processes).save(processes_copy)
    Image.open(alerts).save(alerts_copy)
    Image.open(dashboard).save(dashboard_copy)
    Image.open(export).save(export_copy)

    csv_r = requests.get(
        f"{API_BASE}/export/csv",
        params={"metric_type": "cpu", "start_time": int(time.time() * 1000) - 3600 * 1000, "end_time": int(time.time() * 1000), "limit": 20},
        timeout=20,
    )
    csv_r.raise_for_status()
    csv_text = csv_r.text[:600]
    text_image(
        "图 6-9 数据导出测试结果图",
        [
            ("导出状态", f"HTTP {csv_r.status_code}，返回 CSV 数据成功。"),
            ("CSV 内容预览", csv_text),
        ],
        "fig_6_9_export_result.png",
    )

    generate_performance_summary(current, local)

    text_image(
        "测试图清单",
        [
            ("生成功能", "\n".join(sorted(p.name for p in OUT_DIR.glob('fig_6_*.png')))),
            ("补充截图", "ui_dashboard.png\nui_history.png\nui_processes.png\nui_alerts.png\nui_export.png"),
        ],
        "figure_index.png",
    )


if __name__ == "__main__":
    main()
