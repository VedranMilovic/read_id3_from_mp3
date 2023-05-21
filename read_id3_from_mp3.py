from id3_types import id3_field_encodings, apic_picture_types, frame_types
from os import path, SEEK_CUR
from typing import BinaryIO

filename = "Someday.mp3"

def decode_size(encoded_size: bytes) -> int:
    return encoded_size[0] << 21 \
           | encoded_size[1] << 14 \
           | encoded_size[2] << 7 \
           | encoded_size[3]


def read_c_string(binary_file: BinaryIO, c_string_encoding: str) -> str:
    byte_array = bytearray()
    byte_read = binary_file.read(1)
    while byte_read and byte_read != b'\x00':
        byte_array += byte_read
        byte_read = binary_file.read(1)
    if byte_array != b'\x00':
        return byte_array.decode(c_string_encoding)
    else:
        return ""


with open(filename, "rb") as mp3_file:
    header = mp3_file.read(10)
    if header[:5] == b'ID3\x03\x00':
        print(f"Flags: {header[5]:#010b}")
        size_bytes = header[-4:]
        size = decode_size(size_bytes)
        print(f"Tag size: {size} bytes")
        if header[5] & 0b010000:
            ext_size = decode_size(mp3_file.read(4))
            print(f"Extended header, size is {ext_size} bytes")
            mp3.seek(ext_size, SEEK_CUR)
        while True:
            print("*" * 80)
            print(f"Current position: {mp3_file.tell()}")
            frame_header = mp3_file.read(10)
            frame_id = frame_header[:4]
            if frame_id in frame_types:
                print(f"Found frame {frame_id}")
                frame_size = int.from_bytes(frame_header[4:8], "big")
                print(f"Frame size: {frame_size}")

                if frame_id.startswith(b'T'):
                    encoding_byte = mp3_file.read(1)[0]
                    encoding = id3_field_encodings[encoding_byte]
                    print(f"Encoding is {encoding}")
                    text = mp3_file.read(frame_size - 1).decode(encoding)
                    print(f"{frame_types[frame_id]}: {text}")

                elif frame_id.startswith(b'WXXX'):
                    encoding_byte = mp3_file.read(1)[0]
                    encoding = id3_field_encodings[encoding_byte]
                    print(f"Encoding is {encoding}")
                    description_and_url = mp3_file.read(frame_size -1)
                    parts = description_and_url.split(b'\x00')
                    description = parts[0].decode(encoding)
                    url = parts[-1].decode("iso-8859-1")
                    print(f"{frame_types[frame_id]}:")
                    print(f"\tDescription: {description}:")
                    print(f"\tURL: {url}:")

                elif frame_id.startswith(b'APIC'):
                    frame_data_start = mp3_file.tell()
                    print(f'APIC frame starts at {frame_data_start}')
                    encoding_byte = mp3_file.read(1)[0]
                    encoding = id3_field_encodings[encoding_byte]
                    print(f"APIc encoding is {encoding}")
                    mime_type = read_c_string(mp3_file, "iso-8859-1")
                    if mime_type == "":
                        mime_type = "image/"
                        print(f"Mime Type: {mime_type}")

                    picture_type = int.from_bytes(mp3_file.read(1), "big")
                    apic_picture_name = apic_picture_types[picture_type]
                    print(f"Found {apic_picture_name}")

                    description = read_c_string(mp3_file, encoding)
                    print(f"Image description: {description}")
                    if mime_type.startswith("image/"):
                        image_data_start = mp3_file.tell()
                        print(f"Image starts at {image_data_start}")
                        image_size = frame_size - (image_data_start - frame_data_start)
                        print(f"Frame size is: {image_size}")
                        image_data = mp3_file.read(image_size)

                        image_file = mime_type.split("/")[-1]
                        base_filename = path.split(filename)[1]
                        base_filename = path.splitext(base_filename)[0]
                        picture_filename = f"{base_filename} {apic_picture_name}.{image_file}"
                        print(f"Writing image file: {picture_filename}")
                        with open(picture_filename, "wb") as output_file:
                            output_file.write(image_data)

                else:
                    mp3_file.seek(frame_size, SEEK_CUR)
                    next_byte = mp3_file.read(1)
                    while next_byte and next_byte == b'\0':
                        next_byte = mp3_file.read(1)
                    if next_byte == b'':
                        mp3_file.seek(-1, SEEK_CUR)
                print(f'seek position after frame: {mp3_file.tell()}')
            else:
                break
























































