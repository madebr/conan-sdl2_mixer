import os
import shutil

from conans import ConanFile, CMake, tools


class Sdl2mixerTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["sine.wav"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        shutil.copy(os.path.join(self.source_folder, "sine.wav"),
                    os.path.join(self.build_folder, "bin", "sine.wav"))

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")

    def test(self):
        pass
        # docker has no soundcard
        # if not tools.cross_building(self.settings):
        #     os.chdir("bin")
        #     self.run(".%sexample" % os.sep)
