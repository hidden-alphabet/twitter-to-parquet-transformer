import setuptools

setuptools.setup(
    name='twitter-to-parquet-transformer',
    version='0.0.0',
    author=["Cole Hudson", "Chris Louie"],
    author_email="cole@colejhudson.com",
    description="AWS Lambda function to parse HTML into Parquet",
    install_requires=[
        "bs4",
        "s3fs",
        "pyarrow"
    ],
    packages=setuptools.find_packages()
)
