#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class SDL2Conan(ConanFile):
    name = "sdl2_mixer"
    version = "2.0.4"
    description = "SDL_mixer is a sample multi-channel audio mixer library."
    topics = ("conan", "sdl2", "audio", "mixer")
    url = "https://github.com/bincrafters/conan-sdl2_mixer"
    homepage = "https://www.libsdl.org/projects/SDL_mixer/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Zlib"
    exports = ["LICENSE.md"]
    _source_subfolder = "sources"
    _build_subfolder = "build"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def sdl2_mixer_build_folder(self):
        build_dir = os.path.join(self.build_folder, self._build_subfolder)
        try:
            os.mkdir(build_dir)
        except IOError:
            pass
        return build_dir

    @property
    def sdl2_version(self):
        return "2.0.9"

    def requirements(self):
        self.requires.add("sdl2/{}@bincrafters/stable".format(self.sdl2_version))

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def source(self):
        source_url = "https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-%s.tar.gz" % self.version
        tools.get(source_url, sha256="b4cf5a382c061cd75081cf246c2aa2f9df8db04bdda8dcdc6b6cca55bede2419")
        extracted_dir = "SDL2_mixer-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "build-scripts", "config.sub"),
                              "case $os in\n",
                              "case $os in\n"
                              "\t-msvc*)\n"
                              "\t\tos=-windows\n"
                              "\t\t;;\n")

    def build(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings, filter_known_paths=False):
                self.build_autotools()
        else:
            self.build_autotools()

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler in ("gcc", "clang"):
            autotools.libs.append("dl")
        config_args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
            "--enable-sdltest" if tools.get_env("CONAN_RUN_TESTS", False) else "--disable-sdltest",
            # "--with-sdl-prefix={}".format(self.deps_cpp_info["sdl2"].rootpath),
            # "--with-sdl-exec-prefix={}".format(self.deps_cpp_info["sdl2"].rootpath),
        ]
        if self.settings.compiler != "Visual Studio":
            config_args.append("--with-pic" if self.options.fPIC else "--without-pic")

        with tools.chdir(self.sdl2_mixer_build_folder):
            cflags = " ".join("-I{}".format(l) for l in self.deps_cpp_info["sdl2"].includedirs) \
                     + " ".join(self.deps_cpp_info["sdl2"].cflags)
            with tools.environment_append({
                "SDL_CFLAGS": cflags,
                "SDL_LIBS": " ".join("-l{}".format(l) for l in self.deps_cpp_info["sdl2"].libs),
                "SDL_VERSION": self.sdl2_version,
            }):
                self.output.warn("SDL_CFLAGS: {}".format(cflags))
                autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=config_args)
        return autotools

    def build_autotools(self):
        autotools = self._configure_autotools()
        with tools.chdir(self.sdl2_mixer_build_folder):
            autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        with tools.chdir(self.sdl2_mixer_build_folder):
            autotools.install()
        self.copy(pattern="COPYING.txt", dst="license", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.pdb", dst="lib", src=".")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
