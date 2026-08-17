# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the FreeCAD project.

#--------------------------------------------------------------------------
#   Copyright (c) 2026 Werner Mayer <werner.wm.mayer@gmx.de>                *
#                                                                         *
#   This file is part of the FreeCAD CAx development system.              *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU Library General Public License (LGPL)   *
#   as published by the Free Software Foundation; either version 2 of     *
#   the License, or (at your option) any later version.                   *
#   for detail see the LICENCE text file.                                 *
#   for detail see the LICENCE text file.                                 *
#   FreeCAD is distributed in the hope that it will be useful,            *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU Library General Public License for more details.                  *
#                                                                         *
#   You should have received a copy of the GNU Library General Public     *
#   License along with FreeCAD; if not, write to the Free Software        *
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#   USA                                                                   *
#--------------------------------------------------------------------------

macro(SetupCoverage)
    option(FREECAD_ENABLE_COVERAGE "Enable C++ compiler flags for test coverage" OFF)

    if(FREECAD_ENABLE_COVERAGE)
        if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_COMPILER_IS_CLANGXX)
            message(STATUS "Building with C++ test coverage support (--coverage)")
            # Add compile options for coverage
            add_compile_options(--coverage)
            # Add link options for coverage
            add_link_options(--coverage)
        else()
            message(WARNING "Coverage flags are only supported on GCC or Clang compiler toolchains.")
        endif()
    endif()
endmacro()
