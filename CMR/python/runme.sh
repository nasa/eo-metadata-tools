#!/bin/bash

# Assume python3 will be used
python3=python3
pip3=pip3

# This is a script to document the commands used to run all the code life cycle
#   stages of the code. These include lint, test, package, install, uninstall,
#   document, and clean.

# Print out a usage manual
help()
{
    echo 'Run all the code stages: lint, test, document, package, install, uninstall, and clean'
    echo
    echo 'Flags are executed in order and can be called multiple times.'
    echo 'Usage:'
    echo '    ./runme.sh -[cfhlpt] -[i | u]'
    echo '    ./runme.sh'
    echo '        same as ./runme.sh -l -t  #list, test'
    echo '    ./runme.sh -l -t -p -f -i -f  #lint, test, package, find, install, find'
    echo

    format='%4s %-7s %9s : %-30s\n'
    printf "${format}" Flag Value Name Description
    printf "${format}" ---- ------- --------- ----------------------------------
    printf "${format}" '-c' '' 'clean' 'Clean up all generated files and directories'
    printf "${format}" '-C' '' 'coverage' 'Run the code coverage report'
    printf "${format}" '-d' '' 'document' 'Generate documentation files'
    printf "${format}" '-f' '' 'find' "Find the package in $pip3"
    printf "${format}" '-h' '' 'help' 'Print out this help message and then exit'
    printf "${format}" '-H' '' 'coverage' 'Generate the HTML coverage report'
    printf "${format}" '-i' '' 'install' 'Install latest wheel file'
    printf "${format}" '-l' '' 'lint' 'Print out this help message'
    printf "${format}" '-p' '' 'package' 'Package project into a whl file'
    printf "${format}" '-r' '' 'report' 'Doc-It tag report'
    printf "${format}" '-t' '' 'test' 'Run the unit tests'
    printf "${format}" '-u' '' 'uninstall' 'Uninstall the wheel file'
    printf "${format}" '-v' '<value>' 'version' 'Appends a version number to python and pip commands'
}

# Check the syntax of the code for PIP8 violations
lint()
{
    printf '*****************************************************************\n'
    printf 'Run pylint to check for common code convention warnings\n'
    pylint cmr test demos \
        --disable=duplicate-code \
        --extension-pkg-allow-list=math \
        --ignore-patterns=".*\.md,.*\.sh,.*\.html,pylintrc,LICENSE,build,dist,tags,eo_metadata_tools_cmr.egg-info"
}

# Run all the Unit Tests
unit_test()
{
    printf '*****************************************************************\n'
    printf 'Run the unit tests for all subdirectories\n'
    $pip3 install coverage
    coverage run --source=cmr -m unittest discover
    coverage html
}

# assume that the following has been called:
# python3 -m pip install --user --upgrade setuptools wheel
package_project()
{
    printf '*****************************************************************\n'
    printf 'Run python setup to package the project as a wheel\n'
    $python3 setup.py sdist bdist_wheel
}

# lookup library in pip
find_package()
{
    printf '*****************************************************************\n'
    printf "Find library in $(which $pip3)\n"
    $pip3 list eo-metadata-tools-cmr | grep eo-metadata-tools-cmr
}

# call pip to uninstall the library
uninstall_package()
{
    printf '*****************************************************************\n'
    printf 'Uninstall the project from pip\n'
    $pip3 uninstall eo-metadata-tools-cmr
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
        $pip3 install ${newest}
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
        $pip3 install pydoc-markdown
    fi
    pydoc-markdown
}

config_report()
{
    #grep -ri 'Document-it' cmr | sed -e 's/.*Document-it \({.*}\)/\1/g' | jq -c
    $python3 docit.py > doc/config_properties.md
}

# call the coverage tool to report on which files need more tests
code_coverage()
{
    coverage report --skip-covered --omit='test/*,run.py,setup.py,docit.py,cmr/__init__.py'
}

# call the code coverage report, html version
code_coverage_html()
{
    coverage html --skip-covered --omit='test/*,run.py,setup.py,docit.py,cmr/__init__.py'
}

set_version()
{
    python3="python$1"
    pip3="pip$1"
    echo "NOTE: Using $python3 and $pip3 commands."
}

# Process the command line arguments
while getopts "cCHdfhilprtuv:" opt
do
    case ${opt} in
        c) clean ;;
        C) code_coverage ;;
        d) document_markdown ;;
        f) find_package ;;
        h) help ;;
        H) code_coverage_html ;;
        i) install_package ;;
        l) lint ;;
        p) package_project ;;
        r) config_report ;;
        t) unit_test ;;
        u) uninstall_package ;;
        v) set_version $OPTARG ;;
        *) help ; exit ;;
    esac
done

# default, no options given, run these tasks
if [[ $# -eq 0 ]] ; then
    lint
    unit_test
fi
