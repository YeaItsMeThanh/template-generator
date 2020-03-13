# Online Judge Template Generator

テンプレートとかディレクトリとかを作ってくれるやつです。まだ不安定版なので、嘘が出力されてても怒らないでね


## How to Install

``` console
$ pip3 install git+https://github.com/kmyk/online-judge-template-generator.git@master
```

(後でやる: PyPI への登録)


## Usage

``` console
$ oj-template [-t template] URL
```

``` console
$ oj-contest URL
```

-   入力解析は AtCoder と yukicoder と [Library Checker](https://judge.yosupo.jp/) にのみ対応。型の認識はまだ
-   出力解析も AtCoder と yukicoder と [Library Checker](https://judge.yosupo.jp/) で動くけど、原理的に対応してる問題が少ない
-   サンプルの一括ダウンロードは [oj](https://github.com/kmyk/online-judge-tools) が動くやつなら全部動く


## Settings

`oj-template` のためのテンプレートは `~/.config/online-judge-tools/template/` の下に `~/.config/online-judge-tools/template/customized.py` のように作って `oj-template -t customized.py https://...` のように指定する。
テンプレート記法は [Mako](https://www.makotemplates.org/) のものを使う。
[fastio.cpp](https://github.com/kmyk/online-judge-template-generator/blob/master/onlinejudge_template_resources/fastio.cpp) とか [customize_sample.cpp](https://github.com/kmyk/online-judge-template-generator/blob/master/onlinejudge_template_resources/customize_sample.cpp) とかを見てそれっぽく書けば動く。

`oj-contest` の設定は `~/.config/online-judge-tools/oj2.config.toml` に次のように設定する。

``` toml
problem_directory = "~/{service_domain}/{contest_id}/{problem_id}"

[templates]
"main.cpp" = "template.cpp"
"generate.py" = "generate.py"
```

(まだ不安定版であり、設定等の後方互換性は保証されません)


## Example

``` console
$ oj-contest https://atcoder.jp/contests/abc158
...

$ tree ~/atcoder.jp
/home/ubuntu/atcoder.jp
└── abc158
    ├── abc158_a
    │   ├── generate.py
    │   ├── main.cpp
    │   └── test
    │       ├── sample-1.in
    │       ├── sample-1.in
    │       ├── sample-1.out
    │       ├── sample-2.in
    │       ├── sample-2.out
    │       ├── sample-3.in
    │       └── sample-3.out
    ├── ...
    ├── ...
    ├── ...
    ├── ...
    └── abc158_f
        ├── generate.py
        ├── main.cpp
        └── test
            ├── sample-1.in
            ├── sample-1.out
            ├── sample-2.in
            ├── sample-2.out
            ├── sample-3.in
            ├── sample-3.out
            ├── sample-4.in
            └── sample-4.out

13 directories, 50 files

$ cat ~/atcoder.jp/abc158/abc158_f/main.cpp
#include <bits/stdc++.h>
#define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
#define REP3(i, m, n) for (int i = (m); (i) < (int)(n); ++ (i))
#define REP_R(i, n) for (int i = (int)(n) - 1; (i) >= 0; -- (i))
#define REP3R(i, m, n) for (int i = (int)(n) - 1; (i) >= (int)(m); -- (i))
#define ALL(x) ::std::begin(x), ::std::end(x)
using namespace std;

auto solve(int N, const vector<int> & X, const vector<int> & D) {
    // TODO: edit here
}

// generated by online-judge-template-generator
int main() {
    int N;
    scanf("%d", &N);
    vector<int > X(N), D(N);
    REP (i, N) {
        scanf("%d%d", &X[i], &D[i]);
    }
    auto ans = solve(N, X, D);
    printf("%d\n", ans);  // TODO: edit here
    return 0;
}

$ cat ~/atcoder.jp/abc158/abc158_f/generate.py
#!/usr/bin/env python3
import random
import onlinejudge_random as random_oj

def main():
    N = random.randint(1, 10 ** 9)  # TODO: edit here
    X = [None for _ in range(N)]
    D = [None for _ in range(N)]
    for i in range(N):
        X[i] = random.randint(1, 10 ** 9)  # TODO: edit here
        D[i] = random.randint(1, 10 ** 9)  # TODO: edit here
    print(N)
    for i in range(N):
        print(X[i], D[i])

if __name__ == "__main__":
    main()
```


## Architecture

1.  download and recognize HTML with [requests](https://requests.readthedocs.io/en/master/) + [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
1.  parse the `<pre>` format in old style Lex + Yacc ([ply](http://www.dabeaz.com/ply/))
1.  generate codes with a template engine ([Mako](https://www.makotemplates.org/))


## How it works

たとえば Library Checker の問題 [Static RQM](https://judge.yosupo.jp/problem/staticrmq) について考えてみましょう。
この問題の入力フォーマットは次のようになっています。

```
n m
a₀ a₁ … aₙ₋₁
l₁ r₁
⋮
lₘ rₘ
```

これをまず以下のようなトークン列に分解します。
愚直に貪欲をするだけで、やばい規則もないのでほぼ O(n) です。正規表現で便利に書ける既存のツールがあるのでこれを利用しています。

``` json
[
    "ident(n)", "ident(m)", "newline()",
    "ident(a)", "subscript()", "number(0)", "ident(a)", "subscript()", "number(1)", "dots()", "ident(a)", "subscript()", "ident(n)", "binop(-)", "number(1)", "newline()",
    "ident(l)", "subscript()", "number(1)", "ident(r)", "subscript()", "number(1)", "newline()",
    "vdots(1)", "newline()",
    "ident(l)", "subscript()", "ident(m)", "ident(r)", "subscript()", "ident(m)", "newline()"
]
```

このトークン列を解析して次のような木へ変形します。
まず文脈自由文法で解析できる範囲を処理した後に、文脈依存ぽい部分を ad-hoc に処理しています。
文脈自由部分は O(n^3) の愚直な区間 DP (CYK法) でもよいですが、規則を列挙すれば残りをいい感じにやってくれる既存のツール (Yacc) に任せてほぼ線形 (LALR法) で実装されています。

``` json
[
    {"type": "var", "name": "n"},
    {"type": "var", "name": "m"},
    {"type": "newline"},
    {"type": "loop", "counter": "i", "size": "n", "body": [
        {"type": "var", "name": "a", "subscript": "i"}
    ]},
    {"type": "newline"},
    {"type": "loop", "counter": "j", "size": "m", "body": [
        {"type": "var", "name": "l", "subscript": "j + 1"},
        {"type": "var", "name": "r", "subscript": "j + 1"},
        {"type": "newline"}
    ]}
]
```

この木を変換してソースコードにします。
木の畳み込みとか木 DP とか言われる O(n) か O(n²) ぐらいの愚直をします。

``` c++
    int n, m;
    scanf("%d%d", &n, &m);
    std::vector<int> a(n);
    for (int i = 0; i < n; ++i) {
        scanf("%d", &a[i]);
    }
    std::vector<int> l(m), r(m);
    for (int j = 0; j < m; ++j) {
        scanf("%d%d", &l[j], &r[j]);
    }
```

この一連の作業をよろしくやってくれるのがこのツールです。


## License

MIT
