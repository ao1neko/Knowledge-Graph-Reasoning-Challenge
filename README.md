# Dataset
[Dataset for Knowledge Graph Reasoning Challenge for Social Issue](https://github.com/KGRC4SI/DataSet/tree/kgrc4si?tab=readme-ov-file) by Shusaku Egami, Takanori Ugai, Swe Nwe Nwe Htun, Kouji Kozaki, Takahiro Kawamura, Ken Fukuda

# 環境設定
- [Datasetディレクトリ](https://github.com/KGRC4SI/DataSet)をプロジェクト直下に配置  
- 動画ファイルを[zipファイル](https://kgrc4si.home.kg/Movie/)でダウロード後，解凍してmovie/original以下に配置  
- 環境変数API_KEYに，自身のOpenAIのapikeyを設定  

# 実行
### phase 1  
知識グラフを用いた質問応答
> python phase1.py [PROJECT_PATH]

### phase 2
ビデオを用いた質問応答  
- ビデオを複数画像に分割，画像を分類
> python movie.py [PROJECT_PATH]  
> python label.py [PROJECT_PATH]
- 得られた分類結果から回答を予測
> python phase2 .py [PROJECT_PATH]  
