#!/bin/bash
nbdev_build_lib
nbdev_build_test
python remove_test_folders.py
if [ -z $1 ]; then
    echo "pdb at end"
    pytest --pdb --last-failed tests -v  --show-capture=no
else
    if [ $1 = "end" ]; then
        echo "pdb at end"
        pytest --pdb --last-failed tests -v  --show-capture=no
    else
        echo "pdb at beginning"
        pytest --trace --last-failed tests -v  --show-capture=no
    fi
fi
