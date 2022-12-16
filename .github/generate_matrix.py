import dataclasses
import json


def main():
    configs = build_configs()
    output(configs)


def output(configs):
    matrix = {"include": [config.to_dict() for config in configs]}
    print(json.dumps(matrix))


MANYLINUX_CONTAINERS = [
    "quay.io/pypa/manylinux2014_x86_64",
    "quay.io/pypa/manylinux_2_28_x86_64",
]


@dataclasses.dataclass
class BuildConfig:
    os: str = "ubuntu-latest"
    container: str = ""
    rust_toolchain: str = "stable"

    def __post_init__(self):
        if self.os == "ubuntu-latest" and not self.container:
            self.container = MANYLINUX_CONTAINERS[0]

    def to_dict(self):
        return {key: str(value).replace("_", "-") for key, value in self.__dict__}


def build_configs():
    for container in MANYLINUX_CONTAINERS:
        yield BuildConfig(os="ubuntu-latest", container=container)

    for os in ["windows-latest", "macos-latest"]:
        yield BuildConfig(os=os)

    for rust_toolchain in ["beta", "nightly"]:
        yield BuildConfig(rust_toolchain=rust_toolchain)


if __name__ == "__main__":
    main()
