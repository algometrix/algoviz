import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='algoviz',  # How you named your package folder (MyLib)
    packages=['algoviz'],  # Chose the same as "name"
    version='0.1.7',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Generates visualizations for arrays',  # Give a short description about your library
    author='Ashish Nagar',  # Type in your name
    author_email='ashishnagar31@gmail.com',  # Type in your E-Mail
    url='https://github.com/algometrix/algoviz',  # Provide either the link to your github or to your website
    download_url='https://github.com/algometrix/algoviz/archive/v_0.2.1.tar.gz',  # I explain this later on
    keywords=['Visualization', 'Algorithms'],  # Keywords that define your package best
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[  # I get to this in a second
        'rich',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
