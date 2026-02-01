from setuptools import setup, find_packages

setup(
    name="linux-monitor",
    version="1.0.0",
    author="Anthony Navarro",
    description="A concurrent SSH-based infrastructure monitor with a Textual TUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/anavarrolinux/linux-monitor",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "paramiko>=3.0.0",
        "pyyaml>=6.0",
        "textual>=0.40.0",
    ],
    entry_points={
        "console_scripts": [
            "lm-collect=collect:main",
            "lm-monitor=monitor_tui:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9", # Aligned with Rocky Linux 9 defaults
)
