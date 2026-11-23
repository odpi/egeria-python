#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Generate md_processing/md_processing_utils/properties_class_fields.py from Egeria's Java source:
for every open-metadata framework Properties class, its kind (relationship, classification, entity
or other, from the root of its superclass chain) and the JSON property names it reads, inherited
ones included.

Egeria's RelationshipProperties, ClassificationProperties and EntityProperties are polymorphic
(`@JsonTypeInfo(property="class")`): a value sent without a "class" is a 400, and a property the
named class doesn't declare is silently ignored (`ignoreUnknown=true`). Dr.Egeria uses this table to
build the typed bodies (parent relationship properties, initial/replacement classifications,
template replacement properties) and to report every key it can't send.

The keys are what Jackson binds: the beans say `setterVisibility=PUBLIC_ONLY, fieldVisibility=NONE`,
so a key is a public one-argument `setX` (named as Jackson does by default: setURL is "url"), or its
`@JsonProperty` name, declared in the class or any superclass. Superclasses are resolved the way javac
does (explicit import, then same package, then wildcard imports) across the whole frameworks tree, so
package-private fields and superclasses outside the properties packages (GetOptions, SearchOptions,
...) count. This is the same ground truth scripts/audit_properties_class_bodies.py checks against (PY-45).

Regenerating from another Egeria ref: re-run test_py59 with EGERIA_6_4_SRC/EGERIA_6_4_REF set; CI skips the
equality test.

Reads a git ref (default origin/main) with `git cat-file`, so the Egeria checkout is never modified:

    python scripts/gen_properties_class_fields.py [--egeria ~/localGit/egeria-v6/egeria] [--ref origin/main]
