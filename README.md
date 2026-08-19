# danteXtreamer

`danteXtreamer` is an early-stage hardware integration project for building an
XDante/AES67 audio endpoint around the Audiocom A203 module.

The A203 is the network-audio endpoint. Audio crosses the module boundary as
I2S/TDM; XDante/AES67 transport occurs on the A203/network side. A Windows PC
audio transport and ASIO are not part of the core architecture.

## Status

This repository currently contains the reviewed design baseline, an isolated
source layout, and a hardware-first validation plan. It deliberately contains
no A203 control implementation yet: the supplied hardware manual does not
define the configuration/register protocol, and the supplied examples are for
related integrations whose applicability and redistribution terms are not
confirmed.

The proposed first milestone is a measured, bidirectional 48 kHz/24-bit audio
route between a reference XDante/AES67 endpoint and a vendor-confirmed A203
serial-audio mode. It starts with conservative electrical/control-plane
bring-up and records clock lock, channel mapping, interoperability, and
stability before scaling channel count.

The hardware baseline includes provision for a USB 2.0 High-Speed compatibility
bridge. Its eventual firmware would present the legacy AudioXtreamer host-facing
protocol while converting between packed 24-bit USB audio and the A203's 32-bit
serial-audio slots. Bridge firmware is not on the first-milestone critical path
because the legacy USB framing is tied to FX2/FPGA behavior that is not fully
documented and is not yet glitch-free. The first carrier may leave the bridge
processing section unpopulated or held in reset, but it should not require a
carrier redesign to add it.

## Repository map

- `docs/architecture.md` - system boundaries, data/control planes, and staged
  architecture.
- `docs/a203-integration-notes.md` - facts from the A203 manual, observations
  from examples, and project decisions kept explicitly separate.
- `docs/open-questions.md` - questions that must be answered before schematic
  freeze or control-protocol implementation.
- `docs/dependencies.md` - current and anticipated hardware/software setup.
- `docs/provenance.md` - review and licensing record for all supplied and
  related source material.
- `docs/usb-bridge.md` - AudioXtreamer-compatible USB bridge boundary and
  firmware-enablement gates.
- `hardware/` - future carrier, clocking, and signal-integrity design sources.
- `hardware/usb-bridge-requirements.md` - board-level requirements for including
  USB compatibility before its firmware is implemented.
- `src/control/` - future A203 control-plane code after protocol confirmation.
- `src/platform/` - board/MCU-specific glue kept outside protocol code.
- `src/usb-bridge/` - deferred legacy USB compatibility firmware.
- `tests/hardware/` - hardware-in-the-loop plans, fixtures, and non-proprietary
  test definitions.
- `tools/` - repository-owned diagnostic and capture utilities.

## Local vendor material

The existing `a203/` directory contains the supplied manual and example
archives. It is intentionally ignored by Git. Do not force-add those files or
their extracted contents until the copyright owner supplies redistribution
terms that cover the intended use. Inspection extracts belong under ignored
`tmp/` only.

## Development approach

1. Resolve the blocking electrical, PHY, clock, and control-protocol questions.
2. Bring up power/reset and perform read-only identification/status checks.
3. Validate one vendor-confirmed serial-audio mode at 48 kHz before expanding
   channel count or adding optional transports.
4. Include the USB High-Speed port and bridge provisions in the carrier design,
   but add firmware only behind the same serial-audio/control abstractions; do
   not couple core A203 integration to legacy FX2/Spartan-6 code.

See `docs/dependencies.md` before adding a build system. No compiler or SDK is
currently required because no implementation target has been selected.

To confirm that the ignored local inputs match the reviewed versions:

```powershell
.\tools\verify-local-inputs.ps1
```

## Licensing

No project-wide outbound licence has been selected. The new repository
documents are not a grant to redistribute the supplied A203 files. No source
code was copied from AudioXtreamer or the vendor archives during this
preparation pass. See `docs/provenance.md` before importing any external code.
