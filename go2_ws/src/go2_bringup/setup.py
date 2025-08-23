from setuptools import setup

package_name = 'go2_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/full_sim.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Patrick',
    maintainer_email='patrick.pavlovic@stud.uni-due.de',
    description='Bringup package for Unitree Go2 simulation with DimOS',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={},
)
