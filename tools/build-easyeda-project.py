#!/usr/bin/env python3
"""Build the native EasyEDA Pro danteXtreamer schematic project.

The project is assembled from EasyEDA Pro library devices and the KEL device
converted by EasyEDA Pro's own Eagle importer.  It deliberately does not create
schematic symbols.  The A203 socket is the EasyEDA/LCSC MINI_PCI-124P device
C9900003781, retained as a source snapshot because it is not in the bundled
offline library supplied with EasyEDA Pro.
"""

from __future__ import annotations

import csv
import json
import shutil
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware" / "easyeda" / "danteXtreamer.eprj"
TEMPLATE = ROOT / "tmp" / "easyeda-native-example" / "Example_Quick Start.eprj"
SYSTEM_LIB = Path(
    r"C:\Program Files (x86)\easyeda-pro\resources\app\assets\db\easyeda-std.elib"
)
CONVERSIONS = {
    "KEL": ROOT / "tmp" / "kel-native-import.json",
    "FPGA": ROOT / "tmp" / "C39313-native-import.json",
    "FX2": ROOT / "tmp" / "C9926-native-import.json",
    "USB_C": ROOT / "tmp" / "C165948-native-import.json",
    "USB_ESD": ROOT / "tmp" / "C7519-native-import.json",
    "EEPROM": ROOT / "tmp" / "C6478-native-import.json",
    "FLASH": ROOT / "tmp" / "C82344-native-import.json",
    "BUCK": ROOT / "tmp" / "C43590-native-import.json",
    "INDUCTOR": ROOT / "tmp" / "C133191-native-import.json",
}
LIBRARY_SNAPSHOTS = {
    "A203_SOCKET": ROOT / "hardware" / "easyeda" / "library-import" / "EasyEDA-C9900003781.json",
}
SYSTEM_PARTS = {
    "MCU": "C36869",          # STM32F407ZET6
    "CTRL_PHY": "C45223",     # LAN8720A-CP-TR
    "DANTE_PHY": "C713256",   # 88E1512-A0-NNP2I000, provisional
    "CTRL_RJ45": "C12074",    # HR911105A 10/100 MagJack
    "DANTE_RJ45": "C54408",   # HR911130A Gigabit MagJack
}


def uid() -> str:
    return uuid.uuid4().hex


class Ids:
    def __init__(self) -> None:
        self.count = 1

    def new(self) -> str:
        value = f"eDX{self.count}"
        self.count += 1
        return value


IDS = Ids()


@dataclass
class Pin:
    number: str
    name: str
    x: float
    y: float
    pin_type: str


@dataclass
class Device:
    uuid: str
    title: str
    symbol_uuid: str
    footprint_uuid: str
    parts: dict[str, list[Pin]]
    boxes: dict[str, list[float]]


def records(data: str) -> list[list]:
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def parse_symbol(data: str) -> tuple[dict[str, list[Pin]], dict[str, list[float]]]:
    part = ""
    part_for_object: dict[str, str] = {}
    raw_pins: dict[str, dict] = {}
    parts: dict[str, list[Pin]] = {}
    boxes: dict[str, list[float]] = {}
    for item in records(data):
        if item[0] == "PART":
            part = item[1]
            parts.setdefault(part, [])
            boxes[part] = item[2].get("BBOX", [-50, -50, 50, 50])
        elif item[0] == "PIN":
            raw_pins[item[1]] = {
                "part": part,
                "number": "",
                "name": "",
                "type": "",
                "x": float(item[4]),
                "y": float(item[5]),
            }
            part_for_object[item[1]] = part
        elif item[0] == "ATTR" and item[2] in raw_pins:
            pin = raw_pins[item[2]]
            key = str(item[3]).upper()
            if key == "NAME":
                pin["name"] = str(item[4])
            elif key == "NUMBER":
                pin["number"] = str(item[4])
            elif key == "PIN TYPE":
                pin["type"] = str(item[4])
    for raw in raw_pins.values():
        parts[raw["part"]].append(
            Pin(raw["number"], raw["name"], raw["x"], raw["y"], raw["type"])
        )
    return parts, boxes


