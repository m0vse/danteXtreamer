# AudioXtreamer-compatible USB bridge

## Purpose

The carrier includes provision for a bridge that would let existing
AudioXtreamer host software exchange
audio with the A203 without changing the A203's role as the XDante/AES67
endpoint. This is a compatibility feature, not the core network architecture.
The USB/bridge hardware is part of the board baseline; protocol firmware may be
implemented later.

On the replacement card, USB and A203 are two possible network/host-facing
consumers of the Yamaha MLN2-side audio. The hardware must define ownership,
clocking, and isolation so an inactive USB bridge cannot drive or load Yamaha or
A203 audio lanes. Concurrent USB and XDante/AES67 operation is not assumed.

## Known legacy behavior

The related AudioXtreamer sources describe a custom WinUSB path carrying packed
24-bit, channel-interleaved PCM. The host uses high-speed USB isochronous
transfers and a marker/framing convention; a separate ASIO DLL communicates
with the user-mode device process. The repository does not contain the FX2
firmware or complete USB descriptors, so host and FPGA source alone are not a
complete protocol specification.

The A203 serial side instead uses 32-bit slots with 24-bit data left-aligned.
The bridge therefore needs explicit pack/unpack, lane/slot mapping, buffering,
and clock-domain control.

## Isolation rules

- Keep all compatibility work under `src/usb-bridge/` and behind the common
  serial-audio boundary.
- Do not introduce ASIO, WinUSB, FX2, or Xilinx dependencies into core A203
  control or hardware integration.
- Do not copy the ASIO SDK into this repository.
- Do not copy legacy FX2/FPGA code until the exact component is needed, its MIT
  origin is recorded, and any embedded third-party/licensing concerns are
  resolved.
- Do not claim protocol compatibility until descriptor, control-request,
  framing, channel-order, recovery, and long-run tests pass.

## Hardware gates

1. Confirm A203 lane mapping and whether its clocks can be the bridge's audio
   clock reference.
2. Select bridge silicon with USB 2.0 High-Speed device capability, adequate
   serial-audio I/O, RAM/buffering, non-volatile storage, and supported tools.
3. Prove the unpowered/unprogrammed bridge cannot load or drive A203 signals;
   provide separate enable/reset and DNP-safe biasing.
4. Include the connector, VBUS sensing/back-power prevention, ESD protection,
   controlled-impedance routing, reference clock, debug/programming access, and
   clock/audio/reset test points in the carrier review.
5. Budget full-duplex payload and internal bus bandwidth for the intended
   channel/rate ceiling; do not assume USB Full Speed is adequate.

## Firmware enablement gates

1. Complete the native A203 48 kHz/24-bit milestone.
2. Capture or recover the complete legacy USB enumeration and streaming
   contract, including the missing FX2 firmware behavior.
3. Design a bounded elastic buffer and rate-control/recovery policy. The legacy
   per-packet pacing approach must not simply be repeated because its current
   project documents FIFO excursions, capture errors, resync events, and audible
   glitches.
4. Prove x86/x64 host interoperability, channel order, restart/recovery, and at
   least a multi-hour stability run before considering the bridge supported.

## Possible alternative

A standards-based USB Audio Class mode may be easier to maintain than permanent
compatibility with the custom WinUSB/ASIO protocol. It should be evaluated as a
separate mode, not silently substituted if exact AudioXtreamer compatibility is
a product requirement.
