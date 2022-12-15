import json


def main():
    matrix = generate()
    print(json.dumps(matrix))


def generate():
    return {
        "os": [
            "ubuntu-latest",
            "windows-latest",
            "macos-latest",
        ],
        "python-version": [f"3.{minor}" for minor in range(7, 11)],
        "rust-toolchain": ["stable"],
        "include": [
            {
                "os": "ubuntu-latest",
                "python-version": "3.10",
                "rust-toolchain": rust_toolchain,
            }
            for rust_toolchain in ["beta", "nightly"]
        ],
    }


if __name__ == "__main__":
    main()
