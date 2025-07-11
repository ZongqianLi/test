import os
import zipfile


def load_test_case_io_pairs_from_zip(test_case_zip_path):
  with zipfile.ZipFile(test_case_zip_path, 'r') as zip_ref:
    # List all files and folders inside
    # print("Contents of the zip:")
    # for name in zip_ref.namelist():
        # print(name)
    def _read_by_name(_name):
        with zip_ref.open(_name) as f:
            content = f.read()
            # print(f"Content of {_name}:")
            d = content.decode()
            # print(d)
            return d
    
    def _check_name_pair(name_in, name_out):
        if not name_in.endswith('.in'):
            raise ValueError(f"Expected input file to end with '.in', got: {name_in}")
        if not name_out.endswith('.out'):
            raise ValueError(f"Expected output file to end with '.out', got: {name_out}")
        if not name_in[:-3] == name_out[:-4]:
            raise ValueError(f"Input and output files do not match: {name_in} vs {name_out}")
    

    names = zip_ref.namelist()
    sorted_names = sorted(names)
    # print(sorted_names)
    name_index = 0
    all_io_pairs = []
    while name_index < len(sorted_names):
        name = sorted_names[name_index]
        if name.endswith('/'):
            # It's a directory, skip it
            name_index += 1
            continue
        
        name_in = sorted_names[name_index]
        name_out = sorted_names[name_index + 1] if name_index + 1 < len(sorted_names) else ""
        _check_name_pair(name_in, name_out)
        content_in = _read_by_name(name_in)
        content_out = _read_by_name(name_out)
        all_io_pairs.append((content_in, content_out))
        name_index += 2  # Move to the next pair

    return all_io_pairs


if __name__ == "__main__":
    # Example usage
    test_case_zip_path = "/sgl-workspace/data/test_cases/darkbzoj/2378.zip"
    all_io_pairs = load_test_case_io_pairs_from_zip(test_case_zip_path)
    # This will print the contents of the zip and the content of file.txt
    print("All IO pairs:" + str(all_io_pairs[:1]))