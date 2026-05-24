# Discord DM一時停止ボット

このリポジトリは、Discordサーバーの「メンバー間のDM一時停止（`dms_disabled_until`）」を継続的に更新し、
サーバー参加直後などのリスク期間における不審なダイレクトメッセージ被害を抑制するための Discord Bot です。

`extensions/auto_disable.py` の定期タスクが、参加している全サーバーに対して6時間ごとにDM一時停止期限を24時間先へ延長します。

## できること

- Botが参加している各サーバーの `dms_disabled_until` を自動更新
- 実行間隔: 6時間ごと
- 更新内容: 実行時点から24時間先を新しい期限として設定
- 権限不足（`Forbidden`）時はそのサーバーのみスキップし、他サーバー処理を継続
- ops-log-hub へ定期処理の開始・完了・権限不足・想定外エラーを送信

## ディレクトリ構成

- `main.py`: Bot起動エントリポイント
- `extensions/auto_disable.py`: DM一時停止の定期更新ロジック
- `utils/ops_log.py`: ops-log-hub 送信用クライアント
- `constants/__init__.py`: `TOKEN` などの定数
- `Procfile`: PaaS向け起動コマンド

## 動作要件

- Python 3.11 系（`runtime.txt` 参照）
- `requirements.txt` に記載された依存パッケージ

## セットアップ

1. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

2. Botトークンを設定

```txt
DISCORD_BOT_TOKEN=
```

3. ops-log-hub 連携を設定

```txt
OPS_LOG_HUB_URL=https://ops-log-hub.up.railway.app/api/ingest/discord-bot
OPS_LOG_HUB_KEY=
OPS_LOG_HUB_ENVIRONMENT=production
OPS_LOG_HUB_PROJECT=discordbot_disable_direct_message
OPS_LOG_HUB_TIMEOUT_SECONDS=5
```

`OPS_LOG_HUB_KEY` は、ops-log-hub 側の `INGEST_API_KEY` と同じ値を設定します。

4. 起動

```bash
python main.py
```

## ops-log-hub に送信するイベント

- `auto_disable_started`: 定期処理開始
- `auto_disable_completed`: 定期処理完了
- `auto_disable_forbidden`: 対象サーバーで権限不足により更新失敗
- `auto_disable_error`: 対象サーバーで想定外エラーにより更新失敗

ログ送信に失敗しても、Bot本体の処理は停止しません。

## 運用上の注意

- このBotは `discord.Intents.all()` を有効化しています。必要最小権限への見直しを推奨します。
- DM一時停止設定は「全サーバー一律」で更新されるため、サーバーごとに例外運用が必要な場合は実装追加が必要です。
- Botが対象サーバーを編集できる権限を持たない場合、そのサーバーでは設定更新されません。
- ops-log-hub へ送るログには、Bot token や秘匿値を含めないでください。

## 仕様詳細

セキュリティ仕様の詳細は以下を参照してください。

- `docs/discord_security_spec.md`

## コンフリクト対策（セキュリティメニュー設定との干渉抑制）

DM一時停止のみ更新した場合に、手動設定した招待一時停止が解除される事象へ対策を実装しています。

- `guild.edit` 時に `invites_disabled_until` と `dms_disabled_until` を同時送信
- 招待一時停止は `guild.invites_paused_until` の現値を読み取り、その値を再送して保持

また、`discord.py` の `Guild.edit` で incident actions として明示的に更新可能な値を精査し、
本Botが扱うべき同種の値は `invites_disabled_until` と `dms_disabled_until` であることを確認しました。
