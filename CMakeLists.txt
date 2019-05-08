cmake_minimum_required(VERSION 2.6)

include(RezBuild)

file(GLOB_RECURSE bin_files "bin/*")
rez_install_files(
    ${bin_files}
    DESTINATION .
    EXECUTABLE
    LOCAL_SYMLINK
)


file(GLOB_RECURSE bin_files "src/*")
rez_install_files(
    ${bin_files}
    DESTINATION .
    EXECUTABLE
    LOCAL_SYMLINK
)

file(GLOB_RECURSE bin_files "tests/*")
rez_install_files(
    ${bin_files}
    DESTINATION .
    EXECUTABLE
    LOCAL_SYMLINK
)