"""
import argparse
import os
import re
import subprocess
import sys

OUT = os.path.join(os.path.dirname(__file__), "..", "md_processing", "md_processing_utils",
                   "properties_class_fields.py")
FRAMEWORKS = "open-metadata-implementation/frameworks/"
ROOTS = {"RelationshipProperties": "relationship", "ClassificationProperties": "classification",
         "EntityProperties": "entity"}

_PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)
_IMPORT = re.compile(r"^\s*import\s+(?!static\b)([\w.]+?)(\.\*)?\s*;", re.M)
_CLASS = re.compile(r"\bpublic\s+(?:(?:abstract|final)\s+)*class\s+(\w+)(?:\s*<[^{]*?>)?"
                    r"(?:\s+extends\s+([\w.]+))?")
_SETTER = re.compile(r"\bpublic\s+(?:(?:final|synchronized)\s+)*void\s+set(\w+)\s*\(")
_JSON_PROPERTY = re.compile(r"@JsonProperty\s*\(\s*(?:value\s*=\s*)?\"([^\"]*)\"")
_JSON_IGNORE = re.compile(r"@JsonIgnore\b(?!Properties)")


def git(egeria: str, *args, stdin: bytes | None = None) -> bytes:
    return subprocess.run(["git", "-C", egeria, *args], input=stdin, capture_output=True, check=True).stdout


def listed(path: str) -> bool:
    """Files whose *Properties classes go in the table (the rest are read only for superclass chains)."""
    return path.endswith("Properties.java") or "/properties/" in path


def read_sources(egeria: str, ref: str) -> dict[str, str]:
    """Every main-source Java file under the frameworks tree at `ref`, by path."""
    paths = [p for p in git(egeria, "ls-tree", "-r", "--name-only", ref, "--", FRAMEWORKS).decode().split("\n")
             if p.endswith(".java") and "/src/main/java/" in p]
    batch = git(egeria, "cat-file", "--batch", stdin="".join(f"{ref}:{p}\n" for p in paths).encode())
    sources, pos = {}, 0
    for path in paths:
        header_end = batch.index(b"\n", pos)
        size = int(batch[pos:header_end].split()[2])
        start = header_end + 1
        sources[path] = batch[start:start + size].decode("utf-8", errors="ignore")
        pos = start + size + 1
    return sources


ARCHIVES = "open-metadata-resources/open-metadata-archives/open-metadata-types/src/main/java/"
_ENUM_CONSTANT = re.compile(r"\b([A-Z][A-Z0-9_]*)\(\s*\"[0-9a-fA-F-]{20,}\"\s*,\s*\"([^\"]+)\"")
_CLASSIFICATION_DEF = re.compile(
    r"archiveHelper\.getClassificationDef\(\s*OpenMetadataType\.(\w+)\s*,\s*"
    r"(null|this\.archiveBuilder\.getClassificationDef\(\s*OpenMetadataType\.(\w+)\.typeName\s*\))")


_ENTITY_DEF = re.compile(
    r"archiveHelper\.getDefaultEntityDef\(\s*OpenMetadataType\.(\w+)\s*,\s*"
    r"(null|this\.archiveBuilder\.getEntityDef\(\s*OpenMetadataType\.(\w+)\.typeName\s*\))")
_STRING_LITERAL = re.compile(r"\bString\s+(\w+)\s*=\s*\"([^\"]*)\"\s*;")
_RELATIONSHIP_END = re.compile(
    r"archiveHelper\.getRelationshipEndDef\(\s*this\.archiveBuilder\.getEntityDef\(\s*"
    r"OpenMetadataType\.(\w+)\.typeName\s*\)\s*,\s*(\w+)\s*,")


def read_typedef_sources(egeria: str, ref: str) -> dict[str, str]:
    """The OpenMetadataTypesArchive*.java files at `ref`, by path (the typedefs the platform loads)."""
    paths = [p for p in git(egeria, "ls-tree", "-r", "--name-only", ref, "--", ARCHIVES).decode().split("\n")
             if re.search(r"/OpenMetadataTypesArchive[\w]*\.java$", p)]
    batch = git(egeria, "cat-file", "--batch", stdin="".join(f"{ref}:{p}\n" for p in paths).encode())
    sources, pos = {}, 0
    for path in paths:
        header_end = batch.index(b"\n", pos)
        size = int(batch[pos:header_end].split()[2])
        start = header_end + 1
        sources[path] = batch[start:start + size].decode("utf-8", errors="ignore")
        pos = start + size + 1
    return sources


def type_name_constants(sources: dict[str, str]) -> dict[str, str]:
    """{OpenMetadataType constant: its typeName}, from OpenMetadataType.java (NAME("guid", "typeName", ...))."""
    out: dict[str, str] = {}
    for path, src in sources.items():
        if path.endswith("/OpenMetadataType.java") or path == "OpenMetadataType.java" or "OpenMetadataType.java" in path:
            out.update({m.group(1): m.group(2) for m in _ENUM_CONSTANT.finditer(src)})
    return out


def classification_typedef_supers(archives: dict[str, str], names: dict[str, str]) -> dict[str, str]:
    """{classification: its supertype} from the typedefs: the 2nd argument of
    archiveHelper.getClassificationDef(<type>, <supertype or null>, <entity>, <bool>) in every archive."""
    out: dict[str, str] = {}
    for src in archives.values():
        for m in _CLASSIFICATION_DEF.finditer(_strip_comments(src)):
            sub = names.get(m.group(1))
            sup = names.get(m.group(3)) if m.group(3) else None
            if sub and sup:
                out[sub] = sup
    return out


def entity_typedef_supers(archives: dict[str, str], names: dict[str, str]) -> dict[str, str]:
    """{entity type: its supertype} from the typedefs: archiveHelper.getDefaultEntityDef(<type>, <supertype or null>)."""
    out: dict[str, str] = {}
    for src in archives.values():
        for m in _ENTITY_DEF.finditer(_strip_comments(src)):
            sub = names.get(m.group(1))
            sup = names.get(m.group(3)) if m.group(3) else None
            if sub and sup:
                out[sub] = sup
    return out


def relationship_end_types(archives: dict[str, str], names: dict[str, str]) -> dict[str, tuple[str, ...]]:
    """{relationship end attribute name: the entity types at that end}, from the typedefs' getRelationshipEndDef
    (<entity type>, <end attribute name variable>, ...) calls. The attribute name is what an element's relationship
    list is called (serverEndpoints), so the type is what a list's related elements are."""
    out: dict[str, set[str]] = {}
    for src in archives.values():
        text = _strip_comments(src)
        literals: list[tuple[int, str, str]] = [(m.start(), m.group(1), m.group(2)) for m in _STRING_LITERAL.finditer(text)]
        for m in _RELATIONSHIP_END.finditer(text):
            entity = names.get(m.group(1))
            attr = next((lit for pos, var, lit in reversed(literals) if pos < m.start() and var == m.group(2)), None)
            if entity and attr:
                out.setdefault(attr, set()).add(entity)
    return {k: tuple(sorted(v)) for k, v in sorted(out.items())}


