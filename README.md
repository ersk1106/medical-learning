# 医療知識 学習ロードマップ

医療系動画の制作者が、医師・看護師・医事課と会話でき、企画と台本を医学的に正確に作れるようになるための教材リポジトリです。

## 構成

| パス | 内容 |
| --- | --- |
| `content/index.md` | トップ：全体ロードマップ、脳神経外科30手技の一覧、学習ログ |
| `content/basics.md` | 総論：診療科、医事課、職種別の説明義務、合併症と副作用 |
| `content/lessons/*.md` | 各回のレッスン（front matter に title / short / no / date / group） |
| `figures/<回>/` | 図（SVGが原本、PNGはサイト用） |
| `tools/figs.py` | 第2回以降の図を生成（`rsvg-convert` と Noto Sans CJK が必要） |
| `tools/build.py` | `content/` から `site/` にスマホ向けの静的サイトを生成 |
| `site/` | 生成されたサイト（Claude のアーティファクトとして公開） |

## 更新手順

1. `content/lessons/NN-slug.md` を追加し、図を `figures/NN/` に置く
2. `content/index.md` の一覧の状況とリンク、学習ログを更新
3. `python3 tools/build.py`
4. コミットして push、サイトを再公開

## 注意

医学的判断の根拠にはせず、動画で使う際は専門家の監修を受けてください。点数は令和8年度診療報酬改定時点で、出典を各回に記載しています。
