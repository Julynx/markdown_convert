import setuptools

with open('README.md', 'r', encoding='utf-8') as markdown_file:
    readme_contents = markdown_file.read()

setuptools.setup(
    name='markdown_convert',
    version='0.9.0',
    author='Julio Cabria',
    author_email='juliocabria@tutanota.com',
    maintainer='Julio Cabria',
    maintainer_email='juliocabria@tutanota.com',
    url='https://github.com/Julynx/markdown_convert',
    description='Extract one or multiple substrings between two start and end strings.',
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    license='GPLv2',
    packages=['markdown_convert'])
