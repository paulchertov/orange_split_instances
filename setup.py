from setuptools import setup

setup(name="Split Instances",
      packages=["rowspit_instances"],
      package_data={"rowspit_instances": ["img/*.svg"]},
      classifiers=["Example :: Invalid"],
      entry_points={"orange.widgets": "Data = rowspit_instances"},
      )