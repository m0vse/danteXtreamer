# Open integration questions

Questions marked **blocking** must be answered before the associated design or
implementation is committed.

## Yamaha MLN2 replacement boundary

1. **Blocking:** Obtain or derive an authorised MLN2 connector pinout for both
   01X and i88X, including direction, voltage, reset state, and unused pins.
   The local 01X service manual is available; equivalent i88X documentation is
   still missing.
2. **Blocking:** Are the two devices electrically and mechanically identical at
   the card boundary? Document every difference rather than assuming a shared
   interface from the MLN2 name.
3. **Blocking:** Measure the card outline, connector datum, mounting holes,
   keep-outs, chassis/shield contacts, cable clearance, and thermal envelope in
   both devices.
4. **Blocking:** What rails, current/inrush, sequencing, reset, presence detect,
   identification, and startup handshake does each Yamaha host require?
5. **Blocking:** Map every audio lane, slot, direction, word/bit/master clock,
   sample format, channel, and supported rate for both targets.
6. Which MIDI, control-surface, status, word-clock, or other non-audio functions
   traverse MLN2 and must the replacement preserve them?
7. What happens when the original card is absent, slow to start, muted, clock
   unlocked, or reporting a fault, and what behavior must be emulated?
8. Can one PCB safely support both devices through population/firmware options,
   or are separate carrier variants required?
9. Which target should be used for the first installed prototype, and what
   evidence is required before repeating the test on the other?

## Carrier and electrical

1. **Blocking:** What is the A203 maximum and typical 3.3 V current, supply
   tolerance, inrush profile, sequencing requirement, and required decoupling?
2. **Blocking:** Is there an Audiocom carrier/reference schematic and validated
   PCB stack-up/connector recommendation for the 124-pin interface?
3. **Blocking:** What are the required assertion/deassertion timing, pull state,
   and voltage limits for `nRESET_IN`?
4. What loads, if any, may be placed on the 2.5 V, 1.25 V reference, and 1.1 V
   output pins?
5. What is the exact direction, active level, reset state, and debounce/filter
   expectation for `MUTE`?
6. Are unused GPIO, SPI, UART, JTAG, flash, and auxiliary pins to be left open,
   pulled, or strapped?

## Ethernet/network side

1. **Blocking:** Does the carrier require an external RGMII/MII PHY, magnetics,
   and connector? If so, which PHY and delay/strap configuration is validated?
2. **Blocking:** What are the RGMII voltage, timing, trace-length, and clock-delay
   requirements? The supplied manual lists signals but no timing budget.
3. Which XDante/Dante control software and firmware versions are supported?
4. What AES67 profile details are implemented: PTP version/domain, multicast
   addressing, RTP payloads, packet times, SAP/SDP discovery, and stream limits?
5. Are primary/secondary redundant network ports supported by this module, or
   is only one MAC interface exposed?
6. What firmware update method is authorised for production, and what recovery
   path exists after an interrupted update?

## Serial audio and clocking

1. **Blocking:** Provide the exact channel-to-lane/slot map for I2S and
   TDM4/8/16 at 48 and 96 kHz in both directions.
2. **Blocking:** How are I2S/TDM mode, LRCLK polarity, sample width, channel
   count, mixer, and clock role selected?
3. **Blocking:** Is pin 68 `EXTERNL_CLK` the `SCLK_IN` described later in the
   manual? If not, where is `SCLK_IN` exposed?
4. Is the A203 expected to be SCLK/LRCLK master in the normal use case? What
   restrictions apply when locking to external clocks?
5. What is the actual supported rate set? The headline specification says
   48/96 kHz while timing tables mention 44.1-family and higher rates.
6. Does 32x32 use four TDM8 lanes, two TDM16 lanes, or another mapping?
7. What is the module's latency from serial audio to network and back for each
   supported packet time/mode?

## Control protocol

1. **Blocking:** Which physical interface controls the A203 in the intended
   integration: UART A/B, SPI A/B, I2C, network control, or a combination?
2. **Blocking:** Obtain the A203-specific register/protocol/API document and its
   redistribution rules.
3. Do either BF01 example project or the UDP demo apply to A203? If so, which
   version and which commands/registers are stable public interfaces?
4. Confirm UART voltage levels, framing, baud rate, output-enable behavior, flow
   control, message framing, checksums, timeouts, and reset recovery.
5. What read-only identity/status operation is safe for first bring-up?
6. Which configuration is persistent, and how is factory recovery performed?

## AudioXtreamer USB bridge

1. **Blocking for schematic freeze:** What bridge device or module provides
   USB 2.0 High-Speed device operation, the required A203 serial-audio lanes,
   sufficient RAM/buffering, and a maintainable toolchain?
2. **Blocking for schematic freeze:** Which A203 lanes/clocks must be routed to
   the bridge, and what electrical isolation guarantees an unpowered,
   unprogrammed, or unpopulated bridge cannot load them?
3. **Blocking for schematic freeze:** Select connector, VBUS/back-power policy,
   ESD protection, High-Speed routing constraints, reference clock, debug/
   programming path, and bridge power/reset controls.
4. Is compatibility required with the current AudioXtreamer Windows application
   and ASIO driver, or only with its packed PCM/framing concept?
5. Obtain the missing FX2 firmware, USB descriptors, VID/PID policy, endpoint
   layout, alternate settings, and vendor-control request definitions, with
   usable licensing.
6. Define the exact legacy marker/framing behavior and error recovery from a
   capture rather than relying only on host/FPGA code.
7. Define an asynchronous clock-domain strategy. Mirroring individual USB input
   packet counts is not acceptable as the only output-rate control because the
   legacy project records underruns and resynchronisation glitches.
8. Decide whether compatibility justifies maintaining a custom WinUSB/ASIO path
   instead of exposing a standard USB Audio Class interface as a separate mode.
