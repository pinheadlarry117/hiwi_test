import xml.etree.ElementTree as ET
import pandas as pd

#tree = ET.parse(r"C:\Users\yga-hzh\Downloads\21060207T0628Z_XX_YYY_bak\21060207T0628Z_XX_YYY_SV.xml")
#tree = ET.parse(r"C:\Users\yga-hzh\Downloads\21060207T0628Z_XX_YYY_bak\21060207T0628Z_XX_YYY_TP.xml")
tree = ET.parse(r"C:\Users\yga-hzh\Downloads\21060207T0628Z_XX_YYY_bak\21060207T0628Z_YYY_EQ.xml")
root = tree.getroot()

# Print root tag
print(root.tag)

"""
for elem in root:
    for child in elem:
        # remove namespace
        tag = child.tag.split('}')[-1]

        print(tag)
"""

data = []

for elem in root:
    print(elem.tag, elem.attrib)

    # Get object ID
    obj_id = (
        elem.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}ID')
        or elem.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
    )


    if not obj_id:
        continue

    for child in elem:
        tag = child.tag.split('}')[-1]       # e.g. SvPowerFlow.p          # e.g. p, q, Terminal

        # Case 1: resource (Terminal)
        if '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource' in child.attrib:
            resource = child.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
            value = None

        # Case 2: value (p, q)
        else:
            resource = None
            value = child.text

        data.append({
            "id": obj_id,
            "resource": resource,
            "type": tag,
            "value": value
        })

# Create DataFrame
df = pd.DataFrame(data)

# Save
df.to_csv("CIM_EQ.csv", index=False)

print(df.head())

