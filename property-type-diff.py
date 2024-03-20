'''
MIT License

Copyright (c) 2024 David Carlstedt Ringius

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

------------------------------------------------------------------------------

Helper program for finding differences in property types between software updates.
Property types from https://source.android.com/docs/automotive/vhal/property-configuration.
Last update: 20/3/2024.
    -- DcfCR

------------------------------------------------------------------------------
'''

from json import loads


def remove_code_comments(code):
    multiline_start_index = code.find("/*")
    while multiline_start_index != -1:  # Iterate until no more multiline comments. -1 means the substring wasn't found.
        code = code[:multiline_start_index] + code[code.find("*/") + 1:]  # Slice out comment by concatenating slices.
        multiline_start_index = code.find("/*")  # Find start of next multiline comment.
    return_string = ""
    for line in code.split("\n"):  # Split into lines, since they matter for inline comments.
        comment_start_index = line.find('//')
        if comment_start_index != -1:
            line = line[:comment_start_index].strip()  # Stripped so spaces before comments aren't included.
        return_string += line + "\n"
    return return_string.strip()  # Stripped so the last line of code doesn't have an unnecessary newline.


def find_properties(code, property_types):
    found_properties = {}
    for line in code.splitlines():
        line = line.strip()
        if line[:23] == "public static final int":
            line_parts = line.split(" ")
            try:
                property_type_id = int(line_parts[6][:-1]) & int("0x00FF0000", 16)
                found_properties[line_parts[4]] = property_types[property_type_id]  # Map property name => type.
            except KeyError as k:
                print("Invalid ID " + str(k.args[0]) + " for property \"" + line_parts[4] +
                      "\"! This could be due to faulty input or due to an update to the allowed property types.")
                print(
                    "Property type data was last fetched on 20/3/2024 from "
                    "https://source.android.com/docs/automotive/vhal/property-configuration. It is hard-coded in the "
                    "Python file, on line 131. This text is on line 66.")
                print("The rest of the properties will be handled as per usual.\n")
    print("Properties found!\n")
    return found_properties


def get_differences(old_props, updated_props):
    diff = {}  # Map property name to tuple of (old, new)
    all_prop_names = list(old_props.keys()) + list(updated_props.keys())
    for prop_name in all_prop_names:
        try:
            old_type = old_props[prop_name]
        except KeyError:  # Property not in old version...
            new_type = updated_props[prop_name]
            diff[prop_name] = (None, new_type)  # Must come from new version!
        else:  # Property in old version...
            try:
                new_type = updated_props[prop_name]
            except KeyError:  # Property not in new version...
                old_type = old_props[prop_name]
                diff[prop_name] = (old_type, None)  # Must come from old version!
            else:  # Property in both old & new versions...
                if old_type != new_type:
                    diff[prop_name] = (old_type, new_type)
                else:
                    pass  # Don't add to diff if no difference exists!
    return diff


def make_table(version_diffs):  # Creates a plain-text table (assuming monospace font is used).
    table = ""
    keys = list(version_diffs.keys())
    max_key_len = max(8, *[len(k) for k in keys])  # Ensures right-hand alignment for keys column. len("Property") = 8.
    max_type_len = 9  # Longest type name is "INT32_VEC", "INT64_VEC", OR "FLOAT_VEC", all of which are 9 letters.
    vert_line = " | "
    horiz_line = "\n" + ("_" * (max_key_len + 2 * (max_type_len + len(vert_line)))) + "\n"
    table += (max_key_len - 8) * " " + "Property" + vert_line
    table += "Old" + " " * (max_type_len - 3) + vert_line
    table += "New" + " " * (max_type_len - 3) + horiz_line
    for key in keys:
        old_type = str(version_diffs[key][0])
        new_type = str(version_diffs[key][1])
        table += ((max_key_len - len(key)) * " ") + key + vert_line
        table += old_type + ((max_type_len - len(old_type)) * " ") + vert_line
        table += new_type + ((max_type_len - len(new_type)) * " ") + "\n"
    return table


if __name__ == "__main__":
    valid_input = False
    while not valid_input:
        try:
            old_fp = input("Previous version's code (file path): ")
            new_fp = input("Updated version's code (file path): ")
            export_fp = "python_property_diff_util_output.txt"
            old_f = open(old_fp, "r")
            new_f = open(new_fp, "r")
            res_f = open(export_fp, "w")
        except FileNotFoundError as file_error:
            print(f"File \"{file_error.filename}\" does not exist! Try again.")
            print()  # newline
        else:
            valid_input = True
    print()  # newline

    property_types = {"0x00100000": "STRING",
                      "0x00200000": "BOOLEAN",
                      "0x00400000": "INT32",
                      "0x00410000": "INT32_VEC",
                      "0x00500000": "INT64",
                      "0x00510000": "INT64_VEC",
                      "0x00600000": "FLOAT",
                      "0x00610000": "FLOAT_VEC",
                      "0x00700000": "BYTES",
                      "0x00e00000": "MIXED"}
    property_types = {int(key, 16): value for (key, value) in property_types.items()}

    print(f"Finding properties in {old_fp}.\n")
    old_p = find_properties(remove_code_comments(old_f.read()), property_types)
    old_f.close()

    print(f"Finding properties in {new_fp}.\n")
    new_p = find_properties(remove_code_comments(new_f.read()), property_types)
    new_f.close()
    print("Compiling differences...\n\n")
    differences = get_differences(old_p, new_p)
    if differences:
        output = make_table(differences)
    else:
        output = "No changes!"
    res_f.write(output)
    res_f.close()
    print(output)
    print(f"Output saved to {export_fp}\n")
