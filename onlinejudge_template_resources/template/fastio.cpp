<%!
    import onlinejudge_template.generator.cplusplus as cplusplus
    from typing import List
    def fast_input(exprs: List[str]) -> List[str]:
        lines = []
        for expr in exprs:
            lines.append(f"""{expr} = in<int>();""")
        return lines
    def fast_output(exprs: List[str], *, newline: bool) -> List[str]:
        lines = []
        for i, expr in enumerate(exprs):
            if i:
                lines.append("out<char>(' ');")
            lines.append(f"""out<int>({expr});""")
        if newline:
            lines.append("out<char>('\\n');")
        return lines
%>\
<%
    data['config']['rep_macro'] = 'REP'
    data['config']['scanner'] = fast_input
    data['config']['printer'] = fast_output
%>\
#include <bits/stdc++.h>
using namespace std;

template <class Char, std::enable_if_t<std::is_same_v<Char, char>, int> = 0>
inline Char in() { return getchar_unlocked(); }
template <class String, std::enable_if_t<std::is_same_v<String, std::string>, int> = 0>
inline std::string in() {
    char c; do { c = getchar_unlocked(); } while (isspace(c));
    std::string s;
    do { s.push_back(c); } while (not isspace(c = getchar_unlocked()));
    return s;
}
template <class Integer, std::enable_if_t<std::is_integral_v<Integer>, int> = 0>
inline Integer in() {
    char c; do { c = getchar_unlocked(); } while (isspace(c));
    if (std::is_signed<Integer>::value and c == '-') return -in<Integer>();
    Integer n = 0;
    do { n = n * 10 + c - '0'; } while (not isspace(c = getchar_unlocked()));
    return n;
}

template <class Char, std::enable_if_t<std::is_same_v<Char, char>, int> = 0>
inline void out(char c) { putchar_unlocked(c); }
template <class String, std::enable_if_t<std::is_same_v<String, std::string>, int> = 0>
inline void out(const std::string & s) { for (char c : s) putchar_unlocked(c); }
template <class Integer, std::enable_if_t<std::is_integral_v<Integer>, int> = 0>
inline void out(Integer n) {
    char s[20];
    int i = 0;
    if (std::is_signed<Integer>::value and n < 0) { putchar_unlocked('-'); n *= -1; }
    do { s[i ++] = n % 10; n /= 10; } while (n);
    while (i) putchar_unlocked(s[-- i] + '0');
}

${cplusplus.declare_constants(data)}
${cplusplus.return_type(data)} solve(${cplusplus.formal_arguments(data)}) {
    // TODO: edit here
}

// generated by online-judge-template-generator (https://github.com/kmyk/online-judge-template-generator)
int main() {
${cplusplus.read_input(data)}
    auto ${cplusplus.return_value(data)} = solve(${cplusplus.actual_arguments(data)});
${cplusplus.write_output(data)}
    return 0;
}
