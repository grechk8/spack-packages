# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
from datetime import datetime

from spack_repo.builtin.build_systems.cmake import CMakePackage


from spack.package import *


class Opencarp(CMakePackage):
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
    variant("mpi", default=True, description="Enable MPI support")
    variant("openmp", default=True, description="Enable OpenMP support")
    variant("ginkgo", default=False, description="Build with Ginkgo linear solvers")
    variant("cuda", default=False, description="Enable CUDA support")

    variant(
        "cuda_arch",
        default="none",
        values=("none", "70", "75", "80", "86", "89", "90"),
        multi=True,
        description="CUDA architectures for CMAKE_CUDA_ARCHITECTURES",
        when="+cuda",
    )




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

    depends_on("mpi", when="+mpi")


    # Ginkgo is optional
    depends_on("rapidjson", when="+ginkgo", type="build")

    # Base requirement: allow multiple Ginkgo versions (1.5, 1.6, ..., develop)
    depends_on("ginkgo@1.5:", when="+ginkgo")

    # sde variant exists only for newer Ginkgo versions (>=1.7)
    depends_on("ginkgo~sde", when="+ginkgo ^ginkgo@1.7:")

    # Mirror opencarp features onto ginkgo (force overlay namespace)
    depends_on("ginkgo+mpi",    when="+ginkgo+mpi")
    depends_on("ginkgo~mpi",    when="+ginkgo~mpi")

    depends_on("ginkgo+openmp", when="+ginkgo+openmp")
    depends_on("ginkgo~openmp", when="+ginkgo~openmp")

    depends_on("ginkgo+cuda",   when="+ginkgo+cuda")
    depends_on("ginkgo~cuda",   when="+ginkgo~cuda")

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


    def _cuda_arch_str(self):
        if "cuda_arch" not in self.spec.variants:
            return None
        archs = self.spec.variants["cuda_arch"].value
        if not archs or archs == ("none",) or archs == "none":
            return None
        if isinstance(archs, str):
            return archs
        return ";".join(archs)


    def _ginkgo_cmake_dir(self):
        prefix = self.spec["ginkgo"].prefix
        candidates = [
            join_path(prefix, "lib", "cmake", "Ginkgo"),
            join_path(prefix, "lib64", "cmake", "Ginkgo"),
        ]
        for d in candidates:
            if os.path.isdir(d):
                return d
        return str(prefix)

    def setup_build_environment(self, env):
        if "+ginkgo" in self.spec:
            env.prepend_path("CPATH", self.spec["rapidjson"].prefix.include)


    def cmake_args(self):
        spec = self.spec
        args = [
            self.define("DLOPEN", True),
            self.define("SPACK_BUILD", True),

            self.define("BUILD_EXTERNAL", False),
            self.define("ENABLE_MPI", "+mpi" in spec),
            self.define("USE_OPENMP", "+openmp" in spec),
            self.define("USE_CUDA", "+cuda" in spec),
        ]


        if "+mpi" in spec:
            args += [
                self.define("MPI_C_COMPILER", spec["mpi"].mpicc),
                self.define("MPI_CXX_COMPILER", spec["mpi"].mpicxx),
                self.define("MPIEXEC_EXECUTABLE", join_path(spec["mpi"].prefix.bin, "mpiexec")),

            ]

        if "+ginkgo" in spec:
            args += [
                self.define("ENABLE_GINKGO", True),
                self.define("CARP_USE_GINKGO", True),
                self.define("GINKGO_DIR", spec["ginkgo"].prefix),
                self.define("Ginkgo_DIR", self._ginkgo_cmake_dir()),
                # self.define("CMAKE_PREFIX_PATH", spec["ginkgo"].prefix),
            ]
        else:
            args += [
                self.define("ENABLE_GINKGO", False),
                self.define("CARP_USE_GINKGO", False),
            ]


        # CUDA
        if "+cuda" in spec:
            args += [
                self.define("CUDAToolkit_ROOT", spec["cuda"].prefix),
                self.define("CMAKE_CUDA_STANDARD", 17),
            ]

            arch_str = self._cuda_arch_str()
            if arch_str:
                args.append(self.define("CMAKE_CUDA_ARCHITECTURES", arch_str))
                # flags custom :
                args.append(self.define("CUDA_GPU_ARCH", "sm_%s" % arch_str.split(";")[0]))
                args.append(self.define("CUDA_ENABLE_RDC", True))
                args.append(self.define(
                    "CMAKE_CUDA_FLAGS",
                    "--cuda-gpu-arch=sm_%s --no-cuda-version-check" % arch_str.split(";")[0],
                ))

        return args


    def _build_suffix(self):
        """Return a deterministic build suffix like:
        ginkgo_cpu_mpi, ginkgo_cpu_mpi_omp, ginkgo_cuda_mpi_omp, etc.
        """
        spec = self.spec
        parts = []

        # solver
        parts.append("ginkgo" if "+ginkgo" in spec else "petsc")

        # device
        parts.append("cuda" if "+cuda" in spec else "cpu")

        # parallel
        if "+mpi" in spec:
            parts.append("mpi")
        if "+openmp" in spec:
            parts.append("omp")

        return "_".join(parts)

    @property
    def build_directory(self):
        # This is the directory created inside the stage/source tree
        return "build_" + self._build_suffix()


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
            flavor = self._build_suffix().replace("_", "-")  # ie: ginkgo-cpu-mpi-omp
            cusettings(settings_file, "--flavor", flavor, "--software-root", str(self.prefix))
