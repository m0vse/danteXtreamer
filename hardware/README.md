# Hardware sources

This directory is reserved for repository-owned carrier schematics, PCB sources,
pin constraints, and design calculations.

Do not place vendor PDFs, reference archives, exported binaries, or confidential
reference designs here. Keep them under ignored `a203/` or `vendor/` and cite
their title/revision/hash in `docs/provenance.md`.

No carrier design should be started from the pin table alone. Resolve the
blocking power, reset, PHY, clock-input, and unused-pin questions first.

The carrier is expected to include USB High-Speed bridge provisions even if
firmware is deferred. See `usb-bridge-requirements.md`.
