#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, CMake
import os


class VorbisConan(ConanFile):
    name = "vorbis"
    version = "1.3.6"
    description = "The VORBIS audio codec library"
    topics = ("conan", "vorbis", "audio", "codec")
    url = "http://github.com/bincrafters/conan-vorbis"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindVORBIS.cmake"]
    _source_subfolder = "source_subfolder"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    requires = "ogg/1.3.3@bincrafters/stable"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        url = 'https://github.com/xiph/vorbis/archive/v%s.tar.gz' % self.version
        tools.get(url, sha256='43fc4bc34f13da15b8acfa72fd594678e214d1cab35fc51d3a54969a725464eb')
        os.rename("vorbis-%s" % self.version, self._source_subfolder)
        if self.settings.os == 'Windows':
            with tools.chdir(self._source_subfolder):
                tools.replace_in_file('vorbis.pc.in', 'Libs.private: -lm', 'Libs.private:')

    def build(self):
        if self.settings.os == "Linux":
            if 'LDFLAGS' in os.environ:
                os.environ['LDFLAGS'] = os.environ['LDFLAGS'] + ' -lm'
            else:
                os.environ['LDFLAGS'] = '-lm'
        cmake = CMake(self)
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("FindVORBIS.cmake", ".", ".")
        self.copy("include/vorbis/*", ".", "%s" % self._source_subfolder, keep_path=True)
        self.copy("%s/copying*" % self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)
        self.copy('*.pc', src=self._source_subfolder, dst=os.path.join('lib', 'pkgconfig'), keep_path=False)

        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.pdb", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                elif self.settings.os == "Windows":
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):

        self.cpp_info.libs = ['vorbisfile', 'vorbisenc', 'vorbis']

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
