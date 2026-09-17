# 記事本同步伺服器（部署到 Raspberry Pi 5）

存放筆記資料並提供 API + 網頁介面（HTTPS），桌面程式（[Notes.py](../Notes.py)）與瀏覽器都連到這台伺服器同步同一份資料。

## 部署步驟（在 Pi5 上執行）

1. 把 `notes_server` 整個資料夾複製到 Pi5，例如用 `scp` 或 `git clone`：

   ```bash
   scp -r notes_server pi@<Pi5的IP>:/home/pi/notes_server
   ```

2. SSH 進 Pi5，建立虛擬環境並安裝套件：

   ```bash
   cd /home/pi/notes_server
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. 先手動測試能不能跑：

   ```bash
   .venv/bin/python app.py
   ```

   第一次啟動會自動產生一組自簽憑證（`certs/cert.pem` / `certs/key.pem`），並印出憑證路徑。在同一區網的電腦瀏覽器開 `https://<Pi5的IP>:5678`，瀏覽器會顯示「不安全」警告（自簽憑證本來就會這樣），點「進階」→「繼續前往」即可看到記事本網頁。`Ctrl+C` 結束測試。

4. 把憑證複製回你要用的電腦（例如跑桌面版的那台）：

   ```bash
   scp pi@<Pi5的IP>:/home/pi/notes_server/certs/cert.pem .
   ```

   只需要 `cert.pem`（公開金鑰），**不要**複製 `key.pem`（私鑰要留在伺服器上）。

5. 設定開機自動啟動（systemd）：

   ```bash
   sudo cp notes-app.service /etc/systemd/system/notes-app.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now notes-app
   ```

   查看狀態／記錄：

   ```bash
   sudo systemctl status notes-app
   journalctl -u notes-app -f
   ```

6. （建議）在路由器把 Pi5 的區網 IP 設成固定 IP（DHCP 保留），這樣憑證裡記錄的 IP、桌面程式設定的網址才不會因為 IP 變動而失效。如果 IP 真的變了，刪除 `certs/` 資料夾整個重來即可（會用新 IP 重新產生憑證，但記得要重新複製給桌面端並在瀏覽器重新信任一次）。

## 資料存放位置

筆記存在 `notes_server/data/notes_data.json`，如果要備份，定期複製這個檔案即可。

## 桌面程式如何連線

[Notes.py](../Notes.py) 第一次啟動、或點介面左上角「⚙」，會跳出設定視窗，需要填兩項：

- **伺服器位址**：`https://<Pi5的IP>:5678`
- **伺服器憑證檔**：選取步驟 4 複製過來的 `cert.pem`

設定會存在本機的 `notes_client_config.json`，也可以直接編輯這個檔案修改。
