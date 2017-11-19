from setuptools import setup, find_packages


def get_requirements():
    """Build the requirements list for this project"""
    requirements_list = []
    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())
    return requirements_list


setup(
    name="anime-enforce",
    version="0.1.0",
    author="Kyraminol Endyeran",
    author_email="kyraminari@gmail.com",
    description="Unofficial API for animeforce.org.",
    keywords="api anime animeforce.org",
    url="https://github.com/kyraminol/anime-enforce",
    packages=find_packages(),
    setup_requires=["setuptools-markdown"],
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=get_requirements(),
)
