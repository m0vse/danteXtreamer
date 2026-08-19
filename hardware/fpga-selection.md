# FPGA selection record

## Decision

The first board targets **AMD/Xilinx Spartan-6 `XC6SLX16-2FTG256C`**:

- JLCPCB/LCSC part: **`C39313`**
- package: 256-ball FTG/FBGA; 17 x 17 mm; 1.0 mm pitch
- temperature grade: commercial; 0 to 85 deg C
- user I/O: 186
- primary design tools: Xilinx ISE 14.7

The pin-compatible industrial `XC6SLX16-2FTG256I` (`C415800`) is an approved
alternate if thermal analysis requires -40 to 100 deg C. Do not mix grades in a
production run without updating the BOM and timing/power review.

This is a deliberate mature-device choice. It reuses proven AudioXtreamer
constraints and RTL structure, is presently inexpensive and well stocked for
JLCPCB assembly, and has enough package I/O for Yamaha, A203, and optional USB
at the same time. Its cost is the obsolete ISE workflow and a shorter remaining
manufacturer support horizon than a new FPGA family.

## What the FPGA does

The FPGA does not implement Dante, AES67, Ethernet, or USB signalling:

- the A203 owns Dante/AES67 and its external Ethernet PHY interface;
- an optional EZ-USB FX2LP owns USB 2.0 High-Speed signalling and endpoints;
- the FPGA captures and emits Yamaha serial audio/MIDI, packs and unpacks A203
  TDM lanes, routes channels, crosses clock domains, and exposes diagnostics;
- the same channel router may feed A203 and USB concurrently.

Simultaneous A203 and USB operation is therefore within the architectural
scope. It is not considered proven until a combined ISE build meets timing and
hardware loopback runs without FIFO drift, underrun, or overrun.

## Capacity evidence

The existing AudioXtreamer `xc6slx16-2-ftg256` post-route report is the most
relevant measured baseline because it already contains the Yamaha 12-in/12-out
serial lanes, five MIDI paths each way, 16-bit FX2 FIFO, eight-bit LSI control
bus, and dual-clock audio FIFOs.

| Resource | Existing routed use | Device capacity | Headroom |
| --- | ---: | ---: | ---: |
| Slice registers | 4,891 | 18,224 | 73% |
| Slice LUTs | 4,792 | 9,112 | 47% |
| Bonded I/O | 77 | 186 | 109 pins |
| RAMB8BWER | 32 | 64 | 50% |
| BUFG/BUFGMUX | 2 | 16 | 87% |
| DCM | 0 | 4 | 100% |
| DSP48A1 | 0 | 32 | 100% |
| PLL_ADV | 0 | 2 | 100% |

The A203 addition needs eight serial inputs, eight serial outputs, five clock
contacts, and a bounded control set. TDM pack/unpack and counters are small
relative to the remaining 4,320 LUTs. New elastic FIFOs should use remaining
block RAM rather than distributed LUT RAM.

The current package assignment reserves 122 user I/O:

| Bank | Capacity | Assigned | Primary owner | Free |
| --- | ---: | ---: | --- | ---: |
| 0 | 40 | 31 | A203 audio and SPI/status | 9 |
| 1 | 50 | 39 | optional full-width FX2LP interface | 11 |
| 2 | 40 | 12 | A203 UART/I2C and board debug | 28 |
| 3 | 56 | 40 | Yamaha audio/MIDI/clocks | 16 |
| **Total** | **186** | **122** |  | **64** |

All 122 balls were checked against AMD's official
`6slx16ftg256pkg.txt`; every proposed ball exists and matches its stated bank.
All four banks are provisionally 3.3 V LVCMOS. The final UCF and ISE placer are
still authoritative.

Dedicated/reserved configuration connections are separate from the 122 user
I/O count: JTAG `C14/C12/A15/E14`; `PROGRAM_B` T2; `DONE` P13; `INIT_B` R3;
master-SPI `CCLK` R11, `DIN/MISO` P10, and `MOSI/CSI_B` T10. `HSWAPEN` C4 is
not allocated as user I/O. External devices must not drive multifunction
configuration pins during startup.

The design acceptance target is below 80% LUT, below 80% block RAM, no bank
over-allocation, no unconstrained clocks or CDC paths, and positive timing
margin at Yamaha/A203 audio clocks and the 48 MHz FX2 interface.

## JLCPCB assembly and availability snapshot

