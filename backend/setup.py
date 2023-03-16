import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Eclipse",
    version="0.0.1",
    author="Mark Diamantino Caribé",
    author_email="mdcaribe@protonmail.com",
    license="GNU AFFERO GENERAL PUBLIC LICENSE",
    description="A steganography tool based on discrete cosine transform and image augmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdiamantino/eclipse",
    packages=setuptools.find_packages(),
    install_requires=[
        'imageio',
        'cryptography',
        'docopt',
        'pyfiglet',
        'bitstring',
        'opencv_python',
        'imgaug',
        'numpy',
        'PyInquirer',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Topic :: Security",
    ],
    python_requires='>=3.6',
)
