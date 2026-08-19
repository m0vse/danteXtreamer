# Hardware baseline

## Status

This is the pre-schematic baseline for the first `danteXtreamer` carrier. It
defines the blocks, interfaces, safe states, and validation gates needed to
replace the MLN2 card in a Yamaha 01X or i88X. It does not claim that the A203
control protocol, Ethernet PHY circuit, or final channel map is known.

The implementation baseline uses an FPGA for deterministic audio-format
adaptation and clock-domain handling. The FPGA does not implement Dante,
AES67, Ethernet packet processing, or the normal Windows audio path; those
network functions terminate in the A203.

The selected device is `XC6SLX16-2FTG256C`. Its proposed 122-signal assignment
uses bank 3 for Yamaha, bank 0 for A203 audio/SPI, bank 1 for the optional FX2LP,
and bank 2 for remaining A203 control/debug. See `interfaces/` for the complete
connector and bank matrices.

## Evidence behind the baseline

The Yamaha 01X and i88X service manuals show the same MLN2 circuit family and a
100-pin board-to-board `mLAN2-I/F` boundary. The 01X connects its DM board
directly to MLN2 CN6; the i88X connects the same boundary through its DMSUB
board. This is strong evidence for a common replacement-card electrical
boundary, but connector height, board outline, mounting points, rear-panel
clearance, and every product-specific signal use still need physical checks.

The manuals and the working AudioXtreamer reference design establish this
useful subset of the Yamaha-side interface:

- twelve serial audio lines in each direction;
- two 24-bit, MSB-first, left-justified channels per serial line;
- Yamaha clock contacts for WCK, BCK, and MCK in both directions; the legacy
  replacement treats its selected `BCKI` net as a 256 x Fs working clock, while
  the Yamaha block diagram separately labels BCK as 64 x Fs and MCK as
  256 x Fs, so the actual connector waveform/name pairing must be measured;
- five MIDI inputs and five MIDI outputs used by the 01X reference design;
- a +5 V host supply on the connector, from which the earlier replacement
  design was powered;
- additional detect, clock-direction, mute, reset, and status signals whose
  exact product behavior still needs measurement.

The A203 manual establishes eight SDIN and eight SDOUT pins, 32-bit slots,
I2S/TDM4/8/16 modes, clock inputs and outputs, 3.3 V I/O, an onboard VCXO, and
RGMII/MII and PHY-management pins. It does not supply the control/register
contract, PHY reference circuit, power budget, or authoritative lane map.

Local evidence pages reviewed for this baseline are Yamaha 01X service-manual
pages 135-136 and 149-151, Yamaha i88X service-manual pages 87 and 90-91, and
the A203 Hardware Manual Rev 1.2 pages 2-7. The PDFs remain ignored vendor
references; the page citations do not grant redistribution rights.

## Proposed block diagram

```text
 Yamaha 01X/i88X host
 100-pin MLN2 boundary
     | 12 x stereo TX/RX, BCK/MCK/WCLK, MIDI, detect/status, +5V
     v
 protection / series damping / clock mux and buffer / safe-state gating
     |
     +---------------------------> FPGA <-----------------------------+
     |                        format adapter                          |
     |             channel mapper + elastic FIFOs                    |
     |            clock/reset monitor + diagnostics                  |
     |                                                               |
     |                      A203 TDM SDIN/SDOUT                       |
     |                    SCLK/LRCLK/MCLK/reset                       |
     v                                                               |
 Audiocom A203                                                       |
     | RGMII/MII + MDIO/MDC                                          |
     v                                                               |
 vendor-confirmed Ethernet PHY -> magnetics/RJ45                      |
                                                                     |
 USB-C -> ESD/VBUS -> optional USB 2.0 HS controller -> 16-bit FIFO --+

 +5V host -> input protection/current measurement -> point-of-load rails
                                                    -> A203 3.3V
                                                    -> FPGA core/aux/I/O
                                                    -> optional USB rail
```

## Yamaha interface

The replacement should use the original 100-pin mating connector and reproduce
only signal behavior confirmed from the service schematics and measurements.
The schematic should group the connector into:

