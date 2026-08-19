# Hardware sources

This directory is reserved for the repository-owned MLN2 replacement carrier:
schematics, PCB sources, Yamaha 01X/i88X variant records, pin constraints, and
design calculations.

Do not place vendor PDFs, reference archives, exported binaries, or confidential
reference designs here. Keep them under ignored `vendor/` and cite their title,
revision, and hash in `docs/provenance.md`.

The reviewed pre-schematic architecture and selected FPGA are in
`hardware-baseline.md` and `fpga-selection.md`. Complete connector dispositions
and the provisional FTG256 ball assignment are under `interfaces/`. They are
evidence-backed design hypotheses, not a frozen schematic or a claim that
unresolved A203 behavior is known.

No carrier schematic should be frozen from the A203 pin table or an assumed
common MLN2 pinout alone. Resolve the blocking Yamaha mechanics/power/startup
questions and the A203 power, reset, PHY, clock-input, lane-map, and unused-pin
questions first.

The carrier is expected to include USB High-Speed bridge provisions even if
firmware is deferred. See `usb-bridge-requirements.md`.
