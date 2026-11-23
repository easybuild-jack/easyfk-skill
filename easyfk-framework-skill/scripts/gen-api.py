#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 easyfk 源码生成「API 签名速查」文档（给 skill 读取用）。

用法（绝对路径）：
    python "D:\\...\\easyfk-framework-skill\\scripts\\gen-api.py" \
        --version 3.2.12 \
        --repo-root "D:\\othercodespace\\easybuild\\3.2.12" \
        [--skill-root "D:\\...\\easyfk-framework-skill"]

产物：
    <skill-root>/versions/<version>/api/<模块>.api.md
    <skill-root>/versions/<version>/api/INDEX.md

设计要点：
- 只提取 public / protected 成员（接口、枚举、注解类型的成员视为 public）；
- 签名文本直接取自源码，保留原始泛型、注解、throws；
- 常量与枚举值保留初始化表达式，javadoc 摘要作为行尾注释；
- 类上带 Lombok 注解时显式标注（否则读的人以为没有 getter）；
- @ConfigurationProperties 类额外汇总「配置项」小节。
脚本只读源码，不编译、不修改源码。
"""

import argparse
import bisect
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 模块映射
# api 文件名 -> (模块坐标说明, [相对 repo-root 的源码模块目录])
MODULES = [
    ("easyfk-core", "com.mcst:easyfk-core", ["easyfk-base/easyfk-core"]),
    ("easyfk-serializer", "com.mcst:serializer-base、com.mcst:serializer-fory",
     ["easyfk-base/easyfk-serializer/serializer-base", "easyfk-base/easyfk-serializer/serializer-fory"]),
    ("easyfk-thread", "com.mcst:easyfk-thread", ["easyfk-base/easyfk-thread"]),
    ("easyfk-queue", "com.mcst:queue-disruptor", ["easyfk-base/easyfk-queue/queue-disruptor"]),
    ("easyfk-cache", "com.mcst:easyfk-cache", ["easyfk-base/easyfk-cache"]),
    ("easyfk-repository", "com.mcst:easyfk-repository", ["easyfk-base/easyfk-repository"]),
    ("easyfk-service", "com.mcst:service-api、com.mcst:service-base",
     ["easyfk-base/easyfk-service/service-api", "easyfk-base/easyfk-service/service-base"]),
    ("easyfk-remote", "com.mcst:remote-cloud、com.mcst:remote-dubbo",
     ["easyfk-base/easyfk-remote/remote-cloud", "easyfk-base/easyfk-remote/remote-dubbo"]),
    ("easyfk-web", "com.mcst:web-simple、web-base、web-common、web-prd、web-micro",
     ["easyfk-base/easyfk-web/web-simple", "easyfk-base/easyfk-web/web-base",
      "easyfk-base/easyfk-web/web-common", "easyfk-base/easyfk-web/web-prd",
      "easyfk-base/easyfk-web/web-micro"]),
    ("easyfk-authority", "com.mcst:easyfk-authority", ["easyfk-base/easyfk-authority"]),
    ("easyfk-gateway", "com.mcst:easyfk-gateway", ["easyfk-base/easyfk-gateway"]),
    ("easyfk-component-db", "com.mcst:db-redis、db-mongo、db-clickhouse、db-influx",
     ["easyfk-component/component-db/db-redis", "easyfk-component/component-db/db-mongo",
      "easyfk-component/component-db/db-clickhouse", "easyfk-component/component-db/db-influx"]),
    ("easyfk-component-cache", "com.mcst:cache-redis、cache-caffeine、cache-mult",
     ["easyfk-component/component-cache/cache-redis", "easyfk-component/component-cache/cache-caffeine",
      "easyfk-component/component-cache/cache-mult"]),
    ("easyfk-component-autoId", "com.mcst:autoId-api、autoId-redis",
     ["easyfk-component/component-autoId/autoId-api", "easyfk-component/component-autoId/autoId-redis"]),
    ("easyfk-component-lock", "com.mcst:lock-redisson", ["easyfk-component/component-lock/lock-redisson"]),
    ("easyfk-component-orm", "com.mcst:orm-mybatis、orm-flex、orm-hibernate、orm-sharding",
     ["easyfk-component/component-orm/orm-mybatis", "easyfk-component/component-orm/orm-flex",
      "easyfk-component/component-orm/orm-hibernate", "easyfk-component/component-orm/orm-sharding"]),
    ("easyfk-component-mq", "com.mcst:mq-common、mq-rocket、mq-rabbit、mq-kafka",
     ["easyfk-component/component-mq/mq-common", "easyfk-component/component-mq/mq-rocket",
      "easyfk-component/component-mq/mq-rabbit", "easyfk-component/component-mq/mq-kafka"]),
    ("easyfk-component-rpc", "com.mcst:rpc-cloud、rpc-dubbo",
     ["easyfk-component/component-rpc/rpc-cloud", "easyfk-component/component-rpc/rpc-dubbo"]),
    ("easyfk-component-chronicle", "com.mcst:chronicle-map、chronicle-queue",
     ["easyfk-component/component-chronicle/chronicle-map", "easyfk-component/component-chronicle/chronicle-queue"]),
    ("easyfk-component-websocket", "com.mcst:websocket-server、websocket-api",
     ["easyfk-component/component-websocket/websocket-server", "easyfk-component/component-websocket/websocket-api"]),
    ("easyfk-component-job", "com.mcst:job-xxl", ["easyfk-component/component-job/job-xxl"]),
    # 独立工程：源码需单独检出到同一 repo-root 下
    ("easyfk-aeron", "com.mcst:aeron-common、aeron-producer、aeron-consumer、aeron-store、"
                     "aeron-chronicle、aeron-codec-*、aeron-compression-*、aeron-metrics-micrometer、"
                     "aeron-spring-boot-starter",
     ["easyfk-aeron/aeron-common", "easyfk-aeron/aeron-driver", "easyfk-aeron/aeron-producer",
      "easyfk-aeron/aeron-producer-outbox", "easyfk-aeron/aeron-consumer", "easyfk-aeron/aeron-store",
      "easyfk-aeron/aeron-chronicle", "easyfk-aeron/aeron-codec-fory", "easyfk-aeron/aeron-codec-json",
      "easyfk-aeron/aeron-codec-protobuf", "easyfk-aeron/aeron-codec-sbe",
      "easyfk-aeron/aeron-compression-lz4", "easyfk-aeron/aeron-compression-zstd",
      "easyfk-aeron/aeron-metrics-micrometer", "easyfk-aeron/aeron-spring-boot-starter"]),
    ("aeron-cluster", "com.mcst:aeron-cluster-core、aeron-cluster-client、aeron-cluster-spring-boot-starter",
     ["aeron-cluster/aeron-cluster-core", "aeron-cluster/aeron-cluster-client",
      "aeron-cluster/aeron-cluster-spring-boot-starter", "aeron-cluster/aeron-cluster-test"]),
    ("etcd-cluster", "com.mcst:etcd-cluster-api、etcd-cluster-core、etcd-cluster-spring-boot-starter",
     ["etcd-cluster/etcd-cluster-api", "etcd-cluster/etcd-cluster-core",
      "etcd-cluster/etcd-cluster-spring-boot-starter"]),
]

# 生成范围说明（渲染进 INDEX）
MODULE_NOTES = {
    "easyfk-aeron": "`aeron-examples` 是示例工程，不参与 API 提取；示例用法见模块文档与 `manuals/easyfk-aeron/`。",
}

# 已下线的子模块：所有版本快照都不再收录（源码里可能还在，但框架不再提供）
# （cache-mult 多级缓存、db-influx 时序库）
REMOVED_MODULES = {"cache-mult", "db-influx"}


def trim_removed(dirs, coords: str):
    """裁掉 REMOVED_MODULES 里的子模块，并同步清理坐标说明。"""
    removed = {Path(d).name for d in dirs if Path(d).name in REMOVED_MODULES}
    if not removed:
        return dirs, coords
    kept = [d for d in dirs if Path(d).name not in removed]
    parts = [p for p in coords.split("、") if p.rsplit(":", 1)[-1] not in removed]
    return kept, "、".join(parts)


# 没有 Java 源码（纯配置 / 纯依赖聚合 / 源码不在本检出中）的模块，在 INDEX 中说明
NO_SOURCE_NOTE = {
    "easyfk-log": "`log-logback` / `log-log4j2` 只含日志配置文件，没有 Java API；配置项见 [../modules/easyfk-log-skill.md](../modules/easyfk-log-skill.md)。",
    "easyfk-component-ds": "`ds-druid` 只做依赖聚合，没有自有 Java API；使用 Druid 官方配置。",
    "easyfk-component-infra": "`config-nacos` / `registry-nacos` / `protect-sentinel` / `transaction-seata` / `doc-knife4j` 只做依赖聚合，没有自有 Java API。",
    "easyfk-dependencies": "BOM 工程，只有版本约束，没有 Java API；版本清单见 [../modules/easyfk-dependencies-skill.md](../modules/easyfk-dependencies-skill.md)。",
}

MODIFIERS = {
    "public", "protected", "private", "static", "final", "abstract", "sealed",
    "non-sealed", "transient", "volatile", "synchronized", "native", "strictfp",
    "default",
}
TYPE_KEYWORDS = {"class", "interface", "enum", "record"}
LOMBOK_HINTS = {"Data", "Getter", "Setter", "Value", "Builder", "SuperBuilder",
                "Accessors", "NoArgsConstructor", "AllArgsConstructor",
                "RequiredArgsConstructor", "ToString", "EqualsAndHashCode"}
# 这些 Lombok 注解会为私有字段生成 getter/setter，字段名即 API
FIELD_REVEALING_LOMBOK = {"Data", "Getter", "Setter", "Value", "Builder",
                          "SuperBuilder", "Accessors"}

TOKEN_RE = re.compile(r"""
      (?P<ws>\s+)
    | (?P<str>\"\"\"[\s\S]*?\"\"\"|\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')
    | (?P<ident>[A-Za-z_$][\w$]*)
    | (?P<num>\d[\w.]*)
    | (?P<op>.)
""", re.X)


# ---------------------------------------------------------------- 预处理
def mask_comments(src: str):
    """把注释替换成等长空格，返回 (masked, comments[(start,end,text)])。字符串原样保留。"""
    out = list(src)
    comments = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == '"' or c == "'":
            if src.startswith('"""', i):
                j = src.find('"""', i + 3)
                i = n if j < 0 else j + 3
                continue
            j = i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == c:
                    j += 1
                    break
                if src[j] == '\n':
                    break
                j += 1
            i = j
            continue
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            comments.append((i, j, src[i:j]))
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            comments.append((i, j, src[i:j]))
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out), comments