| Group | Provision |
| --- | --- |
| Audio from Yamaha | 12 inputs to FPGA, series damping footprints, optional weak bias only after reset-state measurements |
| Audio to Yamaha | 12 FPGA outputs behind output-enable control, default high-impedance until configuration and clock lock |
| Clocks | Confirmed Yamaha BCK/MCK/WCLK contacts into clock-capable FPGA pins and an external clock-routing network; reverse WCLK path separately enabled |
| MIDI | Five inputs and five outputs routed to FPGA; output drivers disabled at power-up |
| Detect/control/status | Route confirmed signals through series resistors to FPGA or strap matrix; do not guess pulls or directions |
| Power/ground | Use the confirmed +5 V contacts and all applicable ground contacts; do not use the host's other rails without measurement |

The exact 100-pin signal matrix belongs in a separate reviewed pin-assignment
file before schematic capture. Service-manual net names are not enough to
establish voltage tolerance, reset state, or whether the i88X uses every 01X
signal identically.

## Audio adaptation

### Initial packing proposal

If measurement confirms the legacy implementation's 256 x Fs Yamaha working
clock, it is 12.288 and 24.576 MHz at 48 and 96 kHz. Those frequencies match
the bit-clock required for eight 32-bit TDM slots. The least complex initial
packing hypothesis is therefore:

- capture twelve Yamaha stereo lines as 24 channels;
- pack them into three A203 TDM8 lanes in each direction;
- reserve a fourth TDM8 lane for zero-filled/unrouted channels if the A203
  requires a fixed 32-channel group;
- left-align each 24-bit sample in a 32-bit A203 slot and force the low eight
  bits to zero.

This is a design hypothesis, not a documented A203 lane map. Audiocom must
confirm that TDM8 is selectable, identify lane/slot ordering, state whether
three active lanes are permitted, and identify how the module treats unused
slots. A channel-ID/impulse test must verify both directions before the mapping
is frozen.

### Clock domains and slip policy

The installed first-milestone mode should make the Yamaha unit the audio-clock
source and ask the A203 to lock its VCXO to conditioned Yamaha WCLK and the
confirmed 256 x Fs clock. This
matches the Yamaha boundary, avoids asynchronous sample-rate conversion, and
uses the A203's documented external-lock concept. It is conditional on vendor
confirmation that pin 68 is `SCLK_IN` and that the proposed TDM8 external-clock
mode is valid.

The A203 output clocks may be phase-shifted from the Yamaha inputs even when
frequency-locked. The FPGA should therefore use shallow dual-clock elastic
FIFOs between Yamaha and A203 domains, with occupancy, underflow, overflow, and
lock-loss counters. A FIFO absorbs bounded phase and reset differences; it is
not a remedy for clocks with different average rates. Persistent occupancy
drift must mute the route and report an error rather than silently repeat or
drop samples.

Hardware should also preserve a separately gated A203-to-Yamaha WCLK path for a
later network-clock-master mode. Only one clock owner may be enabled at a time.
Use clock-capable pins and dedicated clock buffers/multiplexers where required;
do not gate externally visible clocks through ordinary combinational LUTs.

## A203 carrier section

The carrier should expose all documented A203 audio lanes even if the first
firmware uses only three or four. Place source-series resistor footprints on
SCLK, LRCLK, MCLK, and serial outputs, and provide high-impedance test pads that
do not create production stubs.

Required A203 support blocks are:

- a current-limited, measured 3.3 V rail with local bulk and high-frequency
  decoupling based on a vendor reference design;
- reset supervisor/open-drain reset control and an unambiguous safe mute state;
- routing/strap options for `LRCLK_IN`, the documented external-clock pin,
  SCLK, LRCLK, and MCLK;
- UART, SPI, and I2C access through a 0-ohm selection matrix and debug header,
  without assuming which interface is the production control port;
- vendor-confirmed treatment of unused GPIO, JTAG, auxiliary, and analogue
  reference/output pins.

Do not use the A203's 2.5 V, 1.25 V-reference, or 1.1 V output pins to power
carrier circuitry until their load limits are documented.

## Ethernet section

The A203 pin list exposes RGMII/MII, MDIO/MDC, PHY reset, and interrupt signals.
The provisional carrier therefore reserves an external PHY, magnetics, and an
RJ45 in the rear-panel area. No PHY part, strap values, clock source, I/O
voltage, or RGMII delay scheme should be selected until Audiocom supplies or
approves a reference circuit. The FPGA is not in this media path.

