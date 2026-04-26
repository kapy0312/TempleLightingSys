import webview
import threading
import time
from app import app


def start_flask():
    # 使用 threaded=True 確保 Flask 不會阻塞主執行緒
    app.run(port=5001, threaded=True)


if __name__ == '__main__':
    # 1. 先啟動 Flask
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    # 2. 稍微等待 1 秒確保伺服器已就緒
    time.sleep(1)

    # 3. 建立視窗，明確指定 localhost URL 而非傳入 app 物件
    window = webview.create_window(
        title='正坤點燈資料管理系統 v1.0.2',
        url='http://127.0.0.1:5001',
        width=1024,
        height=768,
        min_size=(800, 600),
        text_select=True  # <--- 新增這一行，允許文字選取與複製
    )

    # 4. 啟動視窗 (關閉 debug 以獲得乾淨介面)
    webview.start(gui='edgechromium')
