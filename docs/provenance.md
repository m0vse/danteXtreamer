# Provenance and licensing record

Reviewed on 2026-08-19. Paths refer to the local development machine; hashes
identify the reviewed inputs without committing them.

## Project requirement

The repository is intended as a replacement for the Yamaha MLN2 card in 01X and
i88X devices. This requirement was supplied by the project owner. It is not a
claim found in the A203 manual or vendor examples, and it requires independent
mechanical, electrical, audio/clock, and host-control validation for each Yamaha
target.

## Audiocom-supplied material

| Local item | SHA-256 | Review outcome |
| --- | --- | --- |
| `vendor/audiocom/a203/hm-a203-en.pdf` | `19C275980A53EBDB254BAB40AD25CAA34AB514D598365CA58C8A0BDDA8D8D8C3` | Read completely and visually checked across all 9 pages. Used as the primary A203 hardware source. No redistribution terms found; ignored by Git. |
| `vendor/audiocom/a203/BF01_InterConn.rar` | `6FBDD7C931506488961F8DC1B3D1D461321C79A0AD20CDD5C1BE53F807737B06` | 525 archive entries; two related STM32F103 projects including vendor code, ST HAL/CMSIS, uC/OS-II-related sources, Keil state, and generated binaries. Preserved and extracted locally under `vendor/audiocom/a203/examples/bf01-interconnect/`; not published. |
| `vendor/audiocom/a203/SerialPortDemo.rar` | `70E7F49B6A5C15A7FAA2561036ECCE08BCF84D614540B7AF36417C588BDA9B31` | 28 archive entries; MFC UDP discovery/register demo plus Visual Studio state and `HostCPU.exe`. Preserved and extracted locally under `vendor/audiocom/a203/examples/serial-port-demo/`; not published. |

The presence of identifiable third-party notices inside parts of an archive does
not license the archive as a whole. In particular, the BF01 archive mixes ST
BSD-3-Clause-labelled files with other middleware and vendor application code.
The SerialPortDemo archive includes COBS source without a clear origin/licence
notice. Both archives remain excluded until Audiocom confirms redistribution
rights and A203 applicability.

## Related AudioXtreamer repository

- Local origin: `C:/Users/phil.taylor/source/repos/audioxtreamer`
- Reviewed commit: `c655eeb3b48ce4dff825a3f3a899b25ab0e0fdad`
- Repository licence: MIT, copyright 2019 Hector Soto, TurtleDesign.

Two Yamaha service documents are available locally for engineering reference:

| Local ignored item | Origin | SHA-256 | Disposition |
| --- | --- | --- | --- |
| `vendor/yamaha/01x/Yamaha-01X-Service-Manual.pdf` | `audioxtreamer/docs/Yamaha-01X-Service-Manual.pdf` | `DD5769860153C6BACF693709EEC54E1BB4FACB24F76821A1CA0000F4A89166D0` | 153-page Yamaha 01X service manual; byte-for-byte local copy. Ignored and not published because the AudioXtreamer MIT licence does not establish redistribution rights for this Yamaha document. |
| `vendor/yamaha/i88x/yamaha_i88x.pdf` | Supplied locally by the project owner | `7D4F9FBCA94FA14F5DA5116900E5AC3F4A7E4CE7D44B542833891306F9AA1867` | 92-page Yamaha i88X service manual, metadata title `i88X_SM`, dated 2004. Ignored and not published because redistribution rights have not been established. |

Reviewed areas and disposition:

| Area | Potential value | Disposition |
| --- | --- | --- |
| `AudioXtreamer/AudioXtreamer/AppLog.*` | Persistent Windows logging pattern | Not copied. A core Windows process is not currently required. Reconsider for a future desktop control utility with MIT attribution. |
| `AudioXtreamer/TortugASIO/` and COM registration | Existing ASIO host-facing pattern | Not copied. Core A203 audio does not stream through Windows, and ASIO SDK headers are separately licensed. |
| `AudioXtreamer/FX2LP`, `WinUSB`, `UsbDev`, `ZTEXDev` | Behavioral reference for optional USB compatibility | Not copied. Hardware-specific, incomplete without FX2 firmware/descriptors, and associated with unresolved transport glitches. |
| `VHDL/`, `FPGA/`, `Pcb/` | Legacy USB/01X implementation and evidence about one Yamaha integration | Not copied. Useful as a reference when characterising the 01X, but it neither proves i88X compatibility nor requires reuse of Spartan-6, Xilinx ISE, or the legacy RTL. The new project's FPGA decision is recorded separately. |
| `AudioXtreamer/Installer/` | x86/x64 WiX registration conventions | Not copied. No Windows deliverable exists yet. |
| `.gitignore`, README, handover document | Build hygiene and documentation patterns | Consulted as references; new repository text was written specifically for A203 and no file was copied. |
| `libs/simpleini` | Settings library submodule | Not copied. No configuration-file requirement exists yet; retain its own upstream provenance if chosen later. |

No AudioXtreamer source component was copied or adapted in this preparation
pass. This is deliberate: the only immediately reusable material was either
Windows-specific, USB/FPGA-specific, or unnecessary before the A203 interface is
confirmed.

For the 2026-08-19 hardware-baseline pass, the following AudioXtreamer files
were read as engineering evidence without copying source:

- `docs/USB_AUDIO_STABILITY_HANDOVER.md` for the documented 01X channel counts,
  MLN2 connector rows, clock ownership, and unresolved USB limitations;
- `VHDL/usb2iis/top_audioxtreamer.vhd` and `pcmio.vhd` for the physical 12-line
  interface and 24-bit left-justified capture/serialisation pattern;
- `FPGA/ZTEX201/USB32chAudio/ZTEX201.ucf` for the actual 3.3 V I/O and clock
  constraints of the experimental Spartan-6 implementation;
- `Pcb/AudioXtreamer_Ymh01x.sch` for the replacement connector's audio, MIDI,
  clock, +5 V, and +3.3 V usage.

The resulting `hardware/hardware-baseline.md` and `hardware/fpga-selection.md`
are new project documents. They describe requirements and alternatives; they do
not incorporate third-party HDL, schematic artwork, footprints, or constraints.

## New repository content

The Markdown files, ignore rules, and directory layout in this repository were
created for `danteXtreamer`. No project-wide outbound licence has been selected.
Before accepting external code, add its origin, exact version/commit, licence,
local modifications, and required notices to this file.
