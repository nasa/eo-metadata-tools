#!/bin/bash

# This is a script to document the commands used to run all the code life cycle
#   stages of the code. These include lint, test, package, install, uninstall,
#   document, and clean.

# Print out a usage manual
help()
{
    echo 'Run all the code stages: lint, test, document, package, install, uninstall, and clean'
    echo
    echo 'Usage:'
    echo '    ./runme.sh -[cfhlpt] -[i | u]'
    echo '    ./runme.sh'
    echo '        same as ./runme.sh -l -t      #list, test'
    echo '    ./runme.sh -l -t -p -i            #lint, test, package, install'
    echo

    format='%4s %-10s - %-30s\n'
    printf "${format}" Flag Name Description
    printf "${format}" ---- ---------- ------------------------------
    printf "${format}" '-c' 'clean' 'Clean up all generated files and directories'
    printf "${format}" '-d' 'document' 'Generate documentation files'
    printf "${format}" '-f' 'find' 'Find the package in pip3'
    printf "${format}" '-h' 'help' 'Print out this help message and then exit'
    printf "${format}" '-i' 'install' 'Install latest wheel file'
    printf "${format}" '-u' 'uninstall' 'Uninstall the wheel file'
    printf "${format}" '-l' 'lint' 'Print out this help message'
    printf "${format}" '-p' 'package' 'Package project into a whl file'
    printf "${format}" '-r' 'report' 'Doc-It tag report'
    printf "${format}" '-t' 'unit test' 'Run the unit tests'
}

# Check the syntax of the code for PIP8 violations
lint()
{
    printf '*****************************************************************\n'
    printf 'Run pylint to check for common code convention warnings\n'
    pylint cmr test demos \
        --disable=duplicate-code \
        --ignore-patterns=".*\.md,.*\.sh,.*\.html,pylintrc,LICENSE,build,dist,tags,eo_metadata_tools_cmr.egg-info"
}

# Run all the Unit Tests
unit_test()
{
    printf '*****************************************************************\n'
    printf 'Run the unit tests for all subdirectories\n'
    pip3 install coverage
    coverage run -m unittest discover
    coverage html
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
    printf 'Remove generated files and directories\n'
    rm -rf build
    rm -rf dist
    rm -rf htmlcov
    rm -rf eo_metadata_tools_cmr.egg-info
    find cmr -type d -name '__pycache__' | xargs rm -rf
}

document_markdown()
{
    printf '*****************************************************************\n'
    printf 'Generate the markdown documentation\n'

    module=cmr
    
    if [ -z "$(which pydoc-markdown)" ] ; then
        pip3 install pydoc-markdown
    fi
    pydoc-markdown
}

config_report()
{
    #grep -ri 'Document-it' cmr | sed -e 's/.*Document-it \({.*}\)/\1/g' | jq -c
    python3 docit.py > doc/config_properties.md
}

# Process the command line arguments
while getopts "cdfhilprtu" opt
do
    case ${opt} in
        c) clean ;;
        d) document_markdown ;;
        f) find_package ;;
        h) help ;;
        i) install_package ;;
        l) lint ;;
        p) package_project ;;
        r) config_report ;;
        t) unit_test ;;
        u) uninstall_package ;;
        *) help ; exit ;;
    esac
done

# default, no options given, run these tasks
if [[ $# -eq 0 ]] ; then
    lint
    unit_test
fi
