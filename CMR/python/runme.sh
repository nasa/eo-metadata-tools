#!/bin/bash

# This is a script to document the commands used to run all the code life cycle
#   stages of the code. These include lint, test, package, install, uninstall,
#   document, and clean.

# Print out a usage manual
help()
{
    echo 'Run all the code life cycle steps: lint, test, package, install, uninstall, and clean'
    echo
    echo 'Usage:'
    echo '    ./runme.sh -[chlpt] -[i | u]'
    echo '    ./runme.sh'
    echo '        same as ./runme.sh -l -t      #list, test'
    echo '    ./runme.sh -l -t -p -i            #lint, test, package, install'
    echo

    format='%4s %-10s - %-30s\n'
    printf "${format}" Flag Name Description
    printf "${format}" ---- ---------- ------------------------------
    printf "${format}" '-c' 'clean' 'Clean up all generated files and directories'
    printf "${format}" '-h' 'help' 'Print out this help message'
    printf "${format}" '-i' 'install' 'Install latest wheel file'
    printf "${format}" '-u' 'uninstall' 'Uninstall the wheel file'
    printf "${format}" '-l' 'lint' 'Print out this help message'
    printf "${format}" '-p' 'package' 'Package project into a whl file'
    printf "${format}" '-t' 'unit test' 'Run the unit tests'
}

# Check the syntax of the code for PIP8 violations
lint()
{
    printf '*****************************************************************\n'
    printf 'Run pylint to check for common code convention warnings\n'
    pylint * \
        --ignore-patterns=".*\.md,.*\.sh,pylintrc,LICENSE,build,dist,eo_metadata_tools_cmr.egg-info"
}

# Run all the Unit Tests
unit_test()
{
    printf '*****************************************************************\n'
    printf 'Run the unit test for all subdirectories\n'
    python3 -m unittest discover
}

# assume that the following has been called:
# python3 -m pip install --user --upgrade setuptools wheel
package_project()
{
    printf '*****************************************************************\n'
    printf 'Run python setup to package the project as a wheel\n'
    python3 setup.py sdist bdist_wheel
}

# lookup library in pip
find_package()
{
    printf '*****************************************************************\n'
    printf 'Find library in pip\n'
    pip3 list eo-metadata-tools-cmr | grep eo-metadata-tools-cmr
}

# call pip to uninstall the library
uninstall_package()
{
    printf '*****************************************************************\n'
    printf 'Uninstall the project from pip\n'
    pip3 uninstall eo-metadata-tools-cmr
}

# Install the newest wheel
install_package()
{
    printf '*****************************************************************\n'
    printf 'Install the project whl file with pip\n'
    newest=$(find dist -name "eo_metadata_tools_cmr-*-py3-none-any.whl" -print \
        | xargs ls -t \
        | head -n 1)
    if [ -a ${newest} ] ; then
        pip3 install ${newest}
    fi
}

# Clean up the directory by removing all generated documents and direcorties
clean()
{
    printf '*****************************************************************\n'
    printf 'Remove all generated files and directories\n'
    rm -rf build
    rm -rf dist
    rm -rf eo_metadata_tools_cmr.egg-info
}

# Process the command line arguments
while getopts "cfhilptu" opt
do
    case ${opt} in
        c) clean ;;
        f) find_package ;;
        h) help ;;
        i) install_package ;;
        l) lint ;;
        p) package_project ;;
        t) unit_test ;;
        u) uninstall_package ;;
        *) help ; exit ;;
    esac
done

# default, no options given, run these tasks
if [[ $# -eq 0 ]] ; then
    lint
    unit_test
    doc_all
fi
