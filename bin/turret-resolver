#! /bin/bash
if [[ $1 = *"tank:"* ]]; then
    python -c "import turret.resolver as r; print r.uri_to_filepath('$1')"
else
    python -c "import turret.resolver as r; print r.filepath_to_uri('$1','tank')"
fi
