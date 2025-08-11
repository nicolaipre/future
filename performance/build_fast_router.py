#!/usr/bin/env python3
"""
Build script for Future's fast router Cython extension.
"""

import os
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

def build_fast_router():
    """Build the fast router Cython extension."""
    
    # Check if Cython is available
    try:
        import Cython
    except ImportError:
        print("Cython not found. Installing...")
        os.system(f"{sys.executable} -m pip install cython")
    
    # Check if numpy is available
    try:
        import numpy
    except ImportError:
        print("NumPy not found. Installing...")
        os.system(f"{sys.executable} -m pip install numpy")
    
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
    
    # Build the extension
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

if __name__ == "__main__":
    build_fast_router() 