import math
import re
from collections import Counter

CJK_RUN_RE = re.compile(r"[一-鿿]+")
LATIN_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def tokenize(text):
    """純規則式分詞：中文以連續CJK字串做2-gram切分，英文/數字以單字為token。
    不依賴 jieba/CKIP 等額外NLP套件（見 RESEARCH.md #7，v2再評估導入）。"""
    if not text:
        return []
    tokens = []
    for run in CJK_RUN_RE.findall(text):
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
    tokens.extend(t.lower() for t in LATIN_TOKEN_RE.findall(text))
    return tokens


def term_frequencies(tokens):
    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    return {term: count / total for term, count in counts.items()}


def build_matrix(documents):
    """建立 TF-IDF term-document matrix。
    documents: List[str]，回傳 (terms, matrix)：
      terms 為排序後的詞彙表；matrix 為每篇文件對應各 term 的 TF-IDF 值 list。"""
    tokenized_docs = [tokenize(doc) for doc in documents]
    doc_freq = Counter()
    for tokens in tokenized_docs:
        doc_freq.update(set(tokens))

    n_docs = len(documents) or 1
    idf = {term: math.log(n_docs / (1 + df)) + 1 for term, df in doc_freq.items()}
    terms = sorted(idf.keys())
    term_index = {term: i for i, term in enumerate(terms)}

    matrix = []
    for tokens in tokenized_docs:
        row = [0.0] * len(terms)
        tf = term_frequencies(tokens)
        for term, freq in tf.items():
            row[term_index[term]] = freq * idf[term]
        matrix.append(row)

    return terms, matrix


def top_keywords(doc_index, terms, matrix, top_n=5):
    """回傳指定文件在 matrix 中權重最高的前 top_n 個詞。"""
    row = matrix[doc_index]
    scored = sorted(zip(terms, row), key=lambda pair: pair[1], reverse=True)
    return [term for term, weight in scored if weight > 0][:top_n]


if __name__ == "__main__":
    sample_docs = [
        "台積電法說會釋出樂觀展望，外資喊買半導體股。",
        "聯發科手機晶片出貨動能強勁，法人上修目標價。",
        "颱風假各縣市停班停課最新消息一次看。",
    ]
    terms, matrix = build_matrix(sample_docs)
    print(f"詞彙表大小: {len(terms)}")
    for i, doc in enumerate(sample_docs):
        print(doc, "->", top_keywords(i, terms, matrix))
