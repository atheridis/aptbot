import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aptbot",
    version="0.0.1",
    author="Georgios Atheridis",
    author_email="atheridis@tutamail.com",
    description="A chatbot for twitch.tv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atheridis/aptbot",
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'aptbot=aptbot.__main__:main',
        ],
    },
    install_requires=[
        'dotenv',
    ],
    python_requires=">=3.7",
)
