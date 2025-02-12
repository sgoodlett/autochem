""" Install automol
"""
from distutils.core import setup


setup(name='automol',
      version='0.5.4',
      packages=['automol',
                'automol.convert',
                'automol.create',
                'automol.embed',
                'automol.etrans',
                'automol.formula',
                'automol.geom',
                'automol.graph',
                'automol.mult',
                'automol.pot',
                'automol.prop',
                'automol.reac',
                'automol.rotor',
                'automol.zmat',
                'automol.util',
                'automol.util.dict_',
                'phydat',
                'transformations'],
      package_dir={'automol': 'automol',
                   'phydat': 'phydat',
                   'transformations': 'transformations'},
      package_data={'automol': ['tests/data/*.txt',
                                'tests/data/*.csv',
                                'tests/data/*.quartic',
                                'tests/data/*.cubic']})
