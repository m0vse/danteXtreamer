# Dependencies and setup

## Current repository

There is no build dependency yet. The repository is intentionally
documentation-first until the carrier, controller, control protocol, and local
audio implementation are selected.

Required now:

- Git for source control.
- A PDF viewer for the locally supplied A203 manual.
- An archive tool that can inspect RAR files without adding extracted vendor
  material to source control.

The `a203/`, `vendor/`, and `tmp/` trees are ignored. Keep supplied or extracted
vendor material there.

Verify the reviewed local A203 inputs and Yamaha 01X service manual:

```powershell
.\tools\verify-local-inputs.ps1
```

## Hardware bring-up equipment

- Yamaha 01X and Yamaha i88X target units, plus known-good original MLN2 cards
  for passive comparison.
- Local Yamaha 01X service manual under ignored `vendor/yamaha/01x/`, authorised
  i88X service information still to be obtained, mechanical measurements, and
  a protected breakout/interposer for each Yamaha card interface.
- A203 module with a confirmed firmware version.
- Vendor-approved carrier/reference design or a reviewed custom carrier.
- Current-limited 3.3 V bench supply and current measurement.
- Oscilloscope and logic analyser capable of the documented SCLK rates.
- A known-good XDante/AES67 endpoint and managed network/PTP visibility.
- A deterministic multichannel audio pattern generator/analyser.
- Vendor-recommended configuration/discovery utility once confirmed.
- USB 2.0 High-Speed signal-integrity/USB protocol test capability for bridge
  hardware validation, even if compatibility firmware is not yet available.

Do not connect a carrier based only on the short A203 manual or an assumed MLN2
pinout. Yamaha-host power, direction, startup behavior, and target differences,
plus A203 current, reset timing, PHY implementation, and several input mappings,
are missing.

## Anticipated implementation dependencies

The build system and toolchain will be selected after the controller is chosen.
Likely categories, not current commitments, are:

- controller/DSP/FPGA vendor toolchain;
- CMake and a modern C/C++ compiler for hardware-independent protocol/test code;
- packet capture and analysis tools for AES67 interoperability;
- hardware-in-the-loop scripts using only documented, redistributable APIs.

Any vendor SDK must be installed outside the tracked source tree or beneath an
ignored local `sdk/` directory unless its licence explicitly permits vendoring.

## AudioXtreamer relationship

The related AudioXtreamer checkout uses Visual Studio, MFC, WiX, a custom
WinUSB transport, and Steinberg ASIO SDK 2.3.4. None is required for the core
A203 XDante/AES67 path.

For the included USB bridge hardware and later compatibility firmware:

- the ASIO SDK must be obtained directly under Steinberg's terms and remain
  outside source control;
- the current AudioXtreamer host and USB design can be used as a behavioral
  reference, but its streaming implementation is not a proven stable transport;
- compatible USB descriptors/firmware and their licensing are prerequisites,
  not details to infer.

## Reproducible setup record

When implementation begins, record exact versions for:

- A203 hardware revision and firmware;
- target device (01X or i88X), serial number/revision, original MLN2 revision,
  connector/interposer revision, and target-specific lane/control profile;
- carrier schematic/PCB revision;
- controller toolchain and SDK;
- network switch, PTP configuration, and reference endpoint;
- build generator/compiler and test instruments;
- optional USB bridge firmware, driver, and ASIO SDK (if used).
