# A203 integration evidence

This file separates facts from the supplied A203 manual, observations from the
supplied examples, and decisions made for `danteXtreamer`. An observation from
one category must not silently become a claim in another.

## Vendor-documented A203 facts

Source: `hm-a203-en.pdf`, **A203 Hardware Manual Rev 1.2**, Shenzhen Audiocom
Technology Co., Ltd, released 2026-07-30. The local PDF is intentionally
untracked; its hash is recorded in `provenance.md`.

- The module is described as a Mini-PCI-form-factor XDante/AES67 network-audio
  interface with 32 input and 32 output channels and a full mixer.
- The headline specification lists 48/96 kHz, 24-bit PCM, and I2S/TDM4/8/16.
- Each serial-audio slot is 32 bits. A 24-bit or 16-bit sample is left-aligned;
  unused low bits are forced to zero.
- Inputs are sampled on rising SCLK. Output data changes on falling SCLK.
- The first channel follows a configurable LRCLK edge.
- The module contains a VCXO, always outputs MCLK, and can lock generated audio
  clocks to an external clock according to the manual.
- MCLK is listed as 12.288 or 24.576 MHz.
- The board drawing shows approximately 59.60 mm by 44.60 mm and 3.7 mm mounting
  holes. Mechanical CAD and tolerances are not supplied.

Key power/control pins from the manual:

| Function | Pins | Notes |
| --- | --- | --- |
| 3.3 V input | 1, 2, 114, 116, 118, 120, 122 | Current, tolerance, and sequencing are not specified. |
| Ground | 27, 30, 33, 36, 37, 41, 44, 51, 57, 58, 61, 62, 63, 66, 71, 72, 77, 78, 81, 83, 84, 93, 94, 102, 103, 112, 113 | Preserve the connector return network in the carrier layout. |
| 2.5 V output | 3 | Allowable load is not specified. |
| 1.25 V reference output | 7 | Allowable load is not specified. |
| 1.1 V outputs | 123, 124 | Allowable load is not specified. |
| `nRESET_IN` | 92 | Timing and electrical treatment are not specified. |
| `MUTE` | 65 | Described as indicating unsynchronised audio clocks; polarity/direction/timing are not fully specified. |

Key audio/clock pins from the manual's pin table:

| Function | Pin(s) |
| --- | --- |
| `SCLK` | 70 |
| `MCLK` | 76 |
| `LRCLK_IN` | 80 |
| `LRCLK` | 82 |
| `SDOUT[0:7]` | 85, 87, 89, 91, 95, 97, 99, 101 |
| `SDIN[0:7]` | 105, 107, 109, 111, 115, 117, 119, 121 |
| `EXTERNL_CLK` | 68 |

The prose later names `SCLK_IN`, while the pin table names only
`EXTERNL_CLK`. Their relationship is not documented and must be confirmed.

The manual's timing table mentions 44.1 kHz-family clock modes and rates above
96 kHz, while its headline product specification lists 48/96 kHz. These timing
rows are not treated as supported product modes without vendor confirmation.

## Observations from supplied examples

These are review notes, not an A203 API specification.

### `BF01_InterConn.rar`

The archive contains two STM32F103/Keil projects: a BF01 application and a
bootloader. The application uses USART1 at 115200 baud for a related module and
USART2 at 115200 for debug. It performs discovery, register reads/writes,
route/mixer setup, and firmware-update handling.

Observed messages include ASCII prefixes resembling `reg_br_` and `reg_bw_`,
followed by binary address/length/data fields. The example also uses undocumented
register addresses and constructs unicast/multicast route records. None of
those fields are implemented here because:

- the archive is named for BF01, not A203;
- no accompanying protocol/register specification is supplied;
- several values are unexplained or marked uncertain in the source itself;
- no archive-level redistribution grant was found.

The archive bundles ST HAL/CMSIS, uC/OS-II-related code, Keil state, compiled
`.bin`/`.hex` outputs, and vendor application code. Mixed provenance makes the
archive unsuitable for wholesale import.

### `SerialPortDemo.rar`

Despite its archive name, the reviewed MFC application communicates over UDP,
not a Windows serial port. It listens for discovery on UDP 9887, uses a
configurable data port, and sends 12-byte register read/write/reset messages to
UDP 4440. The message header starts `27 1E`; command values observed are reset
`02 00`, read `02 01`, and write `02 02`.

The archive includes Visual Studio user state and a compiled `HostCPU.exe`.
There is no clear archive-level licence or statement that this protocol applies
to A203. The code and executable are therefore not copied.

## Project decisions

- The product is an MLN2 replacement for Yamaha 01X and i88X devices. This is a
  project requirement, not a capability stated in the A203 manual.
- Core media flows between the Yamaha MLN2-side audio interface and A203
  XDante/AES67; no ASIO or Windows media transport is assumed.
- Control-protocol code waits for an A203-specific specification or written
  vendor confirmation that a reviewed example applies.
- Initial bring-up uses 48 kHz/24-bit and a vendor-confirmed lane mode.
- The pre-schematic Yamaha-to-A203 audio/control adapter uses
  `XC6SLX16-2FTG256C`. Its ordering code and provisional banks are selected;
  schematic release still depends on each target's lane map, clock role, host
  startup behavior, buffering, electrical levels, and power requirements. See
  `../hardware/fpga-selection.md` and `../hardware/interfaces/`.
- USB compatibility hardware is included in the carrier plan, while its
  firmware is deferred and isolated from core bring-up.
- Vendor manuals, archives, binaries, and extracted examples remain untracked.
