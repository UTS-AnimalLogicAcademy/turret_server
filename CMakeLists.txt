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

