# AGENTS

このファイルは、人間の保守者とAI/自動化エージェントが同じ前提で作業するためのメモです。

## プロジェクト概要

- Railwayで常時稼働するDiscord Botです。
- 主処理は `extensions/auto_disable.py` にあります。
- DBはありません。
- Webサーバーもありません。
- Bot tokenなどの秘匿値は環境変数でのみ扱います。

## 重要な不変条件

- `dms_disabled_until` は6時間ごとに24時間先へ更新します。
- `guild.edit` では `dms_disabled_until` と `invites_disabled_until` を同時送信します。
- `Forbidden` はGuild単位でログに残し、他Guildの処理を継続します。
- ops-log-hub送信失敗でBot本体を止めてはいけません。
- privileged intentを追加する場合は、必要性をREADMEと `docs/architecture.md` に書きます。

## よく使うコマンド

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m compileall main.py constants extensions utils
DISCORD_BOT_TOKEN=dummy OPS_LOG_HUB_URL= python - <<'PY'
from main import build_intents
intents = build_intents()
print(intents.guilds, intents.guild_messages)
PY
```

## ドキュメント更新ルール

- Railway設定を変えたら `README.md` と `docs/railway.md` を更新します。
- Discordセキュリティメニュー挙動を変えたら `docs/discord_security_spec.md` を更新します。
- アーキテクチャ上の前提を変えたら `docs/architecture.md` を更新します。

## レビュー観点

- Railwayで起動できるか
- Discord権限不足時に他Guildへ影響しないか
- 手動設定した招待一時停止を巻き戻さないか
- ログに秘匿値が混入しないか
- 不要なprivileged intentや未使用依存が増えていないか
