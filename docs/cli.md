# Command line

Installing the package exposes an `ioc-classify` command that wraps
[`IOCClassifier`][ioc_typing.IOCClassifier] for shell-pipeline use.

```bash
ioc-classify iocs.txt                # TSV (default)
ioc-classify --format json iocs.txt  # JSON Lines
cat iocs.txt | ioc-classify          # read from stdin
ioc-classify - < iocs.txt            # explicit stdin alias
```

## Input format

One IOC per line. Blank lines and lines starting with `#` are skipped,
so input files can be commented:

```
# Known-bad indicators, week 17
192.168.1.1
malicious.example.com
d41d8cd98f00b204e9800998ecf8427e
```

## Output formats

### TSV (default)

```
query	determined	type_pri	type_sec
192.168.1.1	True	ip	v4
malicious.example.com	True	domain	-
d41d8cd98f00b204e9800998ecf8427e	True	hash	md5
```

`-` is used for `None` type fields so the columns stay cut/awk-friendly.

### JSON Lines

```bash
ioc-classify --format json iocs.txt
```

```json
{"query": "192.168.1.1", "determined": true, "type_pri": "ip", "type_sec": "v4"}
{"query": "malicious.example.com", "determined": true, "type_pri": "domain", "type_sec": null}
```

## Pipeline patterns

Filter to hashes only:

```bash
ioc-classify iocs.txt | awk -F'\t' '$3 == "hash"'
```

Count by type:

```bash
ioc-classify iocs.txt | tail -n +2 | cut -f3 | sort | uniq -c
```

`ioc-classify` exits cleanly when its stdout is closed by a downstream
consumer such as `head`, so SOC-style pipelines don't surface a
`BrokenPipeError` traceback.

## Exit codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | All input lines processed        |
| 1    | Input file not found             |
