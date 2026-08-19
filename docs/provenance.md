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
| `a203/hm-a203-en.pdf` | `19C275980A53EBDB254BAB40AD25CAA34AB514D598365CA58C8A0BDDA8D8D8C3` | Read completely and visually checked across all 9 pages. Used as the primary hardware source. No redistribution terms found; ignored by Git. |
| `a203/BF01_InterConn.rar` | `6FBDD7C931506488961F8DC1B3D1D461321C79A0AD20CDD5C1BE53F807737B06` | 525 archive entries; two related STM32F103 projects including vendor code, ST HAL/CMSIS, uC/OS-II-related sources, Keil state, and generated binaries. Inspected only under ignored `tmp/`; not copied. |
| `a203/SerialPortDemo.rar` | `70E7F49B6A5C15A7FAA2561036ECCE08BCF84D614540B7AF36417C588BDA9B31` | 28 archive entries; MFC UDP discovery/register demo plus Visual Studio state and `HostCPU.exe`. No archive-level licence found; inspected only under ignored `tmp/`; not copied. |

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

One Yamaha service document was copied locally for engineering reference:

| Local ignored item | Origin | SHA-256 | Disposition |
| --- | --- | --- | --- |
| `vendor/yamaha/01x/Yamaha-01X-Service-Manual.pdf` | `audioxtreamer/docs/Yamaha-01X-Service-Manual.pdf` | `DD5769860153C6BACF693709EEC54E1BB4FACB24F76821A1CA0000F4A89166D0` | 153-page Yamaha 01X service manual; byte-for-byte local copy. Ignored and not published because the AudioXtreamer MIT licence does not establish redistribution rights for this Yamaha document. |

No i88X service manual or other i88X-specific file was found in the related
repository. Obtain an authorised reference before deriving that target's MLN2
interface.

Reviewed areas and disposition:

| Area | Potential value | Disposition |
| --- | --- | --- |
| `AudioXtreamer/AudioXtreamer/AppLog.*` | Persistent Windows logging pattern | Not copied. A core Windows process is not currently required. Reconsider for a future desktop control utility with MIT attribution. |
| `AudioXtreamer/TortugASIO/` and COM registration | Existing ASIO host-facing pattern | Not copied. Core A203 audio does not stream through Windows, and ASIO SDK headers are separately licensed. |
| `AudioXtreamer/FX2LP`, `WinUSB`, `UsbDev`, `ZTEXDev` | Behavioral reference for optional USB compatibility | Not copied. Hardware-specific, incomplete without FX2 firmware/descriptors, and associated with unresolved transport glitches. |
| `VHDL/`, `FPGA/`, `Pcb/` | Legacy USB/01X implementation and evidence about one Yamaha integration | Not copied. Useful as a reference when characterising the 01X, but it neither proves i88X compatibility nor establishes a requirement for FPGA or Xilinx ISE in the A203 design. |
| `AudioXtreamer/Installer/` | x86/x64 WiX registration conventions | Not copied. No Windows deliverable exists yet. |
| `.gitignore`, README, handover document | Build hygiene and documentation patterns | Consulted as references; new repository text was written specifically for A203 and no file was copied. |
| `libs/simpleini` | Settings library submodule | Not copied. No configuration-file requirement exists yet; retain its own upstream provenance if chosen later. |

No AudioXtreamer source component was copied or adapted in this preparation
pass. This is deliberate: the only immediately reusable material was either
Windows-specific, USB/FPGA-specific, or unnecessary before the A203 interface is
confirmed.

## New repository content

The Markdown files, ignore rules, and directory layout in this repository were
created for `danteXtreamer`. No project-wide outbound licence has been selected.
Before accepting external code, add its origin, exact version/commit, licence,
local modifications, and required notices to this file.
