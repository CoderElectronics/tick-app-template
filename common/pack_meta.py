import argparse #[cite: 2]
import struct #[cite: 2]
import sys #[cite: 2]
import os #[cite: 2]
import json #[cite: 2]

def main(): #[cite: 2]
    parser = argparse.ArgumentParser(description="Prepend a C-struct metadata header to a Mirror OS bin from a package.json file.") #[cite: 2]

    parser.add_argument("input", help="Path to the raw input .bin file") #[cite: 2]
    parser.add_argument("-m", "--manifest", required=True, help="Path to the package.json file") #[cite: 2]
    parser.add_argument("-o", "--output", help="Path to the output .bin file (defaults to <input>_meta.bin)") #[cite: 2]
    parser.add_argument("--magic", type=lambda x: int(x, 0), default=0x324D5655, help="Magic number in hex (e.g., 0x324D5655) or int") #[cite: 2]

    args = parser.parse_args() #[cite: 2]

    if not os.path.exists(args.input): #[cite: 2]
        print(f"Error: Input file '{args.input}' not found.") #[cite: 2]
        sys.exit(1) #[cite: 2]

    if not os.path.exists(args.manifest): #[cite: 2]
        print(f"Error: Manifest file '{args.manifest}' not found.") #[cite: 2]
        sys.exit(1) #[cite: 2]

    with open(args.manifest, 'r') as f: #[cite: 2]
        try: #[cite: 2]
            manifest = json.load(f) #[cite: 2]
        except json.JSONDecodeError as e: #[cite: 2]
            print(f"Error parsing JSON in {args.manifest}: {e}") #[cite: 2]
            sys.exit(1) #[cite: 2]

    name = manifest.get("name", "App") #[cite: 2]

    author = str(manifest.get("author", "NA")) #[cite: 2]

    version_field = manifest.get("version", 1) #[cite: 2]
    try: #[cite: 2]
        if isinstance(version_field, str): #[cite: 2]
            version = int(version_field.split('.')[0]) #[cite: 2]
        else: #[cite: 2]
            version = int(version_field) #[cite: 2]
    except ValueError: #[cite: 2]
        print(f"Warning: Could not parse version '{version_field}' into an integer. Defaulting to 1.") #[cite: 2]
        version = 1 #[cite: 2]

    # Extract the icon grid (default to a blank 12x12 square if missing)
    default_grid = ["." * 12] * 12
    icon_grid = manifest.get("icon_grid", default_grid)

    # Flatten the 12 strings into a single string of 144 '0's and '1's
    bit_string = ""
    for row in icon_grid:
        # Pad or truncate row to exactly 12 characters to prevent misalignments
        row = row.ljust(12, '.')[:12]
        for char in row:
            bit_string += '1' if char != '.' else '0'

    # Chunk the 144 bits into 18 integer bytes
    icon_bytes = bytearray()
    for i in range(0, 144, 8):
        byte_str = bit_string[i:i+8]
        icon_bytes.append(int(byte_str, 2))

    if args.output: #[cite: 2]
        output_path = args.output #[cite: 2]
    else: #[cite: 2]
        name_root, ext = os.path.splitext(args.input) #[cite: 2]
        output_path = f"{name_root}_meta{ext}" #[cite: 2]

    name_bytes = name[:15].encode('utf-8') #[cite: 2]
    author_bytes = author[:15].encode('utf-8') #[cite: 2]

    try: #[cite: 2]
        # '<'   : Little-endian
        # 'I'   : uint32 (4 bytes) - magic
        # 'H'   : uint16 (2 bytes) - version
        # '18s' : 18-byte char array - icon bitmap
        # '16s' : 16-byte char array - name
        # '16s' : 16-byte char array - author
        header = struct.pack('<I H 18s 16s 16s', args.magic, version, bytes(icon_bytes), name_bytes, author_bytes)
    except struct.error as e: #[cite: 2]
        print(f"Error packing header: {e}") #[cite: 2]
        sys.exit(1) #[cite: 2]

    with open(args.input, 'rb') as f: #[cite: 2]
        payload = f.read() #[cite: 2]

    with open(output_path, 'wb') as f: #[cite: 2]
        f.write(header + payload) #[cite: 2]

    print(f"packed {len(payload)} bytes of payload with metadata.") #[cite: 2]
    print(f"  name:    {name[:15]}") #[cite: 2]
    print(f"  author:  {author[:15]}") #[cite: 2]
    print(f"  version: {version}") #[cite: 2]
    print(f"\nsaved to: {output_path}") #[cite: 2]

if __name__ == "__main__": #[cite: 2]
    main() #[cite: 2]
