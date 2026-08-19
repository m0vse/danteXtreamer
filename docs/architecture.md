# Architecture baseline

## Scope and system boundary

The product replaces the MLN2 card in Yamaha 01X and i88X devices. The A203
terminates the replacement's XDante/AES67 network-audio function. The core
product is therefore a hardware integration around four boundaries:

1. **Yamaha host side:** the original MLN2 mechanical envelope and the 01X/i88X
   power, reset, serial-audio, clock, status, and control interfaces.
2. **Network side:** the A203's Ethernet MAC/PHY-facing signals and the external
   network components required by the vendor's reference design.
3. **Audio adaptation:** synchronous I2S/TDM data, word/bit/master clocks, lane
   mapping, and mute/lock behavior between the Yamaha MLN2 boundary and A203.
4. **Control side:** Yamaha host compatibility plus A203 reset and a
   vendor-confirmed UART, SPI, I2C, or other
   configuration path.

There is no Windows streaming path in the core design. A desktop utility may
eventually configure or diagnose the product, but it would not carry the A203's
XDante/AES67 media stream.

The A203 documentation establishes neither MLN2 compatibility nor the Yamaha
host behavior. `mln2-replacement.md` defines the project requirement and the
evidence needed before compatibility is claimed.

## Logical components

### A203 carrier integration

The carrier supplies 3.3 V, grounding, reset, connector mechanics, and any
external Ethernet PHY/magnetics required by the confirmed reference design.
Power sequencing, rail current, reset timing, PHY choice, and strap requirements
remain blocking questions; the manual does not provide enough information for a
schematic freeze.

### Yamaha MLN2 compatibility layer

The replacement carrier must fit the original card location and safely adapt
the Yamaha host interface to the A203. This includes mechanical mounting,
connector/pin compatibility, power/reset behavior, audio lane and clock mapping,
mute/status handling, and any host startup/identification traffic.

01X and i88X support are separate profiles. A common carrier is desirable but
will be selected only after passive measurements prove which signals and
mechanics are actually shared. Unknown host signals are inputs to a
characterisation plan, not candidates for guessed connections.

### Serial-audio adapter

The adapter converts the Yamaha host's MLN2-side audio representation to the
A203's serial-audio contract:

- 32-bit slots;
- 24-bit or 16-bit samples left-aligned and zero-padded;
- sampling on the rising SCLK edge and output changes on the falling edge;
- I2S or TDM4/8/16, with LRCLK edge polarity configurable somewhere outside the
  supplied manual.

The pre-schematic baseline now uses an FPGA. It captures and serialises the
Yamaha 24-bit left-justified stereo lines, maps channels into A203 TDM slots,
crosses bounded phase/reset differences through elastic FIFOs, monitors clock
lock and FIFO health, and owns safe-state output enables. The legacy Xilinx
ISE/Spartan-6 implementation is evidence about the Yamaha interface, not RTL to
inherit as a proven transport.

The leading mapping hypothesis is twelve Yamaha stereo lines into three TDM8
lanes, with a fourth zero/unrouted lane if the A203 requires a 32-channel group.
This makes the TDM bit clock equal to a 256 x Fs Yamaha clock at 48 and 96 kHz.
It remains conditional on measuring which Yamaha BCK/MCK connector contact
actually carries that clock and on an A203-specific lane map/external-clock
confirmation. See `../hardware/hardware-baseline.md`.

### Control adapter

All module control will sit behind a narrow interface such as discovery,
read-only status, configuration transaction, and reset. No register addresses
or packet formats from the BF01 examples are promoted into this interface until
Audiocom confirms that they apply to the A203 and may be used.

### Diagnostics and validation

Diagnostics should record configuration, clock role, sample rate, mute/lock
state, route identity, packet/network observations, channel map, error counters,
and run duration. Hardware captures and vendor dumps stay out of source control
when they contain proprietary material or device identifiers.

### USB bridge hardware provision

The carrier architecture includes a USB 2.0 High-Speed device path even though
its compatibility firmware may follow later. The board must reserve:

