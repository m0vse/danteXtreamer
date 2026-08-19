# Interface pin-planning records

These files are pre-schematic engineering records. They convert the reviewed
Yamaha and Audiocom documentation into explicit connector dispositions and a
bank-aware FPGA proposal. They are not substitutes for electrical measurements,
vendor reference schematics, or a tool-checked UCF.

- `yamaha-mln2-pin-matrix.csv` covers all 100 numbered MLN2 contacts. The two
  connector shell/anchor contacts numbered 101 and 102 in the AudioXtreamer
  Eagle library are grounded but are outside the advertised 100 signal contacts.
- `a203-pin-matrix.csv` covers all 124 A203 contacts. Pins assigned to the PHY,
  module flash/JTAG, power, or a debug header are deliberately not consumed by
  FPGA I/O.
- `fpga-pin-assignment.csv` is the proposed user-I/O assignment for
  `XC6SLX16-2FTG256C`. It reserves independent banks for Yamaha, A203, and the
  optional full-width FX2LP interface.

Directions are stated at the named device boundary. `input` in the Yamaha file
means input to the replacement card; `input` in the A203 file means input to the
A203. Unknown or multifunction behavior remains marked `verify`.

Before schematic release:

1. verify the 01X and i88X contacts electrically on real hardware;
2. obtain Audiocom's A203 carrier and control-protocol documentation;
3. import the FPGA CSV into an ISE constraints trial and pass placement/timing;
4. confirm every bank is powered at 3.3 V and that configuration pins are not
   loaded during startup;
5. review JLCPCB/LCSC stock again because all inventory figures are snapshots.
