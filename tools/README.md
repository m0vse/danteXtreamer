# Tools

Reserved for repository-owned setup, capture, and analysis utilities.

Tools must default to read-only behavior on unknown hardware. Any command that
writes module registers or initiates firmware update must require an explicit
operation and a confirmed protocol/firmware compatibility check.

`verify-local-inputs.ps1` performs a read-only SHA-256 check of the ignored A203
manual/example archives, Yamaha service manuals, and ZTEX schematic against
`docs/provenance.md`. It also checks that representative extracted firmware and
software skeleton files are present.

`verify-pin-matrices.ps1` checks connector completeness, FPGA bank capacity,
duplicate balls/signals, and cross-file ball references. It does not replace
AMD package-file verification or ISE placement.

`verify-easyeda-schematic.ps1` parses the generated EasyEDA multi-sheet JSON,
checks its document/page types, verifies required LCSC bindings and all 122
non-debug interface-net endpoints, and confirms the Yamaha/A203 contact counts
and mandatory design-hold warnings. It does not replace EasyEDA Pro import,
ERC, footprint review, or electrical design review.
