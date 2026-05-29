# アーキテクチャ

## 目的

このBotは、参加中のDiscord Guildに対して `dms_disabled_until` を定期更新し、メンバー間DM一時停止を継続する単機能の常駐Workerです。

WebサーバーやDBは持たず、Railway上で `python main.py` を1プロセスとして起動します。

## 実行フロー

1. `main.py` が `DisableDirectMessageBot` を起動する。
2. `setup_hook` で `extensions.auto_disable` をロードする。
3. `AutoDisableDirectMessageCog` の `tasks.loop(hours=6)` が開始される。
4. Bot ready後、参加中Guildを走査する。
5. 各Guildに対して `guild.edit(invites_disabled_until=..., dms_disabled_until=...)` を実行する。
6. 実行結果をops-log-hubへ送信する。

## Discord API上の前提

- `dms_disabled_until` は実行時刻から24時間後へ更新する。
- `invites_disabled_until` は現在の `guild.invites_paused_until` を読み取り、期限切れでなければ同時送信して保持する。
- `Forbidden` はGuild単位の権限不足として扱い、処理全体は継続する。
- その他の例外はGuild単位でログ送信し、次のGuildへ進む。
- タスク全体の例外は `auto_disable_task_error` としてログ送信し、次回ループを継続できるように捕捉する。

## Gateway Intent

必要なIntentは以下のみです。

- `guilds`: 参加Guild一覧とGuild情報の取得
- `guild_messages`: Discordが投稿するincident security noticeの検知

`members`, `presences`, `message_content` などのprivileged intentは不要です。

## 環境変数

必須:

- `DISCORD_BOT_TOKEN`: Discord Bot token

任意:

- `OPS_LOG_HUB_URL`: ops-log-hub ingest URL。未設定または空ならログ送信を無効化
- `OPS_LOG_HUB_KEY`: ingest API key
- `OPS_LOG_HUB_ENVIRONMENT`: 既定値 `production`
- `OPS_LOG_HUB_PROJECT`: 既定値 `discordbot_disable_direct_message`
- `OPS_LOG_HUB_TIMEOUT_SECONDS`: 既定値 `5`

## 依存関係

- `discord.py`: Discord Gateway/APIクライアント
- `aiohttp`: ops-log-hubへのHTTP送信
- `python-dotenv`: ローカル開発時の `.env` 読み込み

未使用依存はRailwayのビルド時間、脆弱性表面、トラブルシュート範囲を増やすため追加しません。

## 変更時の注意

- DM一時停止の周期と延長時間を変更する場合は、運用仕様とREADMEも更新する。
- `guild.edit` の引数を増減する場合は、Discordセキュリティメニュー上の副作用を検証する。
- incident notice削除は監査性に影響するため、挙動を変える場合は運用者へ明示する。
- Railwayの起動設定を変える場合は `railway.json`, `.python-version`, `runtime.txt`, `docs/railway.md` を同時に確認する。
