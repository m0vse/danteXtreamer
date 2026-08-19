# Tools

Reserved for repository-owned setup, capture, and analysis utilities.

Tools must default to read-only behavior on unknown hardware. Any command that
writes module registers or initiates firmware update must require an explicit
operation and a confirmed protocol/firmware compatibility check.

`verify-local-inputs.ps1` performs a read-only SHA-256 check of the ignored A203
manual/example archives and both Yamaha service manuals against
`docs/provenance.md`. It also checks that representative extracted firmware and
software skeleton files are present.
