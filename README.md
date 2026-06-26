# Discord DM一時停止ボット

Discordサーバーの「メンバー間のDM一時停止」を継続的に更新し、サーバー参加直後などのリスク期間における不審なダイレクトメッセージ被害を抑制するためのBotです。

`extensions/auto_disable.py` の定期タスクが、参加している全サーバーに対して6時間ごとに `dms_disabled_until` を24時間先へ延長します。Railwayで常時稼働する前提です。

## 現在の実行環境

- Python: 3.11.8
- discord.py: 2.6
- 起動コマンド: `python main.py`
- Railway起動定義: `Procfile`

RailwayのPython runtimeは、他のPilot Botと同じ `runtime.txt` + `mise.toml` で固定しています。

## できること

- Botが参加している各サーバーの `dms_disabled_until` を自動更新
- 実行間隔: 6時間ごと
- 更新内容: 実行時点から24時間先を新しい期限として設定
- `guild.edit` 時に `invites_disabled_until` も同時送信し、招待一時停止の既存値を保持
- 権限不足時はそのサーバーのみスキップし、他サーバー処理を継続
- Discordが投稿する incident security notice を削除
- ops-log-hubへ開始・完了・権限不足・想定外エラーを送信

## ディレクトリ構成

- `main.py`: Bot起動エントリポイント
- `extensions/auto_disable.py`: DM一時停止の定期更新ロジック
- `utils/ops_log.py`: ops-log-hub送信用クライアント
- `constants/__init__.py`: 環境変数の読み取りと検証
- `runtime.txt` / `mise.toml`: Railway向けPython runtime設定
- `Procfile`: Railway起動コマンド
- `docs/architecture.md`: アーキテクチャと設計上の前提
- `docs/railway.md`: Railway運用手順
- `docs/discord_security_spec.md`: Discordセキュリティメニューの運用仕様
- `AGENTS.md`: AI/自動化エージェント向け作業メモ

## セットアップ

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`.env.example` を参考に環境変数を設定します。

```txt
DISCORD_BOT_TOKEN=
OPS_LOG_HUB_URL=https://ops-log-hub.up.railway.app/api/ingest/discord-bot
OPS_LOG_HUB_KEY=
OPS_LOG_ENVIRONMENT=production
OPS_LOG_PROJECT=discordbot_disable_direct_message
OPS_LOG_HUB_TIMEOUT_SECONDS=5
DASHBOARD_CONFIG_URL=https://dashboard.discordbot.jp/api/bot-runtime/settings
DASHBOARD_BOT_CONFIG_SECRET=
```

起動:

```bash
python main.py
```

## Railway運用

Railwayでは `Procfile` の `web: python main.py` を利用します。

詳細は `docs/railway.md` を参照してください。

## ops-log-hubに送信するイベント

- `startup`: Bot起動完了
- `auto_disable_started`: 定期処理開始
- `auto_disable_completed`: 定期処理完了
- `auto_disable_forbidden`: 対象サーバーで権限不足により更新失敗
- `auto_disable_error`: 対象サーバーで想定外エラーにより更新失敗
- `auto_disable_task_error`: 定期処理全体の想定外エラー
- `incident_notice_delete_forbidden`: incident notice削除時の権限不足
- `incident_notice_delete_error`: incident notice削除時の想定外エラー

ログ送信に失敗しても、Bot本体の処理は停止しません。

## 運用上の注意

- Botには対象Guildのセキュリティ設定を編集できる権限が必要です。
- Gateway Intentは `guilds` と `guild_messages` のみに絞っています。privileged intentは不要です。
- DM一時停止設定は「全サーバー一律」で更新されます。サーバーごとの除外や手動優先期間は未実装です。
- Botが対象サーバーを編集できない場合、そのサーバーでは設定更新されません。
- ops-log-hubへ送るログには、Bot tokenや秘匿値を含めないでください。

## Discord Bot JP dashboard 連携

`DASHBOARD_BOT_CONFIG_SECRET` を設定すると、Bot は `DASHBOARD_CONFIG_URL` からサーバー別設定を署名付きで取得します。
dashboard ではサーバーごとの有効/無効、更新周期、基準時刻を保存できます。
Bot は無効化されたサーバーをスキップし、有効な設定の最短周期に定期タスク間隔を合わせます。

## 仕様詳細

- アーキテクチャ: `docs/architecture.md`
- Railway運用: `docs/railway.md`
- Discordセキュリティメニュー仕様: `docs/discord_security_spec.md`
