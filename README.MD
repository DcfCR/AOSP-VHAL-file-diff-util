# Python Util for Finding Differences in AOSP VHAL Property Types.
This is a short Python script for finding the differences in property types between versions of a file. Property type data from [the Android Open Source Documentation](https://source.android.com/docs/automotive/vhal/property-configuration).

## Usage

The script can be run from a command prompt. It prompts the user for two file paths, one for the old version of the file, and one for the updated file. It displays the result in a plain-text table, which is also exported to a text file, with the unwieldy name ```python_property_diff_util_output.txt```.

Here is an example of expected behavior:
```
C:\example_path>  py python

Previous version's code (file path): file_v1.kt
Updated version's code (file path): file_v2.kt

Finding properties in placeholder.txt...
Properties found!

Finding properties in placeholder2.txt...
Properties found!

Compiling differences...

               Property | Old       | New
_______________________________________________
FRONT_FOG_LIGHTS_SWITCH | INT32     | INT64
       EV_CHARGE_SWITCH | BOOLEAN   | None
            CAR_CRASHED | None      | BOOLEAN

Output saved to python_property_diff_util_output.txt

C:\example_path>  ...
```
## License

[MIT](https://choosealicense.com/licenses/mit/)