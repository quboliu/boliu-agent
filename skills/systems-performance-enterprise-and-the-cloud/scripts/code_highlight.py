"""Lossless, source-traceable highlighting for recovered listings (Pygments 2.18)."""
import re
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.lexer import RegexLexer
from pygments.token import Token, Text, Comment, Keyword, Name, String, Number, Operator, Punctuation


class TracingLexer(RegexLexer):
    """The shared C-like lexical subset of DTrace and bpftrace, without parsing."""
    tokens = {'root': [
        (r'#![^\n]*', Comment.Preproc), (r'//[^\n]*', Comment.Single),
        (r'/\*.*?\*/', Comment.Multiline),
        (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', String),
        (r'\b(?:BEGIN|END|if|else|while|for|return|break|continue|struct|int|char|void|long|unsigned|inline|self|this)\b', Keyword),
        (r'(?:@[\w]*|\$\w+)', Name.Variable),
        (r'\b(?:printf|print|count|sum|hist|lhist|str|time|exit|delete|ntop|ksym|usym|kstack|ustack|join)\b', Name.Builtin),
        (r'\b(?:tracepoint|kprobe|kretprobe|uprobe|uretprobe|profile|tick|interval|fbt|syscall|pid|usdt|t|k|kr|u|ur):[^\s{,]+', Name.Function),
        (r'\b(?:0x[\da-fA-F]+|\d+(?:\.\d+)?)\b', Number),
        (r'[+*/%=!<>|&?:-]+', Operator), (r'[{}()[\],;.]', Punctuation),
        (r'\s+', Text.Whitespace), (r'\w+', Name), (r'.', Text),
    ]}
    flags = re.MULTILINE | re.DOTALL


def classify(code, source, context):
    first = code.lstrip().splitlines()[0] if code.strip() else ''
    if first.startswith('#!'):
        if 'bpftrace' in first: return 'bpftrace', 'shebang'
        if 'dtrace' in first: return 'dtrace', 'shebang'
        if 'python' in first: return 'python', 'shebang'
        if 'perl' in first: return 'perl', 'shebang'
        return 'bash', 'shebang'
    if re.search(r'(?m)^\s*(?:[#$%] |[^\n]{1,50}[$#] )',code):
        return 'console', 'shell prompt with command/output'
    if re.search(r'\b(?:SELECT|CREATE TABLE|INSERT INTO)\b',code): return 'sql','SQL statement'
    if re.search(r'\b(?:public class|public static|System\.out)\b',code): return 'java','Java declaration'
    if re.search(r'(?m)^\s*(?:#include|typedef|(?:static\s+)?(?:int|void|long|char)\s+(?:__\w+\s+)?\w+\(|struct\s+\w+\s*\{)',code): return 'c','C declaration'
    if first.startswith('/*') and not source.startswith('015-'): return 'c','C comment'
    if re.match(r'^\*/\d+.*\bcommand\b',first): return 'bash','cron shell command'
    if first.startswith('write: dd') or first.startswith('To free pagecache:'):return 'bash','annotated shell commands'
    if source.startswith('015-') and not re.match(r'^(?:bpftrace |sudo |\./)', first):
        if re.search(r'@[\w]*|\$\w+|\b(?:BEGIN|END|printf|probe|probes|actions|action|if|while)\b|^/|^//|^/\*|^(?:kprobe|uprobe):|type:identifier|test \? true',code):
            return 'bpftrace','bpftrace chapter syntax'
    if re.search(r'(?m)^\s*(?:tracepoint:|kprobe:|profile:|BEGIN\s*\{|@\w|/args->|lhist\()',code): return 'bpftrace','tracing syntax'
    if 'DTrace' in context and re.search(r'(?m)^\s*(?:fbt:|syscall:|pid\$|self->|this->|/|\{)|\b(?:quantize|llquantize|aggregation)\b',code):return 'dtrace','DTrace context and syntax'
    if re.search(r'\b(?:kmem_alloc|kmem_cache_alloc|futex|open|read|stat|lseek)\(',code):return 'c','C calls/trace'
    if re.match(r'^(?:perf|bpftrace|export|echo|cat|sudo|e2fsck|dd|dtrace|ftrace|funccount|funcgraph|stackcount|trace|argdist(?:\.py)?|execsnoop|opensnoop|biosnoop|biolatency|runqlat|runqlen|profile|offcputime|offwaketime|wakeuptime|cachestat|cachetop|tcpconnect|tcplife|tcptop|tcpaccept|tcpretrans|funcslower|functrace|kprobe|tpoint|uprobe|taskset|sysctl|numactl|mpstat|vmstat|sar|iostat|pidstat|cpupower|time|python|perl|awk|grep|find|make|gcc|java|ls|cd|chmod|chown|kill|mount|umount|ip|ethtool|sysbench|stress|fio|curl|wget|apt|yum|git|systemctl)\b|^\./',first): return 'bash','command without prompt'
    if re.search(r'(?m)^\s*(?:for\s+\w+\s+in\b|while\s|done\b|fi\b|export\s)',code):return 'bash','shell control flow'
    if re.search(r'(?m)^\s*net\.(?:core|ipv4)\.',code):return 'ini','sysctl configuration'
    return 'text','literal output, stack, configuration or notation'


def color(token):
    if token in Comment:return '#64748b'
    if token in String:return '#216e39'
    if token in Number:return '#915600'
    if token in Keyword:return '#7540a0'
    if token in Name.Builtin or token in Name.Function:return '#075985'
    if token in Name.Variable:return '#9c2f52'
    if token in Token.Generic.Prompt:return '#075985'
    if token in Operator:return '#7540a0'
    return '#20252b'


def command_names(tokens, language):
    if language not in ('bash', 'console'): return tokens
    result = []
    waiting = language == 'bash'
    for token, value in tokens:
        if token in Token.Generic.Prompt:
            waiting = True
            result.append((token, value))
            continue
        if waiting and token not in Text.Whitespace and value.strip():
            match = re.match(r'^(\s*)([A-Za-z_./][\w./-]*)(.*)$', value, re.S)
            if match and token not in String and token not in Comment and token not in Keyword:
                space, name, rest = match.groups()
                if space: result.append((Text.Whitespace, space))
                result.append((Name.Function, name))
                if rest: result.append((token, rest))
                waiting = name == 'sudo' and not rest.strip()
            else:
                result.append((token, value))
                waiting = False
        else:
            result.append((token, value))
        if language == 'bash' and '\n' in value and not value.rsplit('\n', 1)[1].strip():
            waiting = True
    return result


def highlight(code, language):
    lexer=TracingLexer(stripnl=False,ensurenl=False) if language in ('bpftrace','dtrace') else get_lexer_by_name(language,stripnl=False,ensurenl=False)
    tokens=list(lex(code + '\n',lexer))
    # Session lexers consume only complete lines; trim just the added terminator.
    if tokens and tokens[-1][1].endswith('\n'):
        token, value = tokens[-1]
        tokens[-1] = (token, value[:-1])
    tokens = command_names(tokens, language)
    if ''.join(value for _,value in tokens)!=code:raise ValueError('Highlighter altered listing bytes')
    rows=[[]]
    for token,value in tokens:
        chunks=value.split('\n')
        for i,chunk in enumerate(chunks):
            if i:rows.append([])
            if chunk:rows[-1].append([color(token),chunk])
    return rows