The PHY/RJ45 region and USB region require a controlled-impedance stack-up,
continuous reference planes, chassis/shield strategy, and ESD return path. A
six-layer starting point is reasonable for placement studies, but the final
layer count follows the A203/PHY reference layout and escape analysis rather
than becoming a requirement here.

## Optional USB compatibility section

Include USB 2.0 High-Speed hardware on the first PCB, but make it independently
powerable and safe when not populated. For the best chance of matching the
existing AudioXtreamer host contract, reserve a controller-to-FPGA interface at
least as capable as the legacy FX2 arrangement:

- 16-bit synchronous data bus at 48 MHz;
- FIFO read/write/output-enable, address, flag, and packet-end controls;
- an 8-bit register/control bus plus interrupt/busy/frame indications;
- controller reset, boot EEPROM/flash, programming UART/JTAG as applicable,
  and VBUS sensing;
- USB-C configured as a USB 2.0 device-only port, with ESD protection and no
  carrier back-power path.

The selected first-board controller is the stocked 100-pin EZ-USB FX2LP
`CY7C68013A-100AXC`, which has enough GPIOs for both legacy buses. Its
manufacturer-discontinued status is accepted for this low-volume compatibility
design and requires buy-ahead stock before schematic release. The active FX2G3
successor is a future non-pin-compatible redesign rather than a dual footprint.
Direct ULPI-to-FPGA USB is not the baseline because it adds a USB device
core and substantially increases firmware, verification, and licensing risk.
The USB section must not sit in the native Yamaha-to-A203 path.

## Power, reset, and safe states

Use the Yamaha +5 V input only after measuring available steady-state current,
inrush allowance, and connector contact allocation in both products. The power
tree should provision:

- protected +5 V entry with current measurement and an optional current-limit
  switch for the first prototypes;
- dedicated A203 3.3 V regulation sized only after Audiocom supplies current
  and transient requirements;
- FPGA core, auxiliary, and 3.3 V I/O rails following the selected device's
  reference sequence;
- an independently switchable USB-controller rail;
- supervisor-generated resets and power-good signals visible to FPGA and test
  headers;
- no conduction from USB VBUS or an unpowered FPGA/controller into Yamaha or
  A203 pins.

Before FPGA configuration, Yamaha-facing and A203-facing outputs must be
high-impedance or held at a measured safe level. A watchdog or lock-loss event
must mute/disable outbound audio before changing clock ownership. Recovery must
not require removing the Yamaha unit from the chassis.

## Configuration and diagnostics

Provide:

- external configuration flash sized for at least two FPGA images if the
  chosen family supports recoverable multiboot;
- accessible FPGA JTAG, controller debug, and A203 control/debug headers;
- a recovery strap that prevents normal audio outputs from enabling;
- LEDs for input power, FPGA configured, A203 reset/mute/lock, Ethernet link,
  and USB state, subject to rear-panel visibility;
- test points for every power rail, Yamaha WCLK/BCK/MCK, A203 MCLK/SCLK/LRCLK,
  one data lane each way, reset, mute, and FIFO error trigger;
- optional header pins for a logic-analyser trigger and occupancy/error status.

## Mechanical partition

The placement study should start with the original MLN2 connector datum and
mounting holes, then reserve the former IEEE-1394 rear-panel area for RJ45 and
optional USB. The A203 is approximately 59.6 x 44.6 mm according to its manual;
fit, component height, airflow, service access, and cable clearance must be
checked in both Yamaha chassis before freezing the FPGA package or committing
to a USB mezzanine versus on-board implementation.

## Suggested schematic sheets

1. Yamaha 100-pin interface and protection
2. FPGA banks, configuration, JTAG, and safe-state controls
3. A203 connector, audio clocks/data, reset, and control-selection matrix
4. Ethernet PHY, magnetics, RJ45, and chassis/shielding
5. USB High-Speed controller, connector, boot storage, and FPGA FIFO bus
6. Power entry, regulators, sequencing, reset supervisor, and measurement
7. Debug headers, test points, LEDs, and population options

## First hardware milestone

Build a current-limited prototype that boots in one Yamaha target with USB held
off, operates at 48 kHz/24-bit with Yamaha as clock master, and proves a small
bidirectional channel set through XDante/AES67. Expand to all mapped channels
only after clock lock, FIFO stability, mute/reset behavior, and channel order
are captured. Repeat the electrical and functional matrix in the second Yamaha
target before claiming a common production board.
