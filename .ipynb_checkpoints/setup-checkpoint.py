import setuptools
from denverapi import pysetup

with open("README.md") as file:
    long_description = file.read()

requirements = ["denver-api", "PiOS", "packaging", "toml"]

setuptools.setup(
    name="PiOS-SDK",
    version="0.5.0",
    packages=setuptools.find_packages()
    + setuptools.find_namespace_packages(include=["pios_sdk.*", "pios_sdk"]),
    package_data=pysetup.find_package_data("pios_sdk", "pios_sdk"),
    url="https://github.com/xcodz-dot/PiOS-SDK",
    license="MIT License",
    author="xcodz",
    author_email="",
    description="PiOS, A full featured python written OS [SDK]",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=[
        "PiOS",
        "python",
        "os",
        "github",
        "pyos",
        "operating",
        "system",
        "PiOS-SDK",
        "sdk",
    ],
    entry_points={
        "console_scripts": [
            "pios-sdk-ppk = pios_sdk.ppk:main",
            "pios-sdk-app = pios_sdk.app:main",
            "ark = pios_sdk.ark:main",
        ]
    },
)
