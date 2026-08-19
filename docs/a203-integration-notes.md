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

## Connector library selection

The native schematic uses the existing EasyEDA/LCSC library device
`MINI_PCI-124P`, supplier part `C9900003781`, rather than a locally generated
symbol. The library data contains electrical contacts 1–124, a matching
footprint, and two mechanical latch pads numbered 0. The schematic connects all
124 electrical contacts by pin number to `hardware/interfaces/a203-pin-matrix.csv`;
the mechanical pin 0 is intentionally not connected.

This selection establishes a workable CAD device, not mechanical sign-off.
Connector height, key and latch geometry, module seating datum, and courtyard
must be checked against the physical A203 before fabrication. The unmodified
EasyEDA search response and exact library UUIDs are recorded under
`hardware/easyeda/library-import/`.

## Observations from supplied examples

These are review notes, not an A203 API specification.

### `BF01_InterConn.rar`

The archive contains two STM32F103/Keil projects: a BF01 application and a
bootloader. In the application, USART1 on PA9/PA10 is explicitly identified as
the BF01 communication link and USART2 on PA2/PA3 is the debug console. Both
are configured for 115200 baud, 8 data bits, one stop bit, no parity, and no
hardware flow control. The module link uses DMA transmit/receive and UART idle
line detection to delimit received traffic.

The wire format is visible in `User/app.c`:

- register reads start with the seven ASCII bytes `reg_br_`, followed by a
  big-endian 16-bit register address and a big-endian 16-bit word count;
- register writes start with `reg_bw_`, followed by a big-endian 16-bit
  register address and the payload bytes;
- the startup code reads from register zero, extracts register `0x000f`, TX/RX
  channel counts, IPv4 address, and MAC address, then writes configuration;
- mixer data is written at `0x3000`, TX route records at `0x0400 + 0x20*n`, RX
  route records at `0x0800 + 0x20*n`, and a network/update record at `0x0220`;
- the route builders contain UDP, multicast MAC/IP, port 5004, channel-count,
  and route-in-use fields, demonstrating that the host MCU can configure media
  routing without itself carrying the media stream.

The application does not initialise the STM32 Ethernet peripheral or implement
an IP stack. Ethernet HAL source files present in the project are generic
bundled framework code, not evidence of an Ethernet control implementation.

These observations make a UART-connected management MCU credible, but they do
not establish an A203 API. None of the undocumented register fields are treated
as stable A203 behavior yet because:

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
- The board will provide a separate physical control Ethernet port connected to
  an Ethernet-capable STM32 and its own 10/100 PHY. This port is deliberately
  independent of the A203 Dante/AES67 network port and does not carry audio.
- The STM32 will have a direct UART path to an A203 `COMS_RS_232_*` interface
  and a separate register/control path to the FPGA. The schematic will also
  preserve a selectable SPI alternative where practical; bus ownership must be
  unambiguous so the STM32 and FPGA cannot drive the A203 simultaneously.
- Initial STM32 firmware may use the BF01 example's 115200-baud DMA/idle-line
  transport as an integration hypothesis. Register operations remain disabled
  until Audiocom supplies an A203-specific specification or confirms in writing
  that the BF01 protocol and relevant register map apply.
- Initial bring-up uses 48 kHz/24-bit and a vendor-confirmed lane mode.
- The pre-schematic Yamaha-to-A203 audio/control adapter uses
  `XC6SLX16-2FTG256C`. Its ordering code and provisional banks are selected;
  schematic release still depends on each target's lane map, clock role, host
  startup behavior, buffering, electrical levels, and power requirements. See
  `../hardware/fpga-selection.md` and `../hardware/interfaces/`.
- USB compatibility hardware is included in the carrier plan, while its
  firmware is deferred and isolated from core bring-up.
- Vendor manuals, archives, binaries, and extracted examples remain untracked.
