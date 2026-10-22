# Q積表｜土地家屋調査士のための求積表出力プラグイン

Q積表は、土地家屋調査士の実務を想定した求積表作成プラグインです。

## できること

- `kyuseki_html()` で求積表 HTML を生成
- 印刷レイアウトへ求積表ラベルを自動追加
- 地番絞り込み（単一値 / カンマ区切り / 配列 / 式 / `@atlas_featureid`）
- 地番フィールド名の揺れ吸収（フィールド名・エイリアス両対応）
- 点名属性・境界標属性の照合
- `show_tsubo=true` で地積（坪）表示

## クイックスタート

### 最小例

```text
kyuseki_html('ポリゴンレイヤ名', '地番', '12-1', 'ポイントレイヤ名', '点名', '境界標')
```

### 複数地番

```text
kyuseki_html('ポリゴンレイヤ名', '地番', array('12-1', '12-2'), 'ポイントレイヤ名', '点名', '境界標')
```

### アトラス連携

```text
kyuseki_html(
  'ポリゴンレイヤ名',
  '地番',
  attribute(@atlas_feature, '地番'),
  'ポイントレイヤ名',
  '点名',
  '境界標',
  false,
  3,
  2,
  2,
  true,
  true,
  'north',
  0.0005
)
```

## 引数（順序）

```text
kyuseki_html(
  polygon_layer,
  label_field,
  feature_filter,
  point_layer,
  name_field,
  marker_field,
  full_precision,
  coord_digits,
  area_digits,
  column_count,
  show_total_table,
  show_tsubo,
  start,
  tolerance
)
```

## 表示ルール

- 地理座標系（経緯度）レイヤでは作成できません（投影座標系で利用）。
- `feature_filter` が単純な地番入力の場合、ダッシュ種別（全角/半角など）の揺れを吸収して照合します。
- 列見出しは `(Xn+1-Xn-1)Yn` を使用します。
- `full_precision=false` の場合
  - 座標: `coord_digits` 桁
  - `(Xn+1-Xn-1)Yn`・倍面積: `2*coord_digits` 桁
  - 面積: `2*coord_digits+1` 桁
- `full_precision=true` の場合、上記はフル桁表示（丸めなし）で、面積見出しに「（フル桁）」を付与します。
- 地積は `full_precision` に関係なく、`area_digits` 桁で常に切り捨て表示します。
- `show_total_table=true` で最下部に「合計 / 面積の合計 / 地積の合計」を表示します。
- `show_tsubo=true` で、地積の直下に「地積（坪）」を追加表示します（地積の切り捨て済み値を坪換算）。
- 倍面積・面積・地積（および坪表示）は値セル内で開始位置を揃えて表示します。
- `column_count` は `0` と `1` が縦1列、`2` 以上で横方向分割配置です。
- 穴開きポリゴン（外郭-穴）は、外郭/穴パート行で計算した倍面積の合算を基準に倍面積・面積・地積を算出します。

## 印刷レイアウト連携

印刷レイアウト画面で Q積表 メニューの「求積表ラベルを追加」を実行すると、
`[% kyuseki_html(...) %]` 形式のラベルを現在設定で自動追加できます。

- Plugins メニューには追加せず、印刷レイアウト側メニューのみ提供
- 追加ラベルは HTML レンダリングを自動 ON
- ラベル位置は表示中ビュー中心を基準に、ページ内（A4 などのページ設定サイズ内）へ自動配置
- 初期フォントは `BIZ UDGothic` 優先（見つからない場合は順次フォールバック）、初期サイズは 5pt
- 罫線などの見た目は HTML 側で制御し、フォントはラベルプロパティ側の設定を優先
