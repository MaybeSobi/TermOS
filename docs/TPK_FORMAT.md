# TPK package format — version 1

A `.tpk` file is an **uncompressed POSIX TAR archive**. It is not extracted with
`tar -x`; TPM reads individual regular-file members and validates their paths,
lengths, and SHA-256 digests before installation.

## Archive layout

```text
example-1.0.0-x86_64.tpk
├── manifest.json
└── payload/
    └── usr/
        └── bin/
            └── example
```

The archive contains one `manifest.json` member and one `payload/<relative-path>`
member for each file in the manifest. Version 1 supports regular files only; it
does not support symbolic links, hard links, device nodes, FIFOs, or compressed
TAR streams.

## Manifest fields

The version-1 manifest contains:

- `format`: the literal string `TPK`.
- `format_version`: integer `1`.
- `name`: package identifier.
- `version`: package version. The current upgrade comparator accepts numeric,
  dot-separated versions (for example `1.2.3`).
- `architecture`: target architecture, such as `x86_64`, or `all` where
  supported by the installer.
- `description`: human-readable package description.
- `files`: array of file records. Each record contains `path`, `sha256`, `size`,
  and `mode`.
- Dependency metadata: produced by the current `tpm build --depends SPEC`
  interface and interpreted by TPM's dependency resolver. Use `tpm info FILE`
  to inspect the exact manifest emitted by the installed TPM version; dependency
  grammar and comparison operators are defined by that version's resolver.

`path` is relative to the package root and must not be absolute, contain `..`,
backslashes, NUL bytes, or empty path components. `sha256` is a lowercase
64-character SHA-256 hex digest. `size` is a non-negative integer. `mode` is a
permission mode restricted to `0o777`.

## Building and inspecting

```sh
tpm build ./staging-root \
  --name example --version 1.0.0 --arch x86_64 \
  --description "Example package" \
  --depends 'libfoo>=1.2.0' \
  --output packages/example-1.0.0-x86_64.tpk

tpm info packages/example-1.0.0-x86_64.tpk
```

The package builder records each file's size, mode, and SHA-256. The validator
checks archive membership, duplicate entries, path safety, manifest structure,
and every payload digest before TPM uses the package.

## Repository integrity and authenticity

A repository index records package metadata and the archive's byte size and
SHA-256. The index is signed separately using Ed25519; the detached signature
file is `repository.json.sig`. Clients must verify the signature with a public
key provisioned through a trusted channel and then verify archive hashes.

SHA-256 alone detects accidental or malicious changes only when the expected
hash is trusted. The Ed25519 signature authenticates the index only when the
public key itself is trusted. Never distribute the repository private key in an
ISO, a package archive, or a public source release.

## Compatibility policy

The version-1 format is intentionally small and uncompressed to avoid requiring
Python compression extensions in the minimal TermOS image. Any incompatible
change to archive layout or manifest semantics requires a new `format_version`.
