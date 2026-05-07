# Discord DM一時停止ボット

このリポジトリは、Discordサーバーの「メンバー間のDM一時停止（`dms_disabled_until`）」を継続的に更新し、
サーバー参加直後などのリスク期間における不審なダイレクトメッセージ被害を抑制するための Discord Bot です。

`extensions/auto_disable.py` の定期タスクが、参加している全サーバーに対して6時間ごとにDM一時停止期限を24時間先へ延長します。

## できること

- Botが参加している各サーバーの `dms_disabled_until` を自動更新
- 実行間隔: 6時間ごと
- 更新内容: 実行時点から24時間先を新しい期限として設定
- 権限不足（`Forbidden`）時はそのサーバーのみスキップし、他サーバー処理を継続

## ディレクトリ構成

- `main.py`: Bot起動エントリポイント
- `extensions/auto_disable.py`: DM一時停止の定期更新ロジック
- `constants/__init__.py`: `TOKEN` などの定数（実運用では環境変数化推奨）
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
   現状コードは `constants.TOKEN` を参照します。`constants/__init__.py` で適切に定義してください。

3. 起動

```bash
python main.py
```

## 運用上の注意

- このBotは `discord.Intents.all()` を有効化しています。必要最小権限への見直しを推奨します。
- DM一時停止設定は「全サーバー一律」で更新されるため、サーバーごとに例外運用が必要な場合は実装追加が必要です。
- Botが対象サーバーを編集できる権限を持たない場合、そのサーバーでは設定更新されません。

## 仕様詳細

セキュリティ仕様の詳細は以下を参照してください。

- `docs/discord_security_spec.md`


## コンフリクト対策（セキュリティメニュー設定との干渉抑制）

本Botは `guild.edit(dms_disabled_until=...)` を呼び出すため、Discord側仕様や将来変更によっては、
セキュリティメニュー内の他項目に意図しない影響が出る可能性があります（未確認、必要に応じて確認）。

このリポジトリでは、干渉リスクを下げるために以下の制御を実装しています。

- `DM_DISABLE_ENABLED_GUILD_IDS`（カンマ区切りGuild ID）で対象サーバーを限定可能
- `DM_DISABLE_MIN_REMAINING_HOURS` 以上の残り時間がある場合は `guild.edit` を実行しない
- `DM_DISABLE_TARGET_HOURS` で延長先時間を調整可能
- DM更新時に `invites_disabled_until` も同時に送信し、手動設定した招待一時停止が解除されにくいよう対策

環境変数未設定時は従来互換の動作（全Guild対象、24時間先へ延長、12時間未満でのみ更新）です。
