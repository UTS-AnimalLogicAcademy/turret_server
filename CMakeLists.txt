cmake_minimum_required(VERSION 2.6)

include(RezBuild)

#FILE(GLOB_RECURSE py_files "python/*.py")
#rez_install_python(
#	py_files
#	FILES
#	${py_files}
#	DESTINATION .
#        EXECUTABLE
#	LOCAL_SYMLINK
#)


file(GLOB_RECURSE py_files "python/*.py")
rez_install_files(
    ${py_files}
    DESTINATION .
    EXECUTABLE
    LOCAL_SYMLINK
)

file(GLOB_RECURSE bin_files "bin/*")
rez_install_files(
    ${bin_files}
    DESTINATION .
    EXECUTABLE
    LOCAL_SYMLINK
)
