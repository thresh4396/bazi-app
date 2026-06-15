"""八字命理 App 启动入口 — 用于打包为独立 exe"""
import sys
import os
import webbrowser
import threading
import time

_browser_opened = False
_lock = threading.Lock()


def open_browser_once(port):
    global _browser_opened
    with _lock:
        if _browser_opened:
            return
        _browser_opened = True
    time.sleep(3)
    webbrowser.open(f"http://localhost:{port}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)

    port = 8501

    # 延迟打开浏览器（只开一次）
    threading.Thread(target=open_browser_once, args=(port,), daemon=True).start()

    print(f"\n=== 八字命理分析系统启动中... ===")
    print(f">> 浏览器将自动打开：http://localhost:{port}")
    print(f">> 关闭此窗口即可停止程序。\n")

    # 直接导入并运行 streamlit（进程内，不走子进程）
    import streamlit.web.cli as stcli

    sys.argv = [
        "streamlit", "run", os.path.join(base_dir, "app.py"),
        "--server.headless", "true",
        "--server.port", str(port),
        "--server.runOnSave", "false",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
