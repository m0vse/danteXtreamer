# danteXtreamer

`danteXtreamer` is an early-stage replacement for the Yamaha MLN2 card used in
the Yamaha 01X digital mixing studio and i88X audio interface. It uses an
Audiocom A203 module to replace the original mLAN/FireWire network-audio
function with XDante/AES67 while connecting to the host unit's internal audio,
clock, control, power, and mechanical interfaces.

The intended product boundary is:

```text
Yamaha 01X or i88X <-> MLN2-compatible replacement interface
                    <-> A203 I2S/TDM <-> XDante/AES67 network
```

The A203 is the network-audio endpoint. A compatibility layer must adapt each
Yamaha host's MLN2 connector, audio lanes, clocks, startup/control behavior, and
mechanics to the A203. A Windows PC audio transport and ASIO are not part of the
core network path.

“MLN2 replacement” is the design goal, not a current compatibility claim. The
01X and i88X interfaces must be measured and documented, and differences must
be handled explicitly before the board is described as electrically,
mechanically, or functionally compatible.

## Status

This repository currently contains the reviewed design baseline and an isolated
source layout for replacing MLN2 in both target products. The selected FPGA is a Spartan-6
`XC6SLX16-2FTG256C`, with a complete provisional bank assignment for Yamaha,
A203, and an optional full EZ-USB FX2LP interface. The initial generated
EasyEDA JSON was rejected because its inline symbols and label-heavy layout were
not an acceptable engineering schematic; it has been withdrawn. A native
EasyEDA Pro replacement will use library devices, including the existing KEL
connector device imported from AudioXtreamer. Schematic release remains
conditional on that redraft, a combined trial implementation, power/thermal
budgeting, physical measurements, footprint review, safe-state/clock circuitry,
and A203 vendor information.

The proposed first installed milestone is a measured, bidirectional 48 kHz/
24-bit route through a danteXtreamer prototype fitted in one target Yamaha unit,
using a vendor-confirmed A203 serial-audio mode. It starts by characterising the
original MLN2 interface without driving unknown signals, then records clock
lock, Yamaha channel mapping, XDante/AES67 interoperability, startup/mute
behavior, and stability. The same compatibility matrix must then pass on the
other target; 01X compatibility is not evidence of i88X compatibility.

The hardware baseline includes provision for a USB 2.0 High-Speed compatibility
bridge. Its eventual firmware would present the legacy AudioXtreamer host-facing
protocol while converting between packed 24-bit USB audio and the A203's 32-bit
serial-audio slots. Bridge firmware is not on the first-milestone critical path
because the legacy USB framing is tied to FX2/FPGA behavior that is not fully
documented and is not yet glitch-free. The first carrier may leave the bridge
processing section unpopulated or held in reset, but it should not require a
carrier redesign to add it.

The selected USB controller for the first board is the stocked 100-pin EZ-USB
FX2LP `CY7C68013A-100AXC` (JLCPCB `C9926`). Its manufacturer-discontinued status
is accepted for this low-volume compatibility design and managed through
buy-ahead procurement; it is not treated as a long-life general-purpose choice.

## Repository map

- `docs/architecture.md` - system boundaries, data/control planes, and staged
  architecture.
- `docs/a203-integration-notes.md` - facts from the A203 manual, observations
  from examples, and project decisions kept explicitly separate.
- `docs/mln2-replacement.md` - Yamaha 01X/i88X replacement boundary,
  compatibility criteria, and staged validation.
- `docs/open-questions.md` - questions that must be answered before schematic
  freeze or control-protocol implementation.
- `docs/dependencies.md` - current and anticipated hardware/software setup.
- `docs/provenance.md` - review and licensing record for all supplied and
  related source material.
- `docs/usb-bridge.md` - AudioXtreamer-compatible USB bridge boundary and
  firmware-enablement gates.
- `hardware/` - MLN2-form-factor replacement carrier, clocking, and
  signal-integrity design sources.
- `hardware/hardware-baseline.md` - proposed board blocks, Yamaha/A203 audio
  adaptation, clocks, power, Ethernet, USB, safe states, and schematic split.
- `hardware/fpga-selection.md` - I/O/resource requirements, current FPGA
  decision, capacity evidence, JLCPCB sourcing snapshot, and selection gates.
- `hardware/interfaces/` - complete Yamaha and A203 connector dispositions plus
  the provisional Spartan-6 FTG256 bank/ball assignment.
- `hardware/easyeda/` - native EasyEDA drafting requirements and the reusable
  KEL connector library-import source extracted from AudioXtreamer.
- `hardware/usb-bridge-requirements.md` - board-level requirements for including
  USB compatibility before its firmware is implemented.
- `src/control/` - future A203 control-plane code after protocol confirmation.
- `src/platform/` - board/MCU-specific glue kept outside protocol code.
- `src/usb-bridge/` - deferred legacy USB compatibility firmware.
- `tests/hardware/` - hardware-in-the-loop plans, fixtures, and non-proprietary
  test definitions.
- `tools/` - repository-owned diagnostic and capture utilities.

## Local vendor material

All local third-party material is consolidated under ignored `vendor/`:

- `vendor/audiocom/a203/` - A203 manual, original example archives, and
  reference-only extracted firmware/software skeletons;
- `vendor/yamaha/01x/Yamaha-01X-Service-Manual.pdf` - local 01X service manual;
- `vendor/yamaha/i88x/yamaha_i88x.pdf` - local i88X service manual;
- `vendor/ztex/usb-fpga-2.01.pdf` - local ZTEX FX2/Spartan-6 schematic reference.

Do not force-add these files or their extracted contents until the copyright
owners supply redistribution terms that cover the intended use. Temporary
inspection output belongs under ignored `tmp/`.

## Development approach

1. Characterise original MLN2 cards and both Yamaha host interfaces using
   passive/read-only methods; document every 01X/i88X difference.
2. Resolve the blocking Yamaha mechanical/electrical, A203 PHY, clock, power,
   reset, and control-protocol questions.
3. Bring up the replacement outside the Yamaha host with current limiting and
   perform read-only identification/status checks.
4. Validate an installed 48 kHz path on one target, then repeat the compatibility
   matrix on the other target before claiming support for both.
5. Include the USB High-Speed port and bridge provisions in the carrier design,
   but add firmware only behind the same serial-audio/control abstractions; do
   not couple core A203 integration to legacy FX2/Spartan-6 code.

See `docs/dependencies.md` before adding a build system. ISE 14.7 is the selected
FPGA toolchain, but no RTL trial project has been added yet.

To confirm that the ignored local inputs match the reviewed versions:

```powershell
.\tools\verify-local-inputs.ps1
```

To regenerate the KEL Eagle-library import file:

```powershell
.\tools\extract-kel-eagle-library.ps1
```

## Licensing

No project-wide outbound licence has been selected. The new repository
documents are not a grant to redistribute the supplied A203 files. No source
code was copied from AudioXtreamer or the vendor archives during this
preparation pass. See `docs/provenance.md` before importing any external code.
