import setuptools

setuptools.setup(
    name='hidden-alphabet-transformers-twitter',
    version='0.0.0',
    author=["Cole Hudson", "Chris Louie"],
    author_email="cole@colejhudson.com",
    description="AWS Lambda function to parse HTML from twitter.com/search into Parquet",
    install_requires=[
        "bs4",
        "s3fs",
        "pyarrow"
    ],
    packages=setuptools.find_packages()
)