- a USB device connector, ESD protection, VBUS detection, and controlled-
  impedance D+/D- routing;
- a bridge processing footprint or module interface capable of sustained
  high-speed USB, multichannel serial audio, bounded buffering, and firmware
  update/debug;
- access to the confirmed A203 audio lanes and MCLK/SCLK/LRCLK so the bridge can
  share or measure the audio clock domain;
- independently controllable bridge power/reset so an unprogrammed or
  unpopulated bridge cannot load A203 signals or disturb native network audio;
- clock/audio/reset test points and enough non-volatile storage/RAM for the
  eventual implementation.

The FPGA is shared with the core audio adapter. The board should reserve an
independently powered USB High-Speed controller and an FPGA bus at least as
capable as the legacy 16-bit, 48 MHz FX2 FIFO plus register interface. The USB
controller ordering code remains open. Direct ULPI-to-FPGA USB is not the
baseline because it adds a USB device core and avoidable verification/licensing
risk. See `../hardware/usb-bridge-requirements.md`.

## Clocking model

The manual says the A203 has an onboard VCXO, always outputs MCLK, and can lock
its generated audio clocks to an external clock. It also discusses LRCLK_IN and
SCLK_IN, but the pin table names pin 68 `EXTERNL_CLK` and does not explicitly map
that pin to `SCLK_IN`.

Bench bring-up must leave the uncertain clock input undriven and first observe
the A203 as clock master. The proposed installed 48 kHz milestone then uses the
Yamaha host as reference and asks the A203 to lock to conditioned Yamaha WCLK
and the measured 256 x Fs source only after Audiocom confirms the pin/mode. The
carrier also preserves a separately gated reverse WCLK route for a later
network-master mode. Capture MCLK, SCLK, LRCLK, MUTE, FIFO occupancy, and
lock-loss together; never enable both clock owners. No asynchronous sample-rate
converter is in the baseline.

## USB compatibility bridge

The bridge is included in the hardware plan but remains a peer of the local
audio subsystem, not the network transport:

```text
existing AudioXtreamer host software
        | custom USB/WinUSB stream
optional USB bridge (packing, buffering, clock-domain control)
        | A203 serial audio (I2S/TDM)
       A203
        | XDante/AES67 network
```

Compatibility firmware requires the missing legacy FX2 descriptors/firmware
behavior to be recovered or separately specified. The bridge must not copy the
legacy output-pacing scheme without solving its documented underrun/
resynchronization problems. Hardware may be fitted and safely held inactive
before that firmware exists. Details and gates are in `usb-bridge.md`.

## First integration milestone

**Goal:** replace the original MLN2 card in one target Yamaha unit and prove one
stable bidirectional XDante/AES67 route at the A203 manual's clearly advertised
48 kHz, 24-bit operating point using measured Yamaha host behavior and a
vendor-confirmed A203 serial-audio mode.

Entry criteria:

- confirmed carrier/reference schematic requirements and maximum 3.3 V load;
- confirmed target-specific MLN2 connector, mechanics, rails, reset/startup,
  clocking, audio lanes/slots, and safe unpowered behavior;
- confirmed PHY/network connection and reset/power sequence;
- confirmed A203 control interface and a safe way to select/read the test mode;
- confirmed serial-audio lane and channel ordering for the chosen mode.

Pass criteria:

- the module powers and resets without exceeding limits;
- the Yamaha host starts normally with the prototype installed and the
  replacement neither contends with nor back-powers host signals;
- clocks and MUTE/lock behavior match the confirmed configuration;
- a reference XDante/AES67 endpoint can send and receive the selected channels;
- an impulse/channel-ID pattern proves direction and channel order;
- a 30-minute run shows no audible discontinuity or observed sample slip;
- the exact hardware, firmware, configuration, PTP state, and measurements are
  recorded in a reproducible test report.

The same target-specific compatibility matrix must then pass on the other
Yamaha device. Scaling channel count, adding rates/modes, or enabling USB
compatibility firmware follows only after the baseline passes. USB-capable
hardware may already be present but must remain electrically benign.
