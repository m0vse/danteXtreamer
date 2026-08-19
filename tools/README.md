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

`extract-kel-eagle-library.ps1` extracts the existing KEL
`8831E-100-170L` two-gate device and footprint from the AudioXtreamer Eagle
schematic into a standalone `.lbr` file. EasyEDA Pro can import that file into
its project or personal device library. The script verifies the expected device
and package names before writing the library.
