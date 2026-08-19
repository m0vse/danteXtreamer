# USB bridge hardware requirements

The first carrier should be capable of supporting an AudioXtreamer-compatible
USB bridge without requiring a redesign. Firmware may follow later, and the
bridge section must be safe when unpopulated or held in reset.

## Functional capacity

- USB 2.0 High-Speed device operation (480 Mbit/s signalling); USB Full Speed is
  not a suitable design ceiling for multichannel 24-bit audio.
- Access to the shared audio-adapter FPGA rather than a second, competing set
  of A203 or Yamaha audio drivers.
- Deterministic DMA/data movement and enough RAM for bounded elastic buffering
  in both directions.
- A clocking architecture that can slave audio-side logic to the A203 or safely
  cross between A203 and USB timing domains.
- Non-volatile firmware storage plus a recoverable programming/debug path.

For capacity context only, 32 input plus 32 output channels at 48 kHz and 24
bits represent 73.728 Mbit/s of raw sample payload; at 96 kHz the raw payload is
147.456 Mbit/s, before USB framing and implementation overhead. These figures
do not establish that the A203 exposes 32x32 in one particular lane mode.

## USB physical design

- Select a device connector appropriate to the product; document shield and
  chassis strategy.
- Add VBUS detection and prevent back-powering between USB and carrier rails.
- Place low-capacitance ESD protection and any required common-mode component
  according to the selected PHY/controller reference design.
- Route D+/D- as a controlled 90-ohm differential pair with the length,
  discontinuity, and via budget required by the selected stack-up.
- Provide USB test access that does not create harmful stubs in production.

## Yamaha/A203-side isolation

- Route only measured Yamaha-host signals and vendor-confirmed A203
  serial-audio clocks/lanes to the bridge.
- Prevent an unpowered or reset bridge from driving or parasitically powering
  either Yamaha host or the A203. Use devices with appropriate fail-safe I/O or
  explicit isolation/gating where required.
- Provide an independently controlled bridge power rail and reset/enable.
- Make the unpopulated option electrically complete: no floating enables, clock
  contention, or interrupted Yamaha-to-A203 audio path.
- Add test points for MCLK, SCLK, LRCLK, selected SDIN/SDOUT lanes, bridge reset,
  and power rails with a documented probing strategy.

## Controller interface baseline

Reserve roughly 40 FPGA I/O for an interface at least as capable as the legacy
AudioXtreamer arrangement: a 16-bit synchronous data FIFO at 48 MHz, FIFO
address/read/write/output-enable/packet/flag controls, an 8-bit register bus,
and interrupt/busy/frame/reset indications. The buses may later be multiplexed
to reduce pins, but the first pin plan must prove the full compatibility case.

The USB controller section must be independently powered/reset and connect to
the core FPGA through explicit output enables. It must not connect directly as
a second driver of Yamaha or A203 clocks/data.

## Controller selection still open

The core audio-adapter FPGA is selected separately in `fpga-selection.md`.
Compare at least these USB-controller approaches:

- FX2LP or a compatible FIFO controller for the closest electrical/behavioral
  match to the incomplete legacy contract;
- a modern native USB High-Speed device MCU that can emulate the FIFO/register
  contract and has a maintainable firmware/debug flow;
- a replaceable controller mezzanine if lifecycle or protocol recovery makes a
  fixed on-board choice too risky.

Direct ULPI-to-FPGA USB is outside the baseline unless a maintainable,
appropriately licensed USB device core and verification plan are identified.

Selection depends on the recovered legacy USB descriptor/control contract,
development-tool longevity, firmware licensing, power, and component sourcing.
