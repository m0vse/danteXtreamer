# EasyEDA library import

`KEL_8831E-100-170L.lbr` is an Eagle XML library extracted without geometric
changes from the MIT-licensed AudioXtreamer project. It contains the existing
two-gate `8831E-100-170L` schematic symbol, the
`KEL_8831E-100-170L` footprint, and their complete pin-to-pad mapping.

EasyEDA Pro supports direct Eagle 6.0+ library import. Import this file using
**File > Import > EAGLE**, select library extraction, and save the resulting
device in the project or personal EasyEDA library. Place that library device in
the danteXtreamer schematic; do not explode it into inline graphics.

The retained AudioXtreamer MIT notice is in `LICENSE-AudioXtreamer`.

The source can be regenerated from the local AudioXtreamer checkout with:

```powershell
.\tools\extract-kel-eagle-library.ps1
```

After import, verify all 100 signal contacts plus the two shell pads against the
original KEL drawing and a physical connector before releasing a PCB. Format
conversion does not itself prove the footprint dimensions or pad numbering.

## Audiocom A203 socket

`EasyEDA-C9900003781.json` is an unmodified response from EasyEDA Pro's online
device search for `MINI_PCI-124P`, retrieved on 2026-08-19. It contains the
EasyEDA/LCSC library device, symbol, and footprint used directly by the native
project generator; it is not a locally drawn or exploded symbol.

Source endpoint:
`POST https://pro.easyeda.com/api/v2/devices/search` with the LCSC library and
search term `MINI_PCI-124P`. The selected device identifies supplier part
`C9900003781`. The JLC assembly listing `C9900177431` is not used because its
EasyEDA API entry does not provide a schematic component.

The EasyEDA/LCSC metadata does not establish that the connector will mate at
the required installed height. Verify the 0.8 mm contact pitch, key position,
board datum, latch locations, and height using the physical A203 before release.
