# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
from datetime import datetime

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage

from spack.package import *


class Opencarp(CMakePackage, CudaPackage):
    """The openCARP simulation software,
    an open cardiac electrophysiology simulator for in-silico experiments."""

    homepage = "https://www.opencarp.org"
    git = "https://git.opencarp.org/openCARP/openCARP.git"

    maintainers("MarieHouillon")

    version(
        "18.1",
        commit="6eaa147d18b69a6037d05a90b841e23301048a59",
        submodules=False,
        no_cache=True,
        preferred=True,
    )
    version(
        "18.0", commit="ac4e96792db082958fa9a830341f6e0642cc6bb8", submodules=False, no_cache=True
    )
    version(
        "17.0", commit="537a359d49e976cc9f97042189fb9d3ba4e686c4", submodules=False, no_cache=True
    )
    version(
        "16.0", commit="295055b6a3859709730f62fc8d4fe0e87c4e20b9", submodules=False, no_cache=True
    )
    version(
        "15.0", commit="2271a3cccd7137f1e28c043c10adbd80480f1462", submodules=False, no_cache=True
    )
    version(
        "13.0", commit="e1e0deca7eddcfd210835f54430361c85a97a5a4", submodules=False, no_cache=True
    )
    version(
        "12.0", commit="a34c11af3e8c2afd6e123e586a446c6993e0b039", submodules=False, no_cache=True
    )
    version(
        "11.0", commit="fd8419d5c7649060c9447adf2dbee1723a8af9db", submodules=False, no_cache=True
    )
    version(
        "10.0", commit="7aec7900b3efa6cfe8b27a13fafcb99fd6ff5c8e", submodules=False, no_cache=True
    )
    version(
        "9.0", commit="c01675994df46b8b39c80e001590f9cfaf43cd87", submodules=False, no_cache=True
    )
    version(
        "8.2", commit="dbfd16fdd472375694190b4c7802c0bfba114146", submodules=False, no_cache=True
    )
    version(
        "8.1", commit="28eb2e978f276e7e998719a3f6d436fcb87e482a", submodules=False, no_cache=True
    )
    version(
        "7.0", commit="78da91952738b45760bcbc34610814a83c8c6299", submodules=False, no_cache=True
    )
    version("master", branch="master", submodules=False, no_cache=True)

    variant("carputils", default=False, description="Installs the carputils framework")
    variant("meshtool", default=False, description="Installs the meshtool software")
    variant("openmp", default=True, description="Enable OpenMP support")
    variant("ginkgo", default=False, description="Build with Ginkgo linear solvers")
    variant("cuda", default=False, description="Enable CUDA support")

    conflicts("+cuda", when="~ginkgo", msg="+cuda is supported only with +ginkgo")

    # Patch removing problematic steps in CMake process
    patch("opencarp7.patch", when="@7.0")

    # Patch numerics/ginkgo/SF_ginkgo_solver.cc
    patch("patches/opencarp-ginkgo-iterativebase-namespace.patch", when="@:17.0 +ginkgo ^ginkgo@1.9:")
    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    depends_on("git", type=("build", "run"))
    depends_on("petsc")
    depends_on("petsc@:3.22.5", when="@:17.0")
    depends_on("binutils")
    depends_on("gengetopt")
    depends_on("pkgconfig")
    depends_on("python")
    depends_on("zlib-api")
    depends_on("perl")
    depends_on("mpi")

    # Base requirement: allow multiple Ginkgo versions (1.5, 1.6, ..., develop)
    depends_on("ginkgo@1.5:", when="+ginkgo")

    # Mirror opencarp features onto ginkgo (force overlay namespace)
    depends_on("ginkgo+mpi", when="+ginkgo")

    depends_on("ginkgo+openmp", when="+ginkgo+openmp")
    depends_on("ginkgo~openmp", when="+ginkgo~openmp")

    depends_on("ginkgo+cuda",   when="+ginkgo+cuda")
    depends_on("ginkgo~cuda",   when="+ginkgo~cuda")

    # MPI implementations with CUDA support
    depends_on("openmpi+cuda", when="+cuda ^openmpi")
    depends_on("mpich+cuda", when="+cuda ^mpich")

    # CUDA toolchain
    depends_on("cuda", when="+cuda")


    depends_on("py-carputils", when="+carputils", type=("build", "run"))
    depends_on("meshtool", when="+meshtool", type=("build", "run"))
    # Use specific versions of carputils and meshtool for releases
    for ver in [
        "18.1",
        "18.0",
        "17.0",
        "16.0",
        "15.0",
        "13.0",
        "12.0",
        "11.0",
        "10.0",
        "9.0",
        "8.2",
        "8.1",
        "7.0",
    ]:
        depends_on("py-carputils@oc" + ver, when="@" + ver + " +carputils")
        depends_on("meshtool@oc" + ver, when="@" + ver + " +meshtool")

    def cmake_args(self):
        spec = self.spec
        args = [
            self.define("DLOPEN", True),
            self.define("SPACK_BUILD", True),
            self.define("BUILD_EXTERNAL", False),
            self.define("USE_OPENMP", "UTILS" if "+openmp" in spec else "OFF")
        ]

        if "+ginkgo" in spec:
            args += [
                self.define("ENABLE_GINKGO", True),
            ]

        return args


    @run_after("install")
    def post_install(self):
        # If carputils has been installed, a new settings file
        # with right executable paths is generated
        if "+carputils" in self.spec:
            settings_prefix = os.path.expanduser(join_path("~", ".config", "carputils"))
            settings_file = join_path(settings_prefix, "settings.yaml")
            if os.path.exists(settings_file):
                print("Backup the existing settings.yaml...")
                os.rename(
                    settings_file,
                    join_path(
                        settings_prefix,
                        "settings.yaml." + datetime.today().strftime("%Y-%m-%d-%H:%M:%S"),
                    ),
                )
            cusettings = Executable("cusettings")
            cusettings(settings_file, "--software-root", str(self.prefix))