def tokenize(masked: str):
    toks = []
    for m in TOKEN_RE.finditer(masked):
        kind = m.lastgroup
        if kind == "ws":
            continue
        toks.append((kind, m.group(), m.start(), m.end()))
    return toks


def javadoc_summary(text: str, maxlen: int = 110) -> str:
    body = text.strip()
    if body.startswith("/**"):
        body = body[3:]
    if body.endswith("*/"):
        body = body[:-2]
    lines = []
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("*"):
            line = line[1:].strip()
        if line.startswith("@"):
            break
        lines.append(line)
    # 取第一段
    para = []
    for line in lines:
        if not line:
            if para:
                break
            continue
        para.append(line)
    s = " ".join(para).strip()
    # 清理 javadoc 内联标签
    s = re.sub(r"\{@code\s+([^}]*)\}", r"\1", s)
    s = re.sub(r"\{@literal\s+([^}]*)\}", r"\1", s)
    s = re.sub(r"\{@link(?:plain)?\s+([^}]*)\}",
               lambda m: re.split(r"[#.]", m.group(1))[-1], s)
    s = re.sub(r"\{@\w+\s*([^}]*)\}", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > maxlen:
        cut = s[:maxlen]
        for sep in ("。", "；", "，", ". ", "; "):
            pos = cut.rfind(sep)
            if pos > maxlen // 2:
                cut = cut[:pos]
                break
        s = cut.rstrip("，,、；;. ") + "…"
    return s


def tidy(s: str) -> str:
    """压缩空白并修掉换行折叠产生的多余空格。"""
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    s = re.sub(r"<\s+", "<", s)
    s = re.sub(r"\s+>", ">", s)
    s = re.sub(r"\[\s+", "[", s)
    s = re.sub(r"\s+\]", "]", s)
    return s.strip()


def collapse(s: str) -> str:
    return tidy(s)


# ---------------------------------------------------------------- 解析
class TypeInfo:
    def __init__(self):
        self.kind = ""
        self.name = ""
        self.header = ""        # public class Foo<T> extends Bar
        self.full = ""          # 含外部类前缀
        self.annotations = []
        self.doc = ""
        self.members = []       # list of MemberInfo
        self.nested = []        # list of TypeInfo
        self.record_components = []
        self.is_config_props = False
        self.prefix = ""
        self.is_public = True

    @property
    def is_public_api(self):
        return True


class MemberInfo:
    def __init__(self):
        self.kind = ""          # field | method | ctor | enumconst | init
        self.sig = ""
        self.name = ""
        self.doc = ""
        self.annotations = []
        self.modifiers = []
        self.value = ""
        self.visible = True


class Parser:
    def __init__(self, src: str, path: str):
        self.raw = src
        self.masked, self.comments = mask_comments(src)
        self.toks = tokenize(self.masked)
        self.i = 0
        self.path = path
        self._cend = [c[1] for c in self.comments]
        self.package = ""
        self.imports = []

    # -- 基础操作
    def peek(self, k=0):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else (None, None, -1, -1)

    def at(self, text, k=0):
        t = self.peek(k)
        return t[1] == text

    def text(self, k=0):
        return self.peek(k)[1]

    def advance(self, k=1):
        self.i += k

    def slice(self, a, b):
        return self.masked[a:b]

    def doc_before(self, pos):
        idx = bisect.bisect_right(self._cend, pos) - 1
        while idx >= 0:
            cs, ce, ctext = self.comments[idx]
            if self.masked[ce:pos].strip() == "":
                if ctext.startswith("/**"):
                    return javadoc_summary(ctext)
                return ""
            return ""
        return ""

    # -- 编译单元
    def parse_unit(self):
        types = []
        while self.i < len(self.toks):
            t = self.text()
            if t == "package":
                self.advance()
                buf = []
                while self.i < len(self.toks) and self.text() != ";":
                    buf.append(self.text())
                    self.advance()
                self.package = "".join(buf)
                self.advance()
                continue
            if t == "import":
                while self.i < len(self.toks) and self.text() != ";":
                    self.advance()
                self.advance()
                continue
            if t in (";", "}"):
                self.advance()
                continue
            ti = self.parse_type(None)
            if ti is None:
                self.advance()
            else:
                types.append(ti)
        return types

    # -- 修饰符与注解
    def parse_mods(self):
        """返回 (注解列表, 修饰符列表[保持源码顺序], 首个修饰符位置 / 首个声明 token 位置)。"""
        anns, mods = [], []
        mods_start = None
        while self.i < len(self.toks):
            t = self.text()
            if t == "@":
                if self.at("interface", 1):
                    break
                start = self.peek()[2]
                self.advance()
                if self.peek()[0] == "ident":
                    self.advance()
                while self.at("."):
                    self.advance()
                    if self.peek()[0] == "ident":
                        self.advance()
                if self.at("("):
                    depth = 0
                    while self.i < len(self.toks):
                        tk = self.text()
                        if tk == "(":
                            depth += 1
                        elif tk == ")":
                            depth -= 1
                            if depth == 0:
                                self.advance()
                                break
                        self.advance()
                anns.append(collapse(self.slice(start, self.peek(-1)[3])))
                continue
            if t in MODIFIERS:
                if mods_start is None:
                    mods_start = self.peek()[2]
                mods.append(t)
                self.advance()
                continue
            break
        return anns, mods, mods_start

    def parse_type(self, outer: str):
        start = self.peek()[2]
        anns, mods, mods_start = self.parse_mods()
        t = self.text()
        if t == "@" and self.at("interface", 1):
            kind = "@interface"
            decl_start = self.peek()[2]
            self.advance(2)
        elif t in TYPE_KEYWORDS:
            kind = t
            decl_start = self.peek()[2]
            self.advance()
        else:
            return None
        if self.peek()[0] != "ident":
            return None
        name = self.text()
        self.advance()
        # header 到 '{'
        depth = 0
        hstart = self.peek()[2]
        while self.i < len(self.toks):
            tk = self.text()
            if tk in ("(", "["):
                depth += 1
            elif tk in (")", "]"):
                depth -= 1
            elif tk == "{" and depth == 0:
                break
            self.advance()
        hend = self.peek()[2]
        header_extra = collapse(self.slice(hstart, hend))
        header = collapse(self.slice(mods_start if mods_start is not None else decl_start, hend))
        ti = TypeInfo()
        ti.kind = kind
        ti.name = name
        ti.is_public = "public" in mods
        ti.full = f"{outer}.{name}" if outer else name
        ti.header = header
        ti.annotations = anns
        ti.doc = self.doc_before(start)
        for a in anns:
            if a.startswith("@ConfigurationProperties"):
                ti.is_config_props = True
                # prefix 可能是字面量，也可能引用常量（如 AeronProperties.PREFIX）
                m = re.search(r'@ConfigurationProperties\(\s*(?:prefix\s*=\s*)?("(?:[^"]*)"|[\w$.]+)',
                              a)
                ti.prefix = m.group(1) if m else ""
        if kind == "record":
            m = re.search(r"\((.*)\)", header_extra, re.S)
            if m:
                for part in split_top(m.group(1), ","):
                    part = part.strip()
                    if part:
                        ti.record_components.append(collapse(part))
        # 进入 body
        if self.at("{"):
            self.advance()
            self.parse_body(ti)
        return ti

    def parse_body(self, ti: TypeInfo):
        if ti.kind == "enum":
            self.parse_enum_constants(ti)
        while self.i < len(self.toks):
            if self.at("}"):
                self.advance()
                return
            if self.at(";"):
                self.advance()
                continue
            self.parse_member(ti)

    def parse_enum_constants(self, ti: TypeInfo):
        while self.i < len(self.toks):
            if self.at(";"):
                self.advance()
                return
            if self.at("}"):
                return
            start = self.peek()[2]
            anns, _, _ = self.parse_mods()
            if self.peek()[0] != "ident":
                return
            name = self.text()
            self.advance()
            extra = ""
            if self.at("("):
                s = self.peek()[2]
                self.skip_balanced("(", ")")
                extra = collapse(self.slice(s, self.peek(-1)[3]))
            if self.at("{"):
                self.skip_balanced("{", "}")
            mi = MemberInfo()
            mi.kind = "enumconst"
            mi.name = name
            mi.sig = f"{name}{extra}"
            mi.doc = self.doc_before(start)
            ti.members.append(mi)
            if self.at(","):
                self.advance()
                continue
            return

    def skip_balanced(self, open_t, close_t):
        depth = 0
        while self.i < len(self.toks):
            tk = self.text()
            if tk == open_t:
                depth += 1
            elif tk == close_t:
                depth -= 1
                if depth == 0:
                    self.advance()
                    return
            self.advance()

    def parse_member(self, ti: TypeInfo):
        start = self.peek()[2]
        anns, mods, mods_start = self.parse_mods()
        if self.i >= len(self.toks):
            return
        t = self.text()
        if t == "@" and self.at("interface", 1) or t in TYPE_KEYWORDS:
            # 嵌套类型：回退到注解/修饰符起点重新解析
            self.rewind_to(start)
            nested = self.parse_type(ti.full)
            if nested is not None:
                ti.nested.append(nested)
            return
        # 静态/实例初始化块
        if t == "{":
            self.skip_balanced("{", "}")
            return
        # 收集 header
        hstart = self.peek()[2]
        depth = 0
        has_paren = False
        has_eq = False
        hend = None
        while self.i < len(self.toks):
            tk = self.text()
            if tk in ("(", "["):
                depth += 1
                if tk == "(":
                    has_paren = True
            elif tk in (")", "]"):
                depth -= 1
            elif tk == "=" and depth == 0:
                has_eq = True
            elif tk == ";" and depth == 0:
                hend = self.peek()[2]
                self.advance()
                break
            elif tk == "{" and depth == 0:
                if has_paren and not has_eq:
                    hend = self.peek()[2]
                    self.skip_balanced("{", "}")
                    break
                else:
                    # 数组初始化 / 匿名类 / 非方法块
                    self.skip_balanced("{", "}")
                    continue
            elif tk == "}" and depth == 0:
                hend = self.peek()[2]
                break
            self.advance()
        if hend is None:
            hend = self.peek()[2]
        sig_body = collapse(self.slice(hstart, hend))
        # 保留 static / default / abstract / final 等语义修饰符，去掉访问修饰符
        keep = [m for m in mods if m not in ("public", "protected", "private")]
        sig = ((" ".join(keep) + " " + sig_body).strip() if keep else sig_body)
        if not sig:
            return
        mi = MemberInfo()
        mi.doc = self.doc_before(start)
        mi.annotations = [a for a in anns if a != "@Override"]
        mi.modifiers = mods
        if has_paren and not has_eq:
            mi.kind = "ctor" if re.match(rf"^{re.escape(ti.name)}\s*\(", sig) else "method"
            m = re.search(r"([\w$]+)\s*\(", sig)
            mi.name = m.group(1) if m else ""
            mi.sig = sig
        else:
            mi.kind = "field"
            head, _, val = sig.partition(" = ")
            m = re.search(r"([\w$]+)\s*(=|$)", head)
            names = re.findall(r"([\w$]+)\s*(?:=|$|,)", head)
            mi.name = names[-1] if names else ""
            mi.sig = head.strip()
            mi.value = val.strip()
        visible = ("public" in mods or "protected" in mods
                   or ti.kind in ("interface", "enum", "@interface"))
        if mi.kind == "field" and ti.kind == "interface":
            visible = True
        # Lombok 类（@Data 等）与 @ConfigurationProperties 的私有字段是事实上的 API，
        # 否则读的人看不到字段名和类型。
        if mi.kind == "field" and not visible:
            lom_names = {a[1:].split("(")[0] for a in ti.annotations if a.startswith("@")}
            if ti.is_config_props or (lom_names & FIELD_REVEALING_LOMBOK):
                visible = True
        mi.visible = visible
        if not visible:
            return
        ti.members.append(mi)

    def rewind_to(self, pos):
        for j, tk in enumerate(self.toks):
            if tk[2] == pos:
                self.i = j
                return


def split_top(s: str, sep: str):
    """按顶层分隔符切分（忽略 <> () [] {} 内的分隔符）。"""
    out, buf, depth = [], [], 0
    for ch in s:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


# ---------------------------------------------------------------- 渲染
def collect_types(types, out):
    for ti in types:
        out.append(ti)
        collect_types(ti.nested, out)


def render_member(mi: MemberInfo) -> str:
    ann = ""
    if mi.annotations:
        ann = " ".join(mi.annotations) + " "
    body = mi.sig
    if mi.value:
        body = f"{mi.sig} = {mi.value}"
    line = f"{ann}{body}"
    if mi.doc:
        line = f"{line}  // {mi.doc}"
    return line


def render_type(ti: TypeInfo, level: int, lines: list):
    hashes = "#" * level
    lines.append(f"{hashes} {ti.full}")
    lines.append("")
    head = f"`{ti.header}`"
    lom = [a for a in ti.annotations
           if a.startswith("@") and a[1:].split("(")[0] in LOMBOK_HINTS]
    extra = []
    if lom:
        extra.append("Lombok：" + " ".join(f"`{a}`" for a in lom))
    other = [a for a in ti.annotations
             if a not in lom and a != "@Override"]
    if other:
        extra.append("注解：" + " ".join(f"`{a}`" for a in other))
    if ti.doc:
        extra.append(ti.doc)
    lines.append(head + ("　" + "　".join(extra) if extra else ""))
    lines.append("")

    rows = []
    consts = [m for m in ti.members if m.kind == "enumconst"]
    fields = [m for m in ti.members if m.kind == "field"]
    ctors = [m for m in ti.members if m.kind == "ctor"]
    methods = [m for m in ti.members if m.kind == "method"]

    if ti.kind == "record" and ti.record_components:
        rows.append(("构造参数（record 组件）", ti.record_components))
    if consts:
        rows.append(("枚举常量", [render_member(m) for m in consts]))
    if fields:
        rows.append(("字段 / 常量", [render_member(m) for m in fields]))
    if ctors:
        rows.append(("构造器", [render_member(m) for m in ctors]))
    if methods:
        rows.append(("方法", [render_member(m) for m in methods]))

    if not rows:
        if ti.kind == "@interface":
            lines.append("_标记注解，无属性。_")
        else:
            lines.append("_无 public 成员。_")
        lines.append("")
    for title, items in rows:
        lines.append(f"**{title}**")
        lines.append("")
        lines.append("```java")
        lines.extend(items)
        lines.append("```")
        lines.append("")
    for n in ti.nested:
        if n.is_public:
            render_type(n, level + 1, lines)


def resolve_prefix(ti: TypeInfo) -> str:
    """prefix 可能是字面量，也可能是类内常量引用（AeronProperties.PREFIX）。"""
    p = (ti.prefix or "").strip()
    if not p:
        return "(未声明 prefix)"
    if p.startswith('"'):
        return p.strip('"')
    const_name = p.split(".")[-1]
    for m in ti.members:
        if m.kind == "field" and m.name == const_name and m.value.startswith('"'):
            return m.value.strip('"')
    return p


def render_module(ver: str, api_name: str, coords: str, src_dirs, repo_root: Path,
                  skill_root: Path):
    types = []
    files = []
    for rel in src_dirs:
        base = repo_root / rel / "src" / "main" / "java"
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.java")):
            if p.name in ("package-info.java", "module-info.java"):
                continue
            files.append(p)
            src = p.read_text(encoding="utf-8", errors="replace")
            parser = Parser(src, str(p))
            for ti in parser.parse_unit():
                ti.package = parser.package
                types.append(ti)
    if not types:
        return None, 0, 0

    # 包分组（包级私有类型不是 API，直接跳过）
    types = [ti for ti in types if ti.is_public]
    by_pkg = {}
    for ti in types:
        by_pkg.setdefault(ti.package, []).append(ti)
    n_class = len(types)
    n_method = sum(1 for ti in types for m in ti.members if m.kind in ("method", "ctor"))
    n_field = sum(1 for ti in types for m in ti.members if m.kind in ("field", "enumconst"))

    lines = []
    lines.append(f"# {api_name} API 签名速查（easyfk {ver}）")
    lines.append("")
    lines.append(f"> 坐标：`{coords}`　源码："
                 + "、".join(f"`{d}`" for d in src_dirs))
    lines.append(f"> 由 `scripts/gen-api.py` 从 {len(files)} 个源文件自动提取，"
                 f"共 {n_class} 个类型、{n_method} 个方法/构造器、{n_field} 个字段/枚举常量。")
    lines.append("> **用途**：查精确签名、重载顺序、参数顺序、常量值、配置项。"
                 f"用法、配置示例和注意事项看 [../modules/{api_name}-skill.md](../modules/{api_name}-skill.md)。")
    lines.append("> 只列 public / protected 成员；接口、枚举、注解类型的成员默认 public。"
                 "带 Lombok 注解的类没有显式 getter/setter，按 Lombok 语义理解。")
    lines.append("")
    # 配置项汇总
    cp = [ti for ti in types if ti.is_config_props]
    if cp:
        lines.append("## 配置项（@ConfigurationProperties）")
        lines.append("")
        for ti in cp:
            lines.append(f"### `{resolve_prefix(ti)}` ← {ti.full}")
            lines.append("")
            lines.append("| 字段 | 类型 | 默认值 | 说明 |")
            lines.append("|---|---|---|---|")
            for m in ti.members:
                if m.kind != "field":
                    continue
                # 常量 / 静态字段不是配置项（DEFAULT_XXX 之类），跳过
                if re.fullmatch(r"[A-Z0-9_]+", m.name) or "static" in m.modifiers:
                    continue
                typ = m.sig
                typ = re.sub(r"^(?:(?:static|final|transient|volatile)\s+)+", "", typ)
                m2 = re.search(r"([\w$.<>\[\], ?]+)\s+([\w$]+)$", typ)
                ftype = m2.group(1) if m2 else ""
                fname = m2.group(2) if m2 else m.name
                key = camel_to_kebab(fname)
                default = m.value or "—"
                doc = m.doc.replace("|", "\\|")
                lines.append(f"| `{key}` | `{ftype}` | `{default}` | {doc} |")
            lines.append("")
        lines.append("")

    # 自动配置类清单（来自 META-INF/spring/...AutoConfiguration.imports）
    autos = []
    for rel in src_dirs:
        f = (repo_root / rel / "src" / "main" / "resources" / "META-INF" / "spring"
             / "org.springframework.boot.autoconfigure.AutoConfiguration.imports")
        if f.exists():
            for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    autos.append((rel, ln))
    if autos:
        lines.append("## 自动配置类（引入即生效）")
        lines.append("")
        lines.append("来源：各子模块 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。")
        lines.append("")
        lines.append("| 子模块 | 自动配置类 |")
        lines.append("|---|---|")
        for rel, cls in autos:
            lines.append(f"| `{rel.split('/')[-1]}` | `{cls}` |")
        lines.append("")

    lines.append("## 类型索引")
    lines.append("")
    for pkg in sorted(by_pkg):
        entries = [f"[{ti.full}](#{anchor(ti.full)})"
                   for ti in sorted(by_pkg[pkg], key=lambda x: x.name)]
        chunk = 5
        head = f"- `{pkg}`："
        for i in range(0, len(entries), chunk):
            sep = "" if i == 0 else "  "
            lines.append(head + sep + "、".join(entries[i:i + chunk]))
            head = "  "
    lines.append("")

    for pkg in sorted(by_pkg):
        lines.append(f"## 包 `{pkg}`")
        lines.append("")
        for ti in sorted(by_pkg[pkg], key=lambda x: x.name):
            render_type(ti, 3, lines)

    out_dir = skill_root / "versions" / ver / "api"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{api_name}.api.md"
    out_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_file, n_class, len(files)


def camel_to_kebab(s: str) -> str:
    if re.fullmatch(r"[A-Z0-9_]+", s):          # DEFAULT_SECRET -> default-secret
        return s.replace("_", "-").lower()
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    return s.lower()


def anchor(full: str) -> str:
    s = full.lower()
    s = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", s)
    return s.replace(" ", "-").replace(".", "")


def write_index(ver, skill_root, results):
    modules_dir = skill_root / "versions" / ver / "modules"
    lines = [f"# easyfk {ver} API 签名速查索引", ""]
    lines.append("> 本目录由 `scripts/gen-api.py` 从该版本源码自动提取，**只放签名与常量值**，"
                 "不含用法说明。需要“怎么写、为什么、注意事项”时读 [../modules/](../modules/) 下对应的 skill 文档。")
    lines.append("")
    lines.append("## 什么时候读 API 文档")
    lines.append("")
    lines.append("| 场景 | 读这个 |")
    lines.append("|---|---|")
    lines.append("| 不确定某个类有哪些方法、重载顺序、参数类型 | 本目录对应模块的 `*.api.md` |")
    lines.append("| 需要常量 / 枚举的具体取值（错误码、请求头名、枚举 code） | 同上，看「字段 / 常量」「枚举常量」 |")
    lines.append("| 需要配置项的完整清单和默认值 | 同上，看文首「配置项（@ConfigurationProperties）」 |")
    lines.append("| 需要知道某个注解标在类上还是字段上、有哪些属性 | 同上，注解类型在 `## 包` 下的 `@interface` 条目 |")
    lines.append("| 需要知道引入某个模块后哪些类会自动生效 | 同上，「自动配置类（引入即生效）」 |")
    lines.append("| 需要判断某个能力是否存在（避免凭记忆编 API） | 先查本目录，查不到就是没有 |")
    lines.append("")
    lines.append("## 模块 → API 文件")
    lines.append("")
    lines.append("| 模块 | 坐标 | 类型数 | 源文件数 | API 文档 | 用法文档 |")
    lines.append("|---|---|---|---|---|---|")
    for api_name, coords, n_class, n_file, fname in results:
        usage = modules_dir / f"{api_name}-skill.md"
        usage_link = f"[{api_name}-skill.md](../modules/{api_name}-skill.md)" if usage.exists() else "—"
        if fname:
            lines.append(f"| {api_name} | `{coords}` | {n_class} | {n_file} | "
                         f"[{fname}]({fname}) | {usage_link} |")
        else:
            lines.append(f"| {api_name} | `{coords}` | 0 | 0 | 无 Java API | {usage_link} |")
    lines.append("")
    lines.append("`easyfk-core-toolkit`（工具类选用规则）与 `easyfk-core` 是同一批类，"
                 "签名统一看 [easyfk-core.api.md](easyfk-core.api.md)。")
    lines.append("")
    dropped = []
    for _api, _coords, _dirs in MODULES:
        kept, _ = trim_removed(_dirs, _coords)
        dropped += [Path(d).name for d in _dirs if d not in kept]
    if dropped:
        lines.append("## 已下线的子模块")
        lines.append("")
        lines.append("以下子模块框架已不再提供，`modules/` 用法文档与 `api/` 签名均不收录"
                     "（源码目录里可能还留有代码，但不要在新项目中使用）：")
        lines.append("")
        for name in dropped:
            lines.append(f"- `{name}`")
        lines.append("")
    lines.append("## 没有 Java API 的模块")
    lines.append("")
    for k, v in NO_SOURCE_NOTE.items():
        lines.append(f"- **{k}**：{v}")
    lines.append("")
    if MODULE_NOTES:
        lines.append("## 生成范围说明")
        lines.append("")
        for k, v in MODULE_NOTES.items():
            lines.append(f"- **{k}**：{v}")
        lines.append("")
    lines.append("## 与 modules/ 的关系")
    lines.append("")
    lines.append("| 文档 | 内容 | 可信度 |")
    lines.append("|---|---|---|")
    lines.append("| `modules/*-skill.md` | 模块定位、引入方式、配置、用法、坑、复查记录 | 已逐行对照源码复查 |")
    lines.append("| `api/*.api.md` | 类 / 方法 / 字段 / 枚举常量 / 配置项签名清单 | 脚本从源码提取，签名与源码一致 |")
    lines.append("| `manuals/*` | 框架原厂手册 | 有历史过时内容 |")
    lines.append("")
    lines.append("两者冲突时以源码为准，并修正 `modules/` 中的说明（API 文件重新生成即可）。")
    lines.append("")
    lines.append("## 重新生成")
    lines.append("")
    lines.append("源码有改动、或新增版本快照时，在套件目录下执行（Windows 示例）：")
    lines.append("")
    lines.append("```")
    lines.append(f'python scripts/gen-api.py --version {ver} --repo-root "<该版本源码绝对路径>"')
    lines.append("```")
    lines.append("")
    lines.append("脚本只读源码，覆盖本目录下的 `*.api.md` 与 `INDEX.md`，不改 `modules/`。")
    lines.append("新增或改名模块时，同步修改脚本顶部的 `MODULES` 映射表。")
    lines.append("")
    lines.append("`easyfk-aeron`、`aeron-cluster`、`etcd-cluster` 是各自独立的 Git 仓库，"
                 "需分别检出到同一个 `repo-root` 下（目录名与映射表一致），否则这三个模块会被跳过。")
    lines.append("")
    out = skill_root / "versions" / ver / "api" / "INDEX.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--skill-root", default=None)
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if args.skill_root:
        skill_root = Path(args.skill_root).resolve()
    else:
        skill_root = Path(__file__).resolve().parent.parent
    if not (repo_root / "easyfk-base").exists():
        print(f"源码目录不正确（找不到 easyfk-base）：{repo_root}", file=sys.stderr)
        return 1

    results = []
    for api_name, coords, dirs in MODULES:
        dirs, coords = trim_removed(dirs, coords)
        if not dirs:
            print(f"{api_name:32s}    0 types     0 files  (无源码)")
            continue
        out, n_class, n_file = render_module(args.version, api_name, coords, dirs,
                                             repo_root, skill_root)
        results.append((api_name, coords, n_class, n_file, out.name if out else None))
        print(f"{api_name:32s} {n_class:4d} types  {n_file:4d} files  "
              f"{out.name if out else '(none)'}")
    # 无源码模块也占位，保证 INDEX 覆盖所有 modules 文档
    for name in NO_SOURCE_NOTE:
        if name not in {r[0] for r in results}:
            results.append((name, "—", 0, 0, None))
    idx = write_index(args.version, skill_root, results)
    print(f"\nINDEX -> {idx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
