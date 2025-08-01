# Anki デッキジェネレーター - ユーザーマニュアル

Anki デッキジェネレーターへようこそ！このツールは、お気に入りの動画や字幕から、音声、スクリーンショット、原文を含むバイリンガル Anki 学習カードを簡単かつ効率的に作成するのに役立ちます。
コードはビジネスフレンドリーな Apache オープンソースライセンスに基づいており、ソースコードのアドレスは https://github.com/AquariusGit/AnkiGenerator です。

## 目次
- [ソフトウェアの概要](#ソフトウェアの概要)
- [主な機能](#主な機能)
- [システム要件](#システム要件)
- [初回使用](#初回使用)
- [インターフェースの概要](#インターフェースの概要)
- [使用手順](#使用手順)
  - [ステップ1：オーディオ/ビデオと字幕のダウンロード](#ステップ1オーディオビデオと字幕のダウンロード)
  - [ステップ2：Anki デッキの生成](#ステップ2anki-デッキの生成)
  - [オプション：CSV ファイルからの生成](#オプションcsv-ファイルからの生成)
- [設定タブ](#設定タブ)
- [よくある質問 (FAQ)](#よくある質問-faq)

---

## ソフトウェアの概要

このツールは、YouTubeなどの動画サイトから動画/オーディオと多言語字幕をダウンロードし、Ankiにインポートできる `.apkg` ファイルに処理するグラフィカルインターフェースアプリケーションです。生成されたカードには、原文、翻訳、対応するオーディオクリップ、動画のスクリーンショットを含めることができ、さらに中国語、日本語、韓国語の言語には自動的にピンイン/ふりがな/ローマ字を追加することで、言語学習資料を大幅に充実させることができます。

## 主な機能
- **動画ダウンロード**: YouTubeなどのウェブサイトから動画または純粋なオーディオをダウンロードする機能をサポートしています。
- **字幕ダウンロード**: 公式字幕と自動生成字幕を自動的に取得してダウンロードします。
- **バイリンガルカード**: 2つの言語の字幕を含むAnkiカードをワンクリックで生成します。
- **オーディオ抽出**: 動画から各字幕に対応するオーディオセグメントを自動的に抽出します。
- **動画スクリーンショット**: 各カードの動画フレームを自動的にキャプチャします。
- **TTSサポート**: 動画やオーディオがない場合、gTTSまたはEdge-TTSを使用して字幕の音声を生成できます。
- **自動発音ガイド**:
    - 日本語の漢字に自動的にふりがなを追加します。
    - 中国語の漢字に自動的にピンインを追加します。
    - 韓国語に自動的にローマ字を追加します。
- **高度なカスタマイズ性**:
    - Ankiカードのテンプレートとスタイルをカスタマイズします。
    - 字幕のタイムラインを調整し、字幕行を結合します。
    - 一時ファイルの自動クリーンアップなど、複数の後処理オプション。
- **多言語インターフェース**: 英語、簡体字/繁体字中国語、日本語、韓国語、ベトナム語、その他のインターフェース言語をサポートしています。

## システム要件
- **Python**: Python 3.x 環境が必要です。
- **FFmpeg**: **FFmpeg** をインストールし、システムの環境変数 (PATH) に追加する必要があります。FFmpegは動画からオーディオを抽出し、スクリーンショットをキャプチャするために使用されます。正しくインストールされていない場合、関連する機能は利用できません。

## 初回使用
このソフトウェアを初めて実行すると、「初期設定」ウィンドウがポップアップ表示されます。
1. **表示言語の選択**: ソフトウェアインターフェースに表示したい言語を選択します。
2. **デフォルトの表/裏言語の選択**: 最も頻繁に使用するソース言語（表）とターゲット言語（裏）を設定します。これにより、その後の操作で言語が自動的に選択され、効率が向上します。
設定後、「続行」をクリックしてメインインターフェースに入ります。

## インターフェースの概要
ソフトウェアのメインインターフェースは、主に3つの部分に分かれています。
1. **左側 - 機能タブ**:
    - **オーディオ/ビデオと字幕のダウンロード**: ネットワークURLから素材をダウンロードします。
    - **Anki デッキの生成**: ローカルまたはダウンロードした素材を使用してカードを生成します。
    - **CSV からカードを生成**: `.csv` ファイルからカードを一括生成します。
    - **設定**: ソフトウェアのデフォルトの動作とAnkiテンプレートを設定します。
2. **右側 - ログウィンドウ**: ソフトウェアの操作中に発生するすべての情報、警告、エラーを表示します。
3. **下部 - プログレスバー**: ダウンロードまたは生成の進行状況を表示します。

## 使用手順

### ステップ1：オーディオ/ビデオと字幕のダウンロード
このタブは、オンライン動画からカード作成に必要な素材を取得するために使用されます。ただし、動画またはオーディオには、純粋な中国語や純粋な日本語など、単一の言語のみが含まれていることが望ましいです。複数の言語が同時に含まれている動画やオーディオは使用しないでください。たとえば、最初に中国語を読み、次に日本語を読む動画は適切ではありません。このような機能を提供する必要があるかどうかは後で検討します。

1. **動画URL**: YouTube動画のリンクを貼り付けます。ソフトウェアはクリップボード内の有効なリンクを自動的に検出し、入力します。通常は単一の動画ファイルであり、プレイリストや個人の動画ページではありません（これにより、ダウンロードが正しく行われなかったり、ファイルが多すぎたりする可能性があります）。デフォルトではYouTube動画のみがサポートされています。他のウェブサイトの動画を使用したい場合は、URL入力フィールドの後のチェックボックスをオンにして、URL形式をチェックしないことを示してください。そうすれば、yt-dlpがサポートする任意のウェブサイトからオーディオ/ビデオと字幕をダウンロードできます（結果はご自身で確認してください）。
2. **クエリ言語**: このボタンをクリックすると、ソフトウェアはURLの分析を開始し、利用可能なすべての動画/オーディオ形式と字幕言語を取得します。
3. **ダウンロードディレクトリ**: ダウンロードしたファイルを保存するフォルダを選択します。
4. **オーディオ/ビデオ形式**: ドロップダウンリストから形式を選択します。オーディオとビデオの両方を含む `mp4` 形式、または純粋なオーディオの `m4a` 形式を選択することをお勧めします。
5. **表/裏字幕言語**: カードの表と裏に使用したい字幕言語をそれぞれ選択します。ソフトウェアは「設定」に基づいて自動的にデフォルト言語を選択しようとします。
6. **字幕のみダウンロード**: ローカルに動画ファイルがある場合、またはスクリーンショットや元のオーディオを生成したくない場合は、このオプションをチェックして字幕ファイルのみをダウンロードできます。
7. **ダウンロード開始**: クリックしてダウンロードを開始します。完了後、ソフトウェアはダウンロードしたファイルパスを「Anki デッキの生成」タブに自動的に入力するかどうかを尋ねます。「はい」を選択することをお勧めします。

### ステップ2：Anki デッキの生成
このタブは、素材をAnkiカードに結合するために使用されるコア機能です。

1. **ファイルパス設定**:
    - **メディアファイル (オプション)**: 動画またはオーディオファイルを選択します。動画からオーディオとスクリーンショットを抽出したい場合は、この項目は必須です。
    - **表/裏字幕ファイル**: 2つの言語の字幕ファイル (`.srt` または `.vtt` 形式) を選択します。
    - **出力ディレクトリ**: 生成されたAnkiデッキ (`.apkg`) と一時ファイルの保存場所を選択します（ディレクトリが存在しない場合は自動的に作成されます）。
    - **Anki デッキ名**: Ankiデッキに名前を付けます。デフォルトでは、表の字幕ファイル名と同じになります。

2. **主なオプション**:
    - **スクリーンショットオプション**:
        - `スクリーンショットを追加`: これをチェックすると、各カードのスクリーンショットが生成されます。
        - `スクリーンショットのタイミング`: 字幕の開始、中間、または終了時にスクリーンショットを撮るかを選択します。
        - `品質`: スクリーンショットの品質。1〜31の間で、数字が小さいほど品質が高くなります（ファイルサイズも大きくなります）。
    - **TTSエンジン**: メディアファイルがない場合、またはオーディオ抽出が失敗した場合に、音声を生成するために使用するエンジン。`gTTS` はGoogleサービスへの接続が必要です。利用可能かどうかご自身で確認してください。`gTTS` と `edge-tts` はどちらも良い選択肢です。`MP3を生成しない` はこの機能を無効にします。`gTTS` はGoogleサービスへの接続が必要です。利用可能かどうかご自身で確認してください。
    - **遅い音声**: チェックすると、gTTSはより遅い速度で音声を生成します（edge-ttsはこれをサポートしていません）。
    - **字幕クリーンアップ**: `...非対話コンテンツを削除` をチェックすると、字幕から `[音楽]`、`(拍手)` などのコンテンツが自動的に削除されます。
    - **発音ガイドオプション**: これをチェックすると、表または裏の中国語/日本語/韓国語に発音ガイドが追加されます。
    - **後処理**:
        - `.mp3/.jpg/.csv ファイルをクリーンアップ`: チェックすると、Ankiデッキが正常に生成された後、プロセス中に生成された一時的なオーディオ、スクリーンショット、データファイルが自動的に削除されます。
    - **タイムラインオフセット (ms)**: オーディオと字幕の間に固定の遅延がある場合、ここでミリ秒単位で入力して修正します（正の数はオーディオを早め、負の数はオーディオを遅らせます）。
    - **字幕時間範囲**: 動画の一部のみのカードを作成したい場合は、ここで開始時刻と終了時刻を入力します（形式 `HH:MM:SS`）。
    - **字幕結合**:
        - `時間的に近い字幕行を結合`: チェックすると、時間間隔が非常に近い短い字幕行が1つの文に結合され、会話の多い動画の処理に適しています。この機能はまだ成熟していないため、注意して使用してください。間隔が不規則なポッドキャストのようなメディアにのみ試すことができます。
        - `最大間隔 (ms)`: 字幕を結合できる近さを定義します。
    - **ファイル処理**:
        - `既存のAnkiデッキを上書き`: チェックすると、出力ディレクトリに同じ名前のファイルが既に存在する場合、直接上書きされます。

3. **生成とプレビュー**:
    - **最初の5枚のカードをプレビュー**: 完全なデッキを生成せずに、HTMLファイルをすばやく生成し、ブラウザで最初の5枚のカードの効果をプレビューします。プレビューにはオーディオとプレビュー画像は含まれません。
    - **Anki デッキの生成**: クリックして最終的な生成プロセスを開始します。

### オプション：CSV ファイルからの生成
すでに整理されたバイリンガル比較テキストがある場合は、この機能を使用してすばやくカードを作成できます。

1. **CSV ファイルの準備**: `.csv` ファイルを作成し、**最初の列**をカードの表のテキスト、**2番目の列**をカードの裏のテキストとします。UTF-8エンコードである必要があります。TTSで音声を生成する必要がある場合は、発音ガイドなどのコンテンツを追加しないでください。
2. **CSV ファイル**: ソフトウェアで準備したCSVファイルを選択します。
3. **設定オプション**: 「Anki デッキの生成」タブと同様に、出力ディレクトリ、デッキ名、TTSエンジン、発音ガイドオプションを設定できます。選択した表と裏の言語がCSVファイルと一致していることを確認してください。そうしないと、発音が正しくない可能性があります。
4. **Anki デッキの生成**: ボタンをクリックして生成を開始します。このモードでは、オーディオ抽出とスクリーンショット機能はなく、オーディオは完全にTTSによって生成されます。

## 設定タブ
ここでは、ソフトウェアのデフォルトの動作とカードの外観をカスタマイズできます。

- **デフォルトの表/裏字幕言語**: 最も頻繁に使用する言語を設定すると、ソフトウェアは「ダウンロード」および「自動入力」時にそれらを優先します。
- **Anki テンプレートとスタイル**:
    - **表/裏テンプレート**: Ankiのテンプレート構文（例：`{{Question}}`、`{{Audio_Answer}}`）を使用して、カードの表と裏のレイアウトをカスタマイズします。
    - **スタイルシート**: CSSコードを使用して、カードのフォント、色、背景、その他の外観をカスタマイズします。
- **HTML テンプレートのプレビュー**: 「プレビュー」ボタンをクリックしたときに生成されるHTMLファイルの基本構造をカスタマイズします。通常、これを変更することはお勧めしません。
- **保存と復元**:
    - `設定を保存`: 上記のすべての設定への変更を保存します。
    - `設定を復元`: 変更を元に戻し、最後に保存した状態に復元します。

## よくある質問 (FAQ)
1. **Q: ソフトウェアが「FFmpeg not found」（FFmpegが見つかりません）と表示された場合はどうすればよいですか？**
    A: FFmpeg公式サイト からダウンロードし、解凍後、その `bin` ディレクトリの完全なパスをオペレーティングシステムの `PATH` 環境変数に追加し、ソフトウェアを再起動する必要があります。

2. **Q: 貼り付けたYouTubeリンクが無効と表示されるのはなぜですか？**
    A: このツールは現在、単一の動画URLのみをサポートしており、プレイリストURLはサポートしていません。リンクに `list=` パラメータが含まれていないことを確認してください。他のウェブサイトの動画を使用したい場合、またはソフトウェアをyt-dlpのUIとして使用したい場合は、URLアドレスの後のオプションをチェックして、URLチェックを強制的に無効にしてください。

3. **Q: 発音ガイド機能はどの言語をサポートしていますか？**
    A: 現在、日本語のふりがな、中国語のピンイン、韓国語のローマ字の追加をサポートしています。ソフトウェアは、選択した字幕ファイル名または設定のデフォルト言語に基づいて自動的に判断します。

4. **Q: gTTSとedge-ttsの違いは何ですか？**
    A: どちらもテキスト読み上げエンジンです。gTTS (Google Text-to-Speech) は速度が少し遅い場合がありますが、スロー再生をサポートしています。edge-tts (Microsoft Edge Text-to-Speech) は通常、より自然で高品質な音声ですが、スロー再生はサポートしていません。必要に応じて選択できます。いずれかのエンジンが失敗した場合、ソフトウェアは自動的に別のエンジンを試します。

5. **Q: YouTubeの自動字幕を使用してAnkiデッキを生成することに問題はありますか？**
    A: これは断定できません。自動字幕は、文の区切りに多くの問題がある可能性があり、生成された音声と抽出された音声の両方に問題が生じる可能性があるため、自動字幕の使用はあまり推奨されません。可能な限り、作成者が提供する字幕を使用してください。