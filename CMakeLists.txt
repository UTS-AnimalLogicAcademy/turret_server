cmake_minimum_required(VERSION 2.6)

include(RezBuild)

FILE(GLOB_RECURSE py_files "python/*.py")
rez_install_python(
	py_files
	FILES
	${py_files}
	DESTINATION .
	LOCAL_SYMLINK
)


FILE(GLOB_RECURSE all_files "bin/*")

rez_install_files(
    ${all_files}
    DESTINATION
    .
    LOCAL_SYMLINK
)