def supertype_chains(direct: dict[str, str]) -> dict[str, tuple[str, ...]]:
    """{classification: (supertype, its supertype, ...)}, nearest first, for the ones that have a supertype."""
    out = {}
    for sub in direct:
        chain, node, seen = [], direct.get(sub), {sub}
        while node and node not in seen:
            chain.append(node)
            seen.add(node)
            node = direct.get(node)
        out[sub] = tuple(chain)
    return out


def _strip_comments(src: str) -> str:
    """The source with comments blanked (newlines kept); string and char literals are left in place."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1])
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _depths(src: str) -> list[int]:
    """Brace depth at every character of comment-free `src`, ignoring braces inside literals."""
    depth, out, quote, i = 0, [0] * len(src), None, 0
    while i < len(src):
        c = src[i]
        if quote:
            if c == "\\":
                out[i] = depth
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if i < len(src):
            out[i] = depth
        i += 1
    return out


def _one_argument(src: str, open_paren: int) -> bool:
    """True if the parameter list starting at `open_paren` holds exactly one parameter."""
    depth, angle, saw = 0, 0, False
    for c in src[open_paren:]:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return saw
        elif c == "<":
            angle += 1
        elif c == ">":
            angle -= 1
        elif c == "," and depth == 1 and angle == 0:
            return False
        elif not c.isspace():
            saw = True
    return False


def _jackson_name(base: str) -> str:
    """Jackson's default (legacy) setter naming: lower-case the leading run of capitals, so setURL is
    "url" and setGUID "guid", not java.beans' "URL". Egeria doesn't enable USE_STD_BEAN_NAMING; where it
    wants a camel-case acronym key it says so with @JsonProperty (e.g. iscQualifiedName)."""
    i = 0
    while i < len(base) and base[i].isupper():
        i += 1
    return base[:i].lower() + base[i:]


def parse(src: str) -> dict | None:
    """The top-level public class of one Java file: package, imports, name, extends, and its JSON keys in
    declaration order. Setters of nested classes don't count (depth 1 only); None for interfaces etc."""
    src = _strip_comments(src)
    depth = _depths(src)
    m = next((m for m in _CLASS.finditer(src) if depth[m.start()] == 0), None)
    if not m:
        return None
    package = (_PACKAGE.search(src) or [None, ""])[1]
    explicit, wildcards = {}, []
    for imp in _IMPORT.finditer(src):
        if imp.group(2):
            wildcards.append(imp.group(1))
        else:
            explicit[imp.group(1).rsplit(".", 1)[-1]] = imp.group(1)
    keys, prev_end = [], m.end()
    for s in _SETTER.finditer(src, m.end()):
        if depth[s.start()] != 1:
            continue
        # the annotations on this method: everything since the previous member ended
        start = max(src.rfind(";", prev_end, s.start()), src.rfind("}", prev_end, s.start()), prev_end)
        annotations = src[start:s.start()]
        prev_end = s.end()
        if _JSON_IGNORE.search(annotations) or not _one_argument(src, s.end() - 1):
            continue
        renamed = _JSON_PROPERTY.search(annotations)
        keys.append(renamed.group(1) if renamed else _jackson_name(s.group(1)))
    return {"package": package, "explicit": explicit, "wildcards": wildcards, "name": m.group(1),
            "extends": m.group(2), "keys": list(dict.fromkeys(keys))}


