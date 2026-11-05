"""Verify Orca trial results and package editable plates without machine G-code."""
import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("sliced_directory",type=Path)
args=parser.parse_args()
out=Path(__file__).resolve().parents[1]/"full-lamp-v09"
data=json.loads((out/"Build-map.json").read_text())
assert not any(data[field] for field in ("self_intersections","printed_pairwise_overlaps",
                                         "carrier_skin_intersections"))
projects=out/"Slicer-projects"
projects.mkdir(exist_ok=True)
groups = {
    **{key: {p["file"] for p in data["prints"] if p.get("type")=="ribbon" and p["band"]==key}
       for key in "ABCD"},
    "Splices": {p["file"] for p in data["prints"] if p["type"]=="splice"},
    "Mounts": {p["file"] for p in data["prints"] if p["type"]=="mount pad"},
    "Centre": {p["file"] for p in data["prints"] if p["type"]=="cover"},
}
report = []
for key,names in groups.items():
    job=args.sliced_directory/key/f"{key}-check.3mf"
    result=projects/f"{key}-Kobra-S1-Max.3mf"
    with zipfile.ZipFile(job) as src:
        sliced=ET.fromstring(src.read("Metadata/slice_info.config"))
        plates=sliced.findall("plate")
        objects = set()
        predicted_g = predicted_s = 0
        warnings = set()
        for plate in plates:
            metadata={item.get("key"):item.get("value") for item in plate.findall("metadata")}
            assert metadata["outside"]=="false"
            plate_file=f"Metadata/plate_{metadata['index']}.gcode"
            assert src.getinfo(plate_file).file_size>10000, (key,plate_file)
            predicted_g+=float(metadata["weight"])
            predicted_s+=int(metadata["prediction"])
            for obj in plate.findall("object"):
                assert obj.get("skipped")=="false", obj.attrib
                objects.add(obj.get("name").split("_id_",1)[0])
            warnings.update(item.get("msg") for item in plate.findall("warning"))
        assert objects==names, (key,objects,names)
        model=ET.fromstring(src.read("Metadata/model_settings.config"))
        for plate in model.findall("plate"):
            for item in plate.findall("metadata"):
                if item.get("key")=="gcode_file":
                    plate.remove(item)
        assert len(model.findall("plate")) == len(plates)
        with zipfile.ZipFile(result,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as dest:
            for entry in src.namelist():
                if ".gcode" in entry or entry=="Metadata/slice_info.config":
                    continue
                if entry=="Metadata/model_settings.config":
                    dest.writestr(entry,ET.tostring(model,encoding="utf-8",xml_declaration=True))
                else:
                    dest.writestr(entry,src.read(entry))
        report.append(dict(project=result.name,parts=len(objects),plates=len(plates),
                           estimated_PETG_g=round(predicted_g,1),estimated_hours=round(predicted_s/3600,1),
                           Orca_warnings=sorted(warnings)))
    with zipfile.ZipFile(result) as verify:
        assert verify.testzip() is None
        assert not any(".gcode" in entry for entry in verify.namelist())
assert sum(job["parts"] for job in report)==data["print_count"]
(out/"Slicer-check.json").write_text(json.dumps(
    dict(engine="OrcaSlicer 2.4.2",preset="Anycubic Kobra S1 Max / 0.4 mm / Generic PETG / 0.16 mm",
         scope="Toolpaths generated for every object. Editable projects omit G-code. Confirm the actual filament, support marks and adhesion at the machine.",projects=report),indent=2)+"\n")
for job in report:
    print(job)
