# Hardware sources

This directory is reserved for the repository-owned MLN2 replacement carrier:
schematics, PCB sources, Yamaha 01X/i88X variant records, pin constraints, and
design calculations.

Do not place vendor PDFs, reference archives, exported binaries, or confidential
reference designs here. Keep them under ignored `a203/` or `vendor/` and cite
their title/revision/hash in `docs/provenance.md`.

No carrier design should be started from the A203 pin table or an assumed common
MLN2 pinout alone. Resolve the blocking Yamaha mechanics/connector/power/startup
questions and the A203 power, reset, PHY, clock-input, and unused-pin questions
first.

The carrier is expected to include USB High-Speed bridge provisions even if
firmware is deferred. See `usb-bridge-requirements.md`.