#: Filled by build_table: the Java Properties-class chain above each classification. A cross-check only: the table
#: is built from the typedefs (supertype_chains), which also give supertypes the Java classes do not extend (PY-59 F2).
java_supertypes: dict[str, tuple[str, ...]] = {}


def build_table(sources: dict[str, str], warn=lambda msg: None) -> dict[str, tuple[str, tuple[str, ...]]]:
    """{simple class name: (kind, keys)} for every listed *Properties class in `sources` ({path: java})."""
    classes, paths, by_simple = {}, {}, {}
    for path, src in sources.items():
        info = parse(src)
        if info is None:
            continue
        fqn = f"{info['package']}.{info['name']}" if info["package"] else info["name"]
        if fqn in classes:
            continue
        classes[fqn], paths[fqn] = info, path
        by_simple.setdefault(info["name"], []).append(fqn)

    unresolved: dict[str, set[str]] = {}

    def parent_of(fqn: str) -> str | None:
        info = classes[fqn]
        name = info["extends"]
        if not name:
            return None
        if "." in name and name in classes:
            return name
        candidates = [info["explicit"].get(name), f"{info['package']}.{name}",
                      *(f"{w}.{name}" for w in info["wildcards"])]
        for c in candidates:
            if c and c in classes:
                return c
        if len(by_simple.get(name, [])) == 1:  # e.g. a fully qualified extends to a nested name
            return by_simple[name][0]
        unresolved.setdefault(name, set()).add(fqn)
        return None

    def describe(fqn: str) -> tuple[str, tuple[str, ...]]:
        chain, node, seen = [], fqn, set()
        while node and node not in seen:
            seen.add(node)
            chain.append(node)
            node = parent_of(node)
        kind = next((ROOTS[classes[n]["name"]] for n in reversed(chain) if classes[n]["name"] in ROOTS), "other")
        # root first, as Jackson's bean description lists them; a subclass override keeps the root's slot
        keys = [k for n in reversed(chain) for k in classes[n]["keys"]]
        return kind, tuple(dict.fromkeys(keys))

    def supers(fqn: str) -> tuple[str, ...]:
        """The *Properties classes above `fqn`, nearest first, not counting the polymorphic root itself."""
        out, node, seen = [], parent_of(fqn), {fqn}
        while node and node not in seen and classes[node]["name"] not in ROOTS:
            seen.add(node)
            out.append(classes[node]["name"])
            node = parent_of(node)
        return tuple(out)

    table = {}
    java_supertypes.clear()
    for fqn in sorted(classes, key=lambda f: classes[f]["name"]):
        name = classes[fqn]["name"]
        if not name.endswith("Properties") or not listed(paths[fqn]):
            continue
        if name in table:
            raise SystemExit(f"two listed classes are both called {name}: the table is keyed by simple name")
        table[name] = describe(fqn)
        if table[name][0] == "classification":
            # ClassificationBean is the Java base of the classification beans, not an Egeria classification
            above = tuple(n[:-len("Properties")] for n in supers(fqn)
                          if n.endswith("Properties") and n != "ClassificationBeanProperties")
            if above:
                java_supertypes[name[:-len("Properties")]] = above
    for name, subclasses in sorted(unresolved.items()):
        warn(f"superclass {name} not in the frameworks tree (its setters are not counted): "
             f"{', '.join(sorted(s.rsplit('.', 1)[-1] for s in subclasses))}")
    return table


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--egeria", default=os.path.expanduser("~/localGit/egeria-v6/egeria"))
    ap.add_argument("--ref", default="origin/main")
    args = ap.parse_args()
    warn = lambda m: print(f"warning: {m}", file=sys.stderr)  # noqa: E731
    sources = read_sources(args.egeria, args.ref)
    table = build_table(sources, warn=warn)
    # the supertypes come from the typedefs the platform loads; the Java class chain is only a cross-check
    chains = supertype_chains(classification_typedef_supers(read_typedef_sources(args.egeria, args.ref),
                                                            type_name_constants(sources)))
    archives = read_typedef_sources(args.egeria, args.ref)
    constants = type_name_constants(sources)
    entity_chains = supertype_chains(entity_typedef_supers(archives, constants))
    end_types = relationship_end_types(archives, constants)
    for cls, above in sorted(java_supertypes.items()):
        if chains.get(cls) != above:
            warn(f"classification {cls}: typedef supertypes {chains.get(cls, ())} differ from the Java chain {above}")
    sha, date = git(args.egeria, "log", "-1", "--format=%H %cs", args.ref).decode().strip().split()
    head = f"{sha[:10]} {date}"
    lines = [
        "# SPDX-License-Identifier: Apache-2.0",
        "# Copyright Contributors to the ODPi Egeria project.",
        '"""',
        "Open-metadata Properties classes: kind and the JSON property names each reads (inherited included).",
        "",
        f"GENERATED by scripts/gen_properties_class_fields.py from Egeria {args.ref} at {head} -- do not",
        "edit by hand; re-run the script instead. Kind is the root of the class's superclass chain:",
        "relationship (RelationshipProperties), classification (ClassificationProperties), entity",
        "(EntityProperties) or other. Keys are the public setters (what Jackson binds) through the whole",
        "superclass chain, root first.",
        '"""',
        "",
        "PROPERTIES_CLASS_FIELDS: dict[str, tuple[str, tuple[str, ...]]] = {",
    ]
    for cls, (kind, fields) in table.items():
        lines.append(f"    {cls!r}: ({kind!r}, {fields!r}),")
    lines.append("}")
    lines += [
        "",
        "#: Each classification's supertypes, nearest first, from the typedefs (getClassificationDef's 2nd argument",
        "#: in OpenMetadataTypesArchive*.java), for the classifications that have any. `class:A` in a report column",
        "#: matches a classification named A or any classification with A in this list (PY-59).",
        "CLASSIFICATION_SUPERTYPES: dict[str, tuple[str, ...]] = {",
    ]
    for cls, above in sorted(chains.items()):
        lines.append(f"    {cls!r}: {above!r},")
    lines.append("}")
    lines += [
        "",
        "#: Each entity type's supertypes, nearest first, from the typedefs (getDefaultEntityDef's 2nd argument).",
        "ENTITY_SUPERTYPES: dict[str, tuple[str, ...]] = {",
    ]
    for cls, above in sorted(entity_chains.items()):
        lines.append(f"    {cls!r}: {above!r},")
    lines.append("}")
    lines += [
        "",
        "#: The entity type(s) at each relationship end, by the end's attribute name, which is also what an element's",
        "#: relationship list is called (serverEndpoints -> Endpoint), from the typedefs (getRelationshipEndDef). PY-61.",
        "END_ENTITY_TYPES: dict[str, tuple[str, ...]] = {",
    ]
    for attr, types in end_types.items():
        lines.append(f"    {attr!r}: {types!r},")
    lines.append("}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    kinds = {}
    for kind, _ in table.values():
        kinds[kind] = kinds.get(kind, 0) + 1
    print(f"wrote {len(table)} classes {kinds} from {args.ref} {head} to {OUT}")


if __name__ == "__main__":
    main()
