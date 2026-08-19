# FPGA selection record

## Decision status

The architecture now assumes an FPGA, but the production ordering code is not
frozen. The leading baseline is **Lattice Certus-NX LFD2NX-25 in the 256-ball,
0.8 mm-pitch caBGA package**, subject to a completed pin/bank allocation,
portable RTL trial build, power estimate, and an authorised-distributor
availability check.

This choice is deliberately about I/O density, 3.3 V bank capacity, low-power
bridging, and maintainable tools. No high-speed transceivers or hard CPU are
required because the A203 owns the Ethernet/Dante/AES67 data plane.

## Provisional I/O budget

All counts include margin because several Yamaha and A203 control directions
remain unconfirmed.

| Interface | Provisional FPGA I/O | Basis |
| --- | ---: | --- |
| Yamaha audio/clocks | 30 | 12 inputs, 12 outputs, BCK/MCK/WCLK contacts and clock-direction margin |
| Yamaha MIDI/control/status | 16 | 10 MIDI plus detect, mute, reset, clock ownership, and spare status |
| A203 audio clocks/data | 24 | 16 data pins, MCLK/SCLK/LRCLK, external clocks, reset/mute, margin |
| A203 control/debug | 12 | UART/SPI/I2C selection and status; may reduce after protocol confirmation |
| Optional legacy-capable USB controller | 40 | 16-bit FIFO, FIFO controls, 8-bit register bus, status/frame/reset |
| Board configuration/debug/spares | 12 | straps, LEDs, triggers, recovery and future test |
| **Planning total** | **134** | Mostly 3.3 V single-ended I/O |

The final total may be lower if A203 control terminates in a dedicated MCU or
if the USB controller uses one multiplexed bus. It must not be reduced on paper
until the interfaces are captured in a pin-assignment spreadsheet.

## Minimum device requirements

| Area | Minimum | Preferred target |
| --- | --- | --- |
| 3.3 V-capable user I/O | 134 after configuration pins and bank restrictions | 150 or more, across enough independently powered banks |
| Logic | 15k class | 25k class for USB/control margin and debug instrumentation |
| Embedded RAM | 0.5 Mbit | 1 Mbit or more for dual-clock FIFOs, capture, and diagnostics |
| PLLs | 2 | 2-4; audio clock ownership still uses external/dedicated clock routing |
| Global/clock-capable inputs | Yamaha BCK/MCK/WCLK, A203 SCLK/LRCLK/MCLK, USB clock | At least six conveniently placed clock inputs |
| I/O performance | clean 24.576 MHz 3.3 V audio and 48 MHz synchronous USB FIFO | source-synchronous constraints and per-pin delay support |
| Configuration | external non-volatile image, JTAG | recoverable multiboot or golden image |
| Package | manufacturable BGA with enough grounds and bank access | 0.8 mm pitch, 14-15 mm body |
| Tools | supported Windows build, VHDL/SystemVerilog, timing analysis, on-chip debug | usable without a paid licence for this device |

The resource target does not include sample-rate conversion. The baseline
requires frequency-locked Yamaha and A203 clocks; asynchronous SRC would change
the signal-processing and memory requirements substantially.

## Candidate comparison

The figures below come from current manufacturer documentation reviewed on
2026-08-19. Package-specific bank allocation and configuration-pin sharing
still require a real pin-planning exercise.

| Candidate | Useful package facts | Fit | Main concern |
| --- | --- | --- | --- |
| **Lattice Certus-NX LFD2NX-25, caBGA256** | 25k logic cells; 1,440 kbit EBR + 512 kbit LRAM; 2 GPLLs; 205 total I/O comprising 159 wide-range, 40 high-performance, and 6 ADC pins; 14 x 14 mm, 0.8 mm pitch | Best present fit: the 159 wide-range pins can support the largely 3.3 V plan with useful margin | Requires Radiant licensing registration and a new tool flow; two PLLs leave less architectural margin than some alternatives |
| **AMD Spartan-7 XC7S50, CSGA324** | 210 user I/O in a 15 x 15 mm, 0.8 mm package; HR banks support 3.3 V; all Spartan-7 devices are supported by the no-cost Vivado tier | Strong conservative alternative and closest modern continuation of existing Xilinx/VHDL experience | Larger fabric than needed; more involved power/configuration design and a larger ball count |
| **Altera Cyclone 10 LP 10CL025, U256** | 25k logic elements, 594 kbit M9K RAM, 4 PLLs, up to 150 GPIO; 14 x 14 mm, 0.8 mm pitch; 3.3 V I/O; supported by Quartus Prime Lite | Meets the current I/O floor and has a straightforward free tool path | Least RAM and I/O margin of the shortlist; mature 60 nm family and bank/package planning may become tight with the full USB option |

Official references:

- [Lattice Certus-NX product table and current data sheet](https://www.latticesemi.com/Products/FPGAandCPLD/Certus-NX?ActiveTab=Data+Sheet)
- [Lattice Radiant licence options](https://www.latticesemi.com/Products/DesignSoftwareAndIP/FPGAandLDS/Radiant)
- [AMD 7-series package/I/O guide](https://docs.amd.com/r/en-US/ug475_7Series_Pkg_Pinout)
- [AMD Spartan-7 product page](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/spartan-7.html)
- [Altera Cyclone 10 LP device overview](https://www.intel.com/content/www/us/en/products/details/fpga/cyclone/10/lp.html)
- [Quartus Prime edition/device support](https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime/resource.html)

## Why Certus-NX-25 leads

The 25k device in caBGA256 is a better fit than selecting the largest Certus-NX
part by habit. In this package it exposes 159 wide-range I/O pins, whereas the
40k device exposes fewer wide-range pins because more pins are assigned to
high-performance functions. The design needs ordinary 3.3 V bridging I/O much
more than PCIe, DSP, or transceivers. Its nearly 2 Mbit of embedded memory is
also ample for bounded audio FIFOs and diagnostic capture without external
SDRAM.

The 0.8 mm pitch permits a more conventional escape strategy than the smaller
0.5 mm packages. A 14 mm body should leave more placement freedom around the
A203 and rear-panel connectors, subject to the physical chassis survey.

## Why not freeze it yet

Four checks can still reverse the recommendation:

1. A complete bank-aware pin assignment must prove that at least 134 required
   signals fit while preserving clock pins, configuration pins, JTAG, bank
   voltages, and PCB escape.
2. A small portable RTL project must synthesize and meet timing for Yamaha
   capture/serialization, TDM8 packing, dual-clock FIFOs, error counters, and a
   48 MHz 16-bit USB FIFO loopback.
3. The power estimate must fit the measured Yamaha +5 V budget together with
   the A203, PHY, and optional USB controller.
4. The exact device/speed/temperature/package ordering code must have acceptable
   lifecycle, lead time, and price from an authorised distributor at the point
   of schematic freeze.

If the pin plan exceeds the Certus-NX-25 wide-range-bank capacity, prefer the
Spartan-7 XC7S50 CSGA324 or a larger Certus-NX package rather than using fragile
voltage translation solely to preserve the initial choice.

## Prototype decision gate

Freeze the FPGA only when the repository contains:

- reviewed Yamaha and A203 pin matrices with direction, I/O standard, reset
  state, clock domain, and selected FPGA bank;
- a package escape sketch and preliminary stack-up;
- tool-generated utilisation, timing, and power reports for the portable trial
  design;
- a rail/inrush budget covering USB-populated and USB-unpopulated variants;
- a sourcing record for at least the FPGA, configuration flash, A203 connector,
  Ethernet PHY, USB controller, and Yamaha mating connector.
