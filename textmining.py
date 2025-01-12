import pandas as pd
import numpy as np
import unicodedata
import MeCab
from collections import Counter
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import ipadic
import re

# 青空文庫「吾輩は猫である」のURL
url = "https://times.abema.tv/fifaworldcup/articles/-/10032462"
response = requests.get(url)
# 「BeautifulSoup」でサイトの情報を操作できる。
# 　ここではテキストのデータのみ抜き出す。
soup = BeautifulSoup(response.content, "html.parser")
text = soup.get_text()

#関数の設定
def mecab_tokenizer(text):
    replaced_text = unicodedata.normalize("NFKC",text)
    replaced_text = replaced_text.upper()
    replaced_text = re.sub(r'[【】 () （） 『』　「」]', '' ,replaced_text) #【】 () 「」　『』の除去
    replaced_text = re.sub(r'[\[\［］\]]', ' ', replaced_text)   # ［］の除去
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    replaced_text = re.sub(r'\d+\.*\d*', '', replaced_text) #数字を0にする

    #（大和追加）MeCab.Tagger()
    # pipも必要（https://taketake2.com/Q4-4.html）
    mecab = MeCab.Tagger() 
    parsed_lines = mecab.parse(replaced_text).split("\n")[:-2]

    #（大和追加）最初の段階で品詞の種類を絞り込み
    #parsed_lines = [s for s in parsed_lines if ('名詞' in s or '動詞' in s or '形容詞' in s ) and ('助動詞' not in s )]

    #単語を取得
    surfaces = [l.split("\t")[0] for l in parsed_lines]

    #品詞を取得（元のプログラムでは1を指定していたが、順番が変わったらしいので4をセット）
    pos = [l.split("\t")[4].split(",")[0] for l in parsed_lines]

    # （大和修正）元ファイルだと上手く行かなかったので、少し修正
    token_list = [t for t , p in zip(surfaces, pos) if ('名詞' in p or '動詞' in p or '形容詞' in p ) and ('助動詞' not in p ) ]

    #ひらがなのみの単語を除く
    kana_re = re.compile("^[ぁ-ゖ]+$")
    token_list = [t for t in token_list if not kana_re.match(t)]

    #各トークンを少しスペースを空けて（' '）結合
    return ' '.join(token_list)

#関数の実行
words = mecab_tokenizer(text)

#（大和修正）大和のローカル環境に合わせる
# フォントの設定
font_path=r"C:\Windows\Fonts\HGRPP1.TTC"
#色の設定
colormap="Paired"

wordcloud = WordCloud(
    background_color="white",
    width=800,
    height=800,
    font_path=font_path,
    colormap = colormap,
    stopwords=["する", "ある", "こと", "ない"],
    max_words=100,
    ).generate(words)

plt.figure(figsize=(10, 10))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
# ファイルを保存
plt.savefig('sample.png')
plt.show()