def copy_device(source: sqlite3.Connection, target: sqlite3.Connection, device_uuid: str,
                project_uuid: str) -> Device:
    columns = [row[1] for row in source.execute("PRAGMA table_info(devices)")]
    row = source.execute("SELECT * FROM devices WHERE uuid=?", (device_uuid,)).fetchone()
    if not row:
        raise KeyError(f"EasyEDA device {device_uuid} not found")
    values = dict(zip(columns, row))
    values["project_uuid"] = project_uuid
    target.execute(
        f"INSERT OR REPLACE INTO devices ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
        [values[column] for column in columns],
    )
    attrs = dict(source.execute(
        "SELECT key,value FROM attributes WHERE device_uuid=?", (device_uuid,)
    ).fetchall())
    for key, value in attrs.items():
        target.execute(
            "INSERT OR REPLACE INTO attributes(key,value,device_uuid) VALUES(?,?,?)",
            (key, value, device_uuid),
        )
    component_columns = [row[1] for row in source.execute("PRAGMA table_info(components)")]
    for component_uuid in {attrs.get("Symbol", ""), attrs.get("Footprint", "")} - {""}:
        component_row = source.execute(
            "SELECT * FROM components WHERE uuid=?", (component_uuid,)
        ).fetchone()
        if not component_row:
            continue
        component = dict(zip(component_columns, component_row))
        component["project_uuid"] = project_uuid
        target.execute(
            f"INSERT OR REPLACE INTO components ({','.join(component_columns)}) "
            f"VALUES ({','.join('?' for _ in component_columns)})",
            [component[column] for column in component_columns],
        )
    symbol_data = source.execute(
        "SELECT dataStr FROM components WHERE uuid=?", (attrs["Symbol"],)
    ).fetchone()[0]
    parts, boxes = parse_symbol(symbol_data)
    return Device(device_uuid, values["display_title"], attrs["Symbol"],
                  attrs.get("Footprint", ""), parts, boxes)


def import_conversion(path: Path, target: sqlite3.Connection, project_uuid: str) -> Device:
    payload = json.loads(path.read_text(encoding="utf-8"))["result"]
    source_device = next(
        device for device in payload["devices"] if device.get("attributes", {}).get("Symbol")
    )
    device_uuid = source_device["uuid"]
    target.execute(
        "INSERT OR REPLACE INTO devices(uuid,description,title,display_title,images,source,version,"
        "ticket,footprint_type,symbol_type,modifier_uuid,creator_uuid,owner_uuid,project_uuid) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            device_uuid, source_device.get("description", ""), source_device["title"],
            source_device["title"], source_device.get("images") or "",
            source_device.get("source", ""), source_device.get("version", ""), 1,
            source_device.get("footprint_type"), source_device.get("symbol_type"),
            None, None, None, project_uuid,
        ),
    )
    for key, value in source_device["attributes"].items():
        target.execute(
            "INSERT OR REPLACE INTO attributes(key,value,device_uuid) VALUES(?,?,?)",
            (key, str(value), device_uuid),
        )
    component_by_uuid = {
        item["uuid"]: item for item in payload.get("symbols", []) + payload.get("footprints", [])
    }
    for component_uuid in {
        source_device["attributes"].get("Symbol", ""),
        source_device["attributes"].get("Footprint", ""),
    } - {""}:
        item = component_by_uuid[component_uuid]
        target.execute(
            "INSERT OR REPLACE INTO components(uuid,title,display_title,description,source,version,"
            "ticket,docType,dataStr,project_uuid) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                item["uuid"], item["title"], item.get("display_title", item["title"]),
                item.get("desc", ""), item.get("source", ""), item.get("version", ""),
                1, item["docType"], item["dataStr"], project_uuid,
            ),
        )
    symbol_uuid = source_device["attributes"]["Symbol"]
    parts, boxes = parse_symbol(component_by_uuid[symbol_uuid]["dataStr"])
    return Device(device_uuid, source_device["title"], symbol_uuid,
                  source_device["attributes"].get("Footprint", ""), parts, boxes)


