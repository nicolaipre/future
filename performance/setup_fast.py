from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define the Cython extension
extensions = [
    Extension(
        "future.fast_router",
        ["future/fast_router.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-march=native"],
        extra_link_args=["-O3"]
    )
]

setup(
    name="future-fast-router",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
        'cdivision': True,
    }),
    zip_safe=False,
) 