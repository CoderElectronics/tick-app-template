import argparse
import struct
import sys
import os
import json

def main():
    parser = argparse.ArgumentParser(description="Prepend a C-struct metadata header to a Mirror OS bin from a package.json file.")

    parser.add_argument("input", help="Path to the raw input .bin file")
    parser.add_argument("-m", "--manifest", required=True, help="Path to the package.json file")
    parser.add_argument("-o", "--output", help="Path to the output .bin file (defaults to <input>_meta.bin)")
    parser.add_argument("--magic", type=lambda x: int(x, 0), default=0x324D5655, help="Magic number in hex (e.g., 0x324D5655) or int")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    if not os.path.exists(args.manifest):
        print(f"Error: Manifest file '{args.manifest}' not found.")
        sys.exit(1)

    with open(args.manifest, 'r') as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {args.manifest}: {e}")
            sys.exit(1)

    name = manifest.get("name", "App")

    author = str(manifest.get("author", "NA"))

    version_field = manifest.get("version", 1)
    try:
        if isinstance(version_field, str):
            version = int(version_field.split('.')[0])
        else:
            version = int(version_field)
    except ValueError:
        print(f"Warning: Could not parse version '{version_field}' into an integer. Defaulting to 1.")
        version = 1

    if args.output:
        output_path = args.output
    else:
        name_root, ext = os.path.splitext(args.input)
        output_path = f"{name_root}_meta{ext}"

    name_bytes = name[:15].encode('utf-8')
    author_bytes = author[:15].encode('utf-8')

    try:
        # '<'   : Little-endian
        # 'I'   : uint32 (4 bytes) - magic
        # 'H'   : uint16 (2 bytes) - version
        # '16s' : 16-byte char array - name
        # '16s' : 16-byte char array - author
        header = struct.pack('<I H 16s 16s', args.magic, version, name_bytes, author_bytes)
    except struct.error as e:
        print(f"Error packing header: {e}")
        sys.exit(1)

    with open(args.input, 'rb') as f:
        payload = f.read()

    with open(output_path, 'wb') as f:
        f.write(header + payload)

    print(f"packed {len(payload)} bytes of payload with metadata.")
    print(f"  name:    {name[:15]}")
    print(f"  author:  {author[:15]}")
    print(f"  version: {version}")
    print(f"\nsaved to: {output_path}")

if __name__ == "__main__":
    main()
