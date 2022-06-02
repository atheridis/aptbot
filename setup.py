import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aptbot",
    version="0.2.1",
    author="Georgios Atheridis",
    author_email="atheridis@tutamail.com",
    description="A chatbot for twitch.tv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atheridis/aptbot",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    packages=setuptools.find_packages(),
    package_data={"aptbot": ["resources/main.py"]},
    entry_points={
        "console_scripts": [
            "aptbot=aptbot.main:main",
        ],
    },
    install_requires=[
        "python-dotenv",
        "urllib3",
    ],
    python_requires=">=3.7",
)