def import_pro_search_snapshot(path: Path, target: sqlite3.Connection,
                               project_uuid: str, supplier_part: str) -> Device:
    """Import an unmodified EasyEDA Pro library search result into the project."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    lists = payload.get("result", {}).get("lists", {})
    candidates = [item for group in lists.values() for item in group]
    source_device = next(
        item for item in candidates
        if item.get("attributes", {}).get("Supplier Part") == supplier_part
    )
    attrs = source_device["attributes"]
    symbol = source_device["symbol_info"]
    footprint = source_device["footprint_info"]
    if not symbol.get("dataStr") or not footprint.get("dataStr"):
        raise ValueError(f"EasyEDA snapshot {supplier_part} is missing symbol or footprint data")

    target.execute(
        "INSERT OR REPLACE INTO devices(uuid,description,title,display_title,images,source,version,"
        "ticket,footprint_type,symbol_type,modifier_uuid,creator_uuid,owner_uuid,project_uuid) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            source_device["uuid"], source_device.get("description", ""),
            source_device["title"], source_device["display_title"],
            json.dumps(source_device.get("images", [])), source_device.get("source", ""),
            str(source_device.get("version", "")), source_device.get("ticket", 1),
            source_device.get("footprint_type"), source_device.get("symbol_type"),
            source_device.get("modifier", {}).get("uuid"),
            source_device.get("creator", {}).get("uuid"),
            source_device.get("owner", {}).get("uuid"), project_uuid,
        ),
    )
    for key, value in attrs.items():
        target.execute(
            "INSERT OR REPLACE INTO attributes(key,value,device_uuid) VALUES(?,?,?)",
            (key, str(value), source_device["uuid"]),
        )
    for component in (symbol, footprint):
        target.execute(
            "INSERT OR REPLACE INTO components(uuid,title,display_title,description,source,version,"
            "ticket,docType,dataStr,project_uuid) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                component["uuid"], component["title"], component["display_title"],
                component.get("description", ""), component.get("source", ""),
                str(component.get("version", "")), component.get("ticket", 1),
                component["docType"], component["dataStr"], project_uuid,
            ),
        )
    parts, boxes = parse_symbol(symbol["dataStr"])
    return Device(source_device["uuid"], source_device["display_title"],
                  attrs["Symbol"], attrs["Footprint"], parts, boxes)


class Sheet:
    def __init__(self, title: str, note: str = "") -> None:
        self.title = title
        self.note = note
        self.items: list[list] = [
            ["DOCTYPE", "SCH", "1.1"],
            ["HEAD", {"originX": 0, "originY": 0, "version": "1.6.24.733bf2"}],
            ["LINESTYLE", "st_wire", None, None, None, None],
            ["LINESTYLE", "st_box", "#666666", 1, None, None],
            ["FONTSTYLE", "st_hidden", None, None, None, None, None, None, None, None, 2, 0],
            ["FONTSTYLE", "st_ref", None, None, "Arial", 12, None, 1, None, None, 2, 0],
            ["FONTSTYLE", "st_title", None, None, "Arial", 24, None, 1, None, None, 2, 0],
            ["FONTSTYLE", "st_heading", None, None, "Arial", 18, None, 1, None, None, 2, 0],
            ["FONTSTYLE", "st_note", None, None, "Arial", 13, None, None, None, None, 2, 0],
            ["FONTSTYLE", "st_warn", "#AA0000", None, "Arial", 13, None, 1, None, None, 2, 0],
        ]
        self.text(40, 35, title, "st_title")
        if note:
            self.text(40, 65, note, "st_warn" if "HOLD" in note.upper() else "st_note")

    def text(self, x: float, y: float, value: str, style: str = "st_note") -> None:
        self.items.append(["TEXT", IDS.new(), x, y, 0, value, style, 0])

    def box(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.items.append(["POLY", IDS.new(), [x1,y1,x2,y1,x2,y2,x1,y2,x1,y1], True, "st_box", 0])

    def component(self, device: Device, designator: str, part: str, x: float, y: float,
                  unique: str | None = None) -> list[Pin]:
        component_id = IDS.new()
        unique = unique or f"dx-{designator.lower()}"
        instance_attrs = {
            "Device": device.uuid,
            "Designator": designator,
            "Unique ID": unique,
        }
        if device.footprint_uuid:
            instance_attrs["Footprint"] = device.footprint_uuid
        self.items.append(["COMPONENT", component_id, part, x, y, 0, 0, instance_attrs, 0])
        box = device.boxes.get(part, [-50, -50, 50, 50])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Designator", designator, 0, 1,
            x + box[0], y + box[1] - 18, 0, "st_ref", 0,
        ])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Device", device.uuid, 0, 0,
            x, y, 0, "st_hidden", 0,
        ])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Name", "", 0, 0,
            None, None, 0, "st_hidden", 0,
        ])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Unique ID", unique, 0, 0,
            None, None, 0, "st_hidden", 0,
        ])
        return [Pin(p.number, p.name, p.x + x, p.y + y, p.pin_type)
                for p in device.parts[part]]

    def port(self, port_device: Device, net: str, x: float, y: float, side: str) -> None:
        component_id = IDS.new()
        rotation = 0 if side == "left" else 180
        self.items.append([
            "COMPONENT", component_id, "", x, y, rotation, 0,
            {"Device": port_device.uuid, "Name": net, "Unique ID": ""}, 0,
        ])
        name_x = x - 45 if side == "left" else x + 45
        self.items.append([
            "ATTR", IDS.new(), component_id, "Name", net, 0, 1,
            name_x, y, 0, "st_note", 0,
        ])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Device", port_device.uuid, 0, 0,
            x, y, 0, "st_hidden", 0,
        ])
        self.items.append([
            "ATTR", IDS.new(), component_id, "Unique ID", "", 0, 0,
            None, None, 0, "st_hidden", 0,
        ])

    def connect_port(self, port_device: Device, pin: Pin, net: str, origin_x: float,
                     spread: int = 75) -> None:
        side = "left" if pin.x < origin_x else "right"
        port_x = pin.x - spread if side == "left" else pin.x + spread
        wire_id = IDS.new()
        self.items.append(["WIRE", wire_id, [[pin.x, pin.y, port_x, pin.y]], "st_wire", 0])
        self.items.append([
            "ATTR", IDS.new(), wire_id, "NET", net, 0, 0,
            (pin.x + port_x) / 2, pin.y, 0, "st_hidden", 0,
        ])
        self.port(port_device, net, port_x, pin.y, side)

    def data(self) -> str:
        return "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                          for item in self.items)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "hardware" / "interfaces" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def first_part(device: Device) -> str:
    return next(iter(device.parts))


def pin_by_number(pins: list[Pin], number: str) -> Pin | None:
    return next((pin for pin in pins if pin.number.upper() == number.upper()), None)


def pin_by_name(pins: list[Pin], *names: str) -> Pin | None:
    wanted = {name.upper() for name in names}
    for pin in pins:
        variants = {pin.name.upper(), pin.name.upper().split("/")[0], pin.name.upper().split("(")[0]}
        if variants & wanted:
            return pin
    return None


def connect_names(sheet: Sheet, ports: Device, pins: list[Pin], origin_x: float,
                  mapping: dict[str, str]) -> None:
    used: set[str] = set()
    for pin_name, net in mapping.items():
        pin = pin_by_name(pins, pin_name)
        if pin and pin.number not in used:
            sheet.connect_port(ports, pin, net, origin_x)
            used.add(pin.number)


def overview() -> Sheet:
    sheet = Sheet("00 Architecture", "REV A ENGINEERING DRAFT — not fabrication ready")
    blocks = [
        (70, 180, 360, 320, "Yamaha 01X / i88X\nMLN2 connector\nKEL 8831E-100-170L"),
        (480, 180, 790, 320, "Spartan-6 LX16\nclock/audio adaptation\nsafe-state + buffering"),
        (920, 180, 1230, 320, "Audiocom A203\nXDante / AES67 endpoint\n124-pin Mini PCI socket"),
        (1350, 180, 1640, 320, "Gigabit PHY + MagJack\nDante/AES67 media port\nPHY circuit HOLD"),
        (480, 470, 790, 610, "STM32F407 control MCU\nA203 UART + FPGA SPI\nmanagement firmware"),
        (920, 470, 1230, 610, "LAN8720A + MagJack\nindependent 10/100\ncontrol Ethernet port"),
        (70, 470, 360, 610, "Optional FX2LP USB 2.0\nAudioXtreamer protocol\nhardware fitted, firmware later"),
    ]
    for x1, y1, x2, y2, label in blocks:
        sheet.box(x1, y1, x2, y2)
        sheet.text(x1 + 25, y1 + 45, label, "st_heading")
    for x1, y1, x2, y2 in [
        (360,250,480,250), (790,250,920,250), (1230,250,1350,250),
        (360,540,480,540), (790,540,920,540), (790,300,790,470),
    ]:
        sheet.items.append(["WIRE", IDS.new(), [[x1,y1,x2,y2]], "st_wire", 0])
    sheet.text(70, 710, "Media network and control network are physically independent. The STM32 does not carry Dante audio.")
    sheet.text(70, 745, "Audiocom BF01 sample evidence: UART 115200 8-N-1, DMA/idle framing, reg_br_/reg_bw_. Verify A203 compatibility.")
    sheet.text(70, 780, "A203 connector is EasyEDA/LCSC C9900003781. Verify physical connector height and latch geometry; gigabit PHY remains provisional.", "st_warn")
    return sheet


def yamaha_sheet(kel: Device, ports: Device) -> Sheet:
    sheet = Sheet("01 Yamaha MLN2 connector", "KEL device imported from the AudioXtreamer Eagle library; every contact is retained")
    rows = {row["contact"]: row for row in read_csv("yamaha-mln2-pin-matrix.csv")}
    positions = [(520, 390), (1370, 390)]
    for index, (part, position) in enumerate(zip(kel.parts, positions), start=1):
        pins = sheet.component(kel, f"J1.{index}", part, *position, unique="dx-j1")
        for pin in pins:
            row = rows.get(pin.number)
            if not row:
                continue
            net = row["design_net"].strip()
            if net:
                sheet.connect_port(ports, pin, net, position[0], 95)
    sheet.text(40, 980, "Unknown/detect contacts remain named and are not silently tied. Series protection and direction control are placed on the FPGA sheet.", "st_warn")
    return sheet


def a203_sheet(socket: Device, ports: Device) -> Sheet:
    sheet = Sheet("02 Audiocom A203 socket", "EasyEDA/LCSC MINI_PCI-124P C9900003781; verify height and latch geometry on the physical A203 before PCB release")
    rows = read_csv("a203-pin-matrix.csv")
    rows_by_pin = {row["pin"]: row for row in rows}
    position = (850, 500)
    pins = sheet.component(socket, "J3", first_part(socket), *position, unique="dx-j3")
    electrical_pins = [pin for pin in pins if pin.number != "0"]
    expected = {str(number) for number in range(1, 125)}
    actual = {pin.number for pin in electrical_pins}
    if actual != expected or set(rows_by_pin) != expected:
        raise ValueError("A203 connector/library pin set is not exactly 1..124")
    for pin in electrical_pins:
        row = rows_by_pin[pin.number]
        signal = row["signal"]
        if signal == "GND":
            net = "GND"
        elif signal == "3.3V":
            net = "+3V3_A203"
        elif row["fpga_ball"]:
            assignment = next((item for item in read_csv("fpga-pin-assignment.csv")
                               if item["ball"] == row["fpga_ball"]), None)
            net = assignment["fpga_signal"] if assignment else f"A203_{signal}"
        elif row["owner"] == "ethernet_phy":
            net = f"A203_{signal}"
        elif signal.startswith("COMS_RS_232"):
            net = f"A203_{signal}"
        else:
            net = f"A203_{signal}_HOLD"
        sheet.connect_port(ports, pin, net, position[0], 115)
    sheet.text(40, 870, "Library device includes contacts 1..124 plus footprint latch pads numbered 0. The symbol's mechanical pin 0 is intentionally not routed.", "st_note")
    sheet.text(40, 900, "All electrical contacts are named from hardware/interfaces/a203-pin-matrix.csv; unresolved functions retain _HOLD nets.", "st_warn")
    return sheet


def fpga_sheet(fpga: Device, ports: Device, flash: Device) -> Sheet:
    sheet = Sheet("03 Spartan-6 FPGA", "XC6SLX16-2FTG256C / JLC C39313 — provisional pin assignment, run ISE before release")
    assignments = {row["ball"].upper(): row["fpga_signal"]
                   for row in read_csv("fpga-pin-assignment.csv")}
    positions = [(320,300),(860,300),(1400,300),(320,790),(860,790),(1400,790),(1940,790)]
    for index, (part, position) in enumerate(zip(fpga.parts, positions), start=1):
        pins = sheet.component(fpga, f"U1.{index}", part, *position, unique="dx-u1")
        for pin in pins:
            net = assignments.get(pin.number.upper())
            upper = pin.name.upper()
            if not net and upper == "VCCINT": net = "+1V2_FPGA"
            if not net and (upper.startswith("VCCAUX") or upper.startswith("VCCO")): net = "+3V3_LOGIC"
            if not net and upper == "GND": net = "GND"
            if net:
                sheet.connect_port(ports, pin, net, position[0], 85)
    flash_part = first_part(flash)
    flash_pins = sheet.component(flash, "U2", flash_part, 1840, 180)
    connect_names(sheet, ports, flash_pins, 1840, {
        "CS#":"FPGA_CSO_N", "DO":"FPGA_DIN", "DI":"FPGA_MOSI",
        "CLK":"FPGA_CCLK", "VCC":"+3V3_LOGIC", "GND":"GND",
    })
    return sheet


def usb_sheet(fx2: Device, usb_c: Device, esd: Device, eeprom: Device, ports: Device) -> Sheet:
    sheet = Sheet("04 Optional USB bridge", "FX2LP hardware provision only; AudioXtreamer-compatible firmware is deferred")
    fx_part = first_part(fx2)
    fx_pins = sheet.component(fx2, "U3", fx_part, 650, 520)
    mapping = {
        "DPLUS":"USB_DP", "DMINUS":"USB_DM", "IFCLK":"USB_IFCLK",
        "RDY0":"USB_SLRD_N", "RDY1":"USB_SLWR_N", "RESET#":"USB_RESET_N",
        "SDA":"USB_EEPROM_SDA", "SCL":"USB_EEPROM_SCL", "XTALIN":"USB_XTAL_IN",
        "XTALOUT":"USB_XTAL_OUT", "PA2":"USB_SLOE_N", "PA4":"USB_FIFOADDR0",
        "PA5":"USB_FIFOADDR1", "PA6":"USB_PKTEND_N",
    }
    for i in range(8):
        mapping[f"PB{i}"] = f"USB_FD{i}"
        mapping[f"PD{i}"] = f"USB_FD{i+8}"
        mapping[f"PC{i}"] = f"USB_LSI_D{i}"
    connect_names(sheet, ports, fx_pins, 650, mapping)
    for pin in fx_pins:
        if pin.name.upper() in {"VCC","AVCC"}: sheet.connect_port(ports,pin,"+3V3_USB",650)
        elif pin.name.upper() in {"GND","AGND"}: sheet.connect_port(ports,pin,"GND",650)

    uc_pins = sheet.component(usb_c, "J2", first_part(usb_c), 1450, 250)
    for pin in uc_pins:
        name = pin.name.upper()
        net = None
        if "VBUS" in name: net = "USB_VBUS"
        elif "GND" in name or "SHELL" in name: net = "GND"
        elif "CC1" in name: net = "USB_CC1"
        elif "CC2" in name: net = "USB_CC2"
        elif "D+" in name or name.startswith("DP"): net = "USB_DP_RAW"
        elif "D-" in name or name.startswith("DM") or name.startswith("DN"): net = "USB_DM_RAW"
        if net: sheet.connect_port(ports,pin,net,1450)
    esd_pins = sheet.component(esd, "U4", first_part(esd), 1450, 570)
    for number, net in {"1":"USB_DP_RAW","6":"USB_DP","3":"USB_DM_RAW","4":"USB_DM","2":"GND","5":"USB_VBUS"}.items():
        pin = pin_by_number(esd_pins, number)
        if pin: sheet.connect_port(ports,pin,net,1450)
    ee_pins = sheet.component(eeprom, "U5", first_part(eeprom), 1450, 800)
    connect_names(sheet, ports, ee_pins, 1450, {"SDA":"USB_EEPROM_SDA","SCL":"USB_EEPROM_SCL","VCC":"+3V3_USB","GND":"GND"})
    return sheet


def control_sheet(mcu: Device, phy: Device, rj45: Device, ports: Device) -> Sheet:
    sheet = Sheet("05 Independent control Ethernet", "STM32F407 + LAN8720A; this port manages FPGA/A203 and does not carry Dante audio")
    mcu_pins = sheet.component(mcu, "U10", first_part(mcu), 560, 520)
    mcu_map = {
        "PA1":"CTRL_RMII_REF_CLK", "PA2":"CTRL_RMII_MDIO", "PC1":"CTRL_RMII_MDC",
        "PA7":"CTRL_RMII_CRS_DV", "PC4":"CTRL_RMII_RXD0", "PC5":"CTRL_RMII_RXD1",
        "PG11":"CTRL_RMII_TX_EN", "PG13":"CTRL_RMII_TXD0", "PG14":"CTRL_RMII_TXD1",
        "PA9":"A203_COMS_RS_232_RX_B", "PA10":"A203_COMS_RS_232_TX_B",
        "PB12":"FPGA_CTRL_CS_N", "PB13":"FPGA_CTRL_SCK", "PB14":"FPGA_CTRL_MISO", "PB15":"FPGA_CTRL_MOSI",
        "NRST":"MCU_RESET_N", "BOOT0":"MCU_BOOT0",
    }
    connect_names(sheet, ports, mcu_pins, 560, mcu_map)
    phy_pins = sheet.component(phy, "U11", first_part(phy), 1250, 480)
    connect_names(sheet, ports, phy_pins, 1250, {
        "REF_CLK":"CTRL_RMII_REF_CLK", "MDIO":"CTRL_RMII_MDIO", "MDC":"CTRL_RMII_MDC",
        "CRS_DV":"CTRL_RMII_CRS_DV", "RXD0":"CTRL_RMII_RXD0", "RXD1":"CTRL_RMII_RXD1",
        "TX_EN":"CTRL_RMII_TX_EN", "TXD0":"CTRL_RMII_TXD0", "TXD1":"CTRL_RMII_TXD1",
        "TXP":"CTRL_PHY_TXP", "TXN":"CTRL_PHY_TXN", "RXP":"CTRL_PHY_RXP", "RXN":"CTRL_PHY_RXN",
        "NRST":"CTRL_PHY_RESET_N", "VDD1A":"+3V3_CTRL", "VDD2A":"+3V3_CTRL", "VDDIO":"+3V3_CTRL", "GND":"GND",
    })
    jack_pins = sheet.component(rj45, "J10", first_part(rj45), 1850, 480)
    connect_names(sheet, ports, jack_pins, 1850, {
        "TD+":"CTRL_PHY_TXP", "TD-":"CTRL_PHY_TXN", "RD+":"CTRL_PHY_RXP", "RD-":"CTRL_PHY_RXN",
        "GND":"GND",
    })
    sheet.text(40, 1010, "A203 UART pin voltage and output-enable behavior remain to be confirmed before fitting the link resistors.", "st_warn")
    return sheet


def dante_sheet(phy: Device, rj45: Device, ports: Device) -> Sheet:
    sheet = Sheet("06 A203 Dante Ethernet", "DESIGN HOLD: 88E1512 and strap network are provisional until Audiocom supplies its validated carrier reference")
    phy_pins = sheet.component(phy, "U20", first_part(phy), 700, 520)
    rgmii = {
        "RGMII_TXC":"A203_RGMII_TXC", "RGMII_TX_CTL":"A203_RGMII_TX_EN",
        "RGMII_TXD0":"A203_RGMII_TXD0", "RGMII_TXD1":"A203_RGMII_TXD1",
        "RGMII_TXD2":"A203_RGMII_TXD2", "RGMII_TXD3":"A203_RGMII_TXD3",
        "RGMII_RXC":"A203_RGMII_RXC", "RGMII_RX_CTL":"A203_RGMII_RX_DV",
        "RGMII_RXD0":"A203_RGMII_RXD0", "RGMII_RXD1":"A203_RGMII_RXD1",
        "RGMII_RXD2":"A203_RGMII_RXD2", "RGMII_RXD3":"A203_RGMII_RXD3",
        "MDC":"A203_MDC", "MDIO":"A203_MDIO",
        "MDIP0":"DANTE_MDI0_P", "MDIN0":"DANTE_MDI0_N", "MDIP1":"DANTE_MDI1_P", "MDIN1":"DANTE_MDI1_N",
        "MDIP2":"DANTE_MDI2_P", "MDIN2":"DANTE_MDI2_N", "MDIP3":"DANTE_MDI3_P", "MDIN3":"DANTE_MDI3_N",
    }
    connect_names(sheet, ports, phy_pins, 700, rgmii)
    jack_pins = sheet.component(rj45, "J20", first_part(rj45), 1550, 520)
    pair_map = {
        "MX1+":"DANTE_MDI0_P", "MX1-":"DANTE_MDI0_N", "MX2+":"DANTE_MDI1_P", "MX2-":"DANTE_MDI1_N",
        "MX3+":"DANTE_MDI2_P", "MX3-":"DANTE_MDI2_N", "MX4+":"DANTE_MDI3_P", "MX4-":"DANTE_MDI3_N",
        "TD1+":"DANTE_MDI0_P", "TD1-":"DANTE_MDI0_N", "TD2+":"DANTE_MDI1_P", "TD2-":"DANTE_MDI1_N",
        "TD3+":"DANTE_MDI2_P", "TD3-":"DANTE_MDI2_N", "TD4+":"DANTE_MDI3_P", "TD4-":"DANTE_MDI3_N",
    }
    connect_names(sheet, ports, jack_pins, 1550, pair_map)
    sheet.text(40, 1010, "Do not fabricate this sheet until RGMII I/O voltage, delay ownership, PHY choice, straps, reset timing and magnetics are confirmed.", "st_warn")
    return sheet


def power_sheet(buck: Device, inductor: Device, ports: Device) -> Sheet:
    sheet = Sheet("07 Power rails", "Preliminary topology only; current, inrush, sequencing and thermal limits require measurement")
    rails = [("U30","L30","+3V3_LOGIC",360),("U31","L31","+3V3_A203",900),("U32","L32","+1V2_FPGA",1440)]
    for uref,lref,rail,x in rails:
        bpins = sheet.component(buck, uref, first_part(buck), x, 420)
        connect_names(sheet, ports, bpins, x, {"AVIN":"+5V_PROTECTED","PVIN":"+5V_PROTECTED","SW":rail+"_SW","FB":rail+"_FB","VOS":rail,"EN":"POWER_ENABLE","AGND":"GND","PGND":"GND"})
        lpins = sheet.component(inductor, lref, first_part(inductor), x, 760)
        for number,net in {"1":rail+"_SW","2":rail}.items():
            pin=pin_by_number(lpins,number)
            if pin: sheet.connect_port(ports,pin,net,x)
    sheet.text(40, 960, "Capacitor population, feedback values, A203 load budget and FPGA package decoupling must be completed before PCB conversion.", "st_warn")
    return sheet


def insert_sheet(db: sqlite3.Connection, project_uuid: str, schematic_uuid: str,
                 sheet: Sheet, number: int) -> str:
    document_uuid = uid()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO documents(uuid,title,display_title,description,docType,dataStr,sheet_id,ticket,"
        "sort_ticket,created_at,updated_at,schematic_uuid,project_uuid) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (document_uuid, f"p{number}", sheet.title, sheet.note, 1, sheet.data(), number, 1,
         number, now, now, schematic_uuid, project_uuid),
    )
    return document_uuid


def main() -> None:
    for required in [TEMPLATE, SYSTEM_LIB, *CONVERSIONS.values(), *LIBRARY_SNAPSHOTS.values()]:
        if not required.exists():
            raise FileNotFoundError(required)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE, OUT)
    db = sqlite3.connect(OUT)
    system = sqlite3.connect(f"file:{SYSTEM_LIB.as_posix()}?mode=ro", uri=True)
    template = sqlite3.connect(f"file:{TEMPLATE.as_posix()}?mode=ro", uri=True)
    try:
        for table in ["attributes","components","devices","documents","schematics","projects",
                      "project_members","boards","coppers","texts","resources","backups"]:
            db.execute(f"DELETE FROM {table}")
        project_uuid = uid()
        schematic_uuid = uid()
        owner = "0819f05c4eef4c71ace90d822a990e87"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO projects(uuid,archive,name,content,cbb_project,thumb,ticket,g_ticket,owner_uuid,"
            "creator_uuid,created_at,updated_at,boards,block_symbol_attrs_groups,pcb_count,default_sheet) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (project_uuid,0,"danteXtreamer","Native EasyEDA Pro hardware design",0,"",1,1,owner,owner,now,now,"[]","{}",0,""),
        )
        db.execute("INSERT INTO project_members(role,project_uuid,user_uuid) VALUES(?,?,?)", (1,project_uuid,owner))

        devices = {name: import_conversion(path, db, project_uuid)
                   for name, path in CONVERSIONS.items()}
        devices["A203_SOCKET"] = import_pro_search_snapshot(
            LIBRARY_SNAPSHOTS["A203_SOCKET"], db, project_uuid, "C9900003781"
        )
        for name, supplier_part in SYSTEM_PARTS.items():
            found = system.execute(
                "SELECT d.uuid FROM devices d JOIN attributes a ON a.device_uuid=d.uuid "
                "WHERE a.key='Supplier Part' AND a.value=? LIMIT 1", (supplier_part,)
            ).fetchone()
            if not found:
                raise KeyError(f"EasyEDA system library has no {supplier_part}")
            devices[name] = copy_device(system, db, found[0], project_uuid)

        # Sheet ports are themselves normal EasyEDA library devices.
        port_uuid = "f9cca3776d314593982404edbe420be3"
        ports = copy_device(template, db, port_uuid, project_uuid)

        sheets = [
            overview(),
            yamaha_sheet(devices["KEL"], ports),
            a203_sheet(devices["A203_SOCKET"], ports),
            fpga_sheet(devices["FPGA"], ports, devices["FLASH"]),
            usb_sheet(devices["FX2"], devices["USB_C"], devices["USB_ESD"], devices["EEPROM"], ports),
            control_sheet(devices["MCU"], devices["CTRL_PHY"], devices["CTRL_RJ45"], ports),
            dante_sheet(devices["DANTE_PHY"], devices["DANTE_RJ45"], ports),
            power_sheet(devices["BUCK"], devices["INDUCTOR"], ports),
        ]
        document_ids = [insert_sheet(db, project_uuid, schematic_uuid, sheet, i+1)
                        for i, sheet in enumerate(sheets)]
        epoch = int(time.time())
        db.execute(
            "INSERT INTO schematics(uuid,description,ticket,sheet_count,project_uuid,name,display_name,"
            "createtime,updatetime,sort) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (schematic_uuid,"Rev A engineering draft",1,len(sheets),project_uuid,"schematic","Schematic",epoch,epoch,",".join(document_ids)),
        )
        db.execute("UPDATE projects SET default_sheet=? WHERE uuid=?", (document_ids[0], project_uuid))
        db.commit()
        check = db.execute("PRAGMA integrity_check").fetchone()[0]
        if check != "ok":
            raise RuntimeError(check)
    finally:
        template.close()
        system.close()
        db.close()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
