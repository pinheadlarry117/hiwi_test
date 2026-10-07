import xml.etree.ElementTree as ET
import pandas as pd

RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def parse_cim_xml(xml_file):
    """
    Parse a CIM RDF/XML file into a long-format DataFrame.

    Parameters
    ----------
    xml_file : str
        Path to EQ, TP, SV, or SSH XML file.

    Returns
    -------
    pd.DataFrame
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = []

    for elem in root:

        obj_id = (
            elem.attrib.get(f"{{{RDF_NS}}}ID")
            or elem.attrib.get(f"{{{RDF_NS}}}about")
        )

        if not obj_id:
            continue

        for child in elem:

            tag = child.tag.split("}")[-1]

            if f"{{{RDF_NS}}}resource" in child.attrib:
                resource = child.attrib[f"{{{RDF_NS}}}resource"]
                value = None
            else:
                resource = None
                value = child.text

            data.append(
                {
                    "id": obj_id,
                    "type": tag,
                    "resource": resource,
                    "value": value,
                }
            )

    return pd.DataFrame(data)


def save_csv(xml_file, output_csv):
    """
    Parse CIM XML and save to CSV.
    """

    df = parse_cim_xml(xml_file)

    df.to_csv(output_csv, index=False)

    print(f"Saved {len(df)} rows to {output_csv}")

    return df