Observed on **2026-08-19**; inventory and pricing are volatile and must be
rechecked at BOM release:

| Part | JLCPCB status | Observed stock | One-off indication | Use |
| --- | --- | ---: | ---: | --- |
| [`XC6SLX16-2FTG256C` / `C39313`](https://jlcpcb.com/partdetail/XC6SLX16-2FTG256C/C39313) | Extended; Standard PCBA; MSL 3; X-ray required | 2,058 | about US$7.72 | primary FPGA |
| [`XC6SLX16-2FTG256I` / `C415800`](https://jlcpcb.com/partdetail/XC6SLX16-2FTG256I/C415800) | Extended; Standard PCBA; MSL 3; X-ray required | LCSC 905 | about US$14.86 | industrial alternate |
| [`CY7C68013A-100AXC` / `C9926`](https://jlcpcb.com/partdetail/CypressSemicon-CY7C68013A100AXC/C9926) | Extended; Economic/Standard PCBA; manufacturer-discontinued | LCSC 2,140 | about US$13.15 | selected first-board USB controller |

The cheaper/smaller FX2LP `CY7C68013A-56LTXC` (`C14912`) is not the baseline:
its 24 GPIOs cannot expose the existing 16-bit FIFO plus independent eight-bit
LSI/control bus without a firmware and FPGA protocol redesign. It may be studied
later as a multiplexed-interface cost reduction.

[Infineon lists `CY7C68013A-100AXC` as end-of-life](https://www.infineon.com/part/CY7C68013A-100AXC)
and identifies [`CYUSB2316-BF104AXI` FX2G3 as active and preferred](https://www.infineon.com/part/CYUSB2316-BF104AXI).
FX2G3 supports a 16-bit bidirectional Slave FIFO and has maintained firmware
examples, but uses a non-pin-compatible 104-LGA footprint. No JLC/LCSC catalogue
entry was found on 2026-08-19; Mouser search results showed 2,328 in stock.
Therefore Rev A selects buy-ahead `C9926` for protocol compatibility. FX2G3 is
retained as a future board-revision option rather than a first-board footprint.
The full 39-signal FPGA interface remains reserved.

AMD currently states Spartan-6 support through at least 2030. That is useful but
not a perpetual availability guarantee. For every prototype or production lot:

1. recheck JLCPCB stock and assembly classification;
2. verify device top-mark and authorised sourcing status;
3. buy/pre-order enough Extended parts for the run plus rework yield;
4. retain the industrial ordering code as a BOM alternate;
5. archive the final JLC BOM/placement result with the hardware revision.

## USB hardware reference

The ZTEX USB-FPGA Module 2.01 schematic confirms the legacy architecture:

- a 100-pin EZ-USB FX2 with PB/PD as the 16-bit `FD` bus;
- PC0..7 as the separate LSI/GPIF address/control byte;
- PA/CTL/RDY and selected PE signals for FIFO and status control;
- a 24 MHz crystal, I2C boot EEPROM, USB connector, and reset supervisor;
- FX2 access to Spartan-6 configuration and JTAG plus an SPI configuration
  flash on the module.

Reference: [ZTEX USB-FPGA Module 2.01 circuit diagram](https://www.ztex.de/downloads/usb-fpga-2.01.pdf).
The PDF is stored only in ignored `vendor/ztex/` local material; redistribution
rights have not been assumed. The new carrier keeps the signal capability but
places USB on FPGA bank 1, isolating it from the bank-2 master-SPI boot path.

## Why not Certus-NX for this revision

Certus-NX remains a credible migration family, but it would require porting and
validating the full RTL/tool flow. The package variants with enough wide-range
3.3 V I/O were not as readily available through the intended JLCPCB supply
chain at review time. Spartan-6 already has measured resource evidence and
excellent JLC/LCSC stock. The old toolchain is accepted for this board revision
with a reproducible build environment and archived installer/license notes.

## Remaining decision gates

The FPGA ordering code is selected, but schematic release remains blocked by:

- a combined Yamaha/A203/FX2 top-level trial build and real ISE timing report;
- A203 electrical/control and Ethernet-PHY reference documentation;
- measured Yamaha clock names, voltage levels, reset states, power, and inrush;
- thermal/power estimates showing the commercial 85 deg C grade is adequate;
- BGA escape and JLCPCB stack-up review;
- a fresh sourcing snapshot immediately before parts are pre-ordered.
