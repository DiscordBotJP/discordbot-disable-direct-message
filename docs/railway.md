# Railway運用手順

## 前提

このリポジトリはRailwayで常駐Workerとしてビルド・デプロイする前提です。

- `Procfile` は `web: python main.py`
- Pythonバージョンは `runtime.txt` で指定
- Railway/RailpackのPython attestation問題を避けるため `mise.toml` を置く
- Webポートは公開しない常駐Worker

## 必須Variables

RailwayのService Variablesに設定します。

```txt
DISCORD_BOT_TOKEN=
```

## 推奨Variables

```txt
OPS_LOG_HUB_URL=https://ops-log-hub.up.railway.app/api/ingest/discord-bot
OPS_LOG_HUB_KEY=
OPS_LOG_ENVIRONMENT=production
OPS_LOG_PROJECT=discordbot_disable_direct_message
OPS_LOG_HUB_TIMEOUT_SECONDS=5
```

`OPS_LOG_HUB_URL` または `OPS_LOG_HUB_KEY` を空にするとログ送信は無効になります。

## デプロイ確認

1. Railwayの最新Deploymentが `Success` になっていることを確認する。
2. ログにDiscord Gatewayへのログイン成功が出ていることを確認する。
3. ops-log-hubで `startup` が出ていることを確認する。
4. ops-log-hubで `auto_disable_started` と `auto_disable_completed` が6時間ごとに出ていることを確認する。
5. Discordの検証用GuildでDM一時停止期限が未来時刻へ更新されていることを確認する。
6. 招待一時停止を有効にしているGuildでは、Bot実行後も招待一時停止期限が維持されていることを確認する。

## Restart policy

現在はRailway側のService設定に従います。

長期運用でプロセスが終了コード0で終了するケースも自動復旧したい場合は、Railwayの有料プラン制約を確認したうえで `ALWAYS` への変更を検討してください。

## 障害時の見方

- `DISCORD_BOT_TOKEN is required`: Railway VariablesにBot tokenが未設定
- `OPS_LOG_HUB_TIMEOUT_SECONDS must be a number`: タイムアウト値が数値ではない
- `auto_disable_forbidden`: Botに対象Guildのセキュリティ設定編集権限がない
- `auto_disable_error`: Guild単位の想定外エラー
- `auto_disable_task_error`: タスク全体の想定外エラー

## バージョン更新

Pythonを更新する場合:

1. Python.orgの最新安定版を確認する。
2. `runtime.txt` を更新する。
3. 必要に応じて `mise.toml` の互換性を確認する。
4. Railwayでビルドが成功することを確認する。

discord.pyを更新する場合:

1. PyPIの最新リリースを確認する。
2. `requirements.txt` を更新する。
3. import確認と依存解決確認を行う。
4. Discordの検証用Guildで `guild.edit` の挙動を確認する。
