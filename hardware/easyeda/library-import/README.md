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
