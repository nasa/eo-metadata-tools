#!/bin/bash

# This is a script to document the commands used to check, test, and build this
#   package.

help()
{
    echo ./runme.sh
    echo "    same as ./runme.sh -l -u"
    echo

    format="%4s %-10s - %-20s\n"
    printf "${format}" Flag Name Description
    printf "${format}" ---- ------- ---------------------
    printf "${format}" '-h' help "Print out this help message"
    printf "${format}" '-d' document "Print out this help message"
    printf "${format}" '-u' 'unit test' "Print out this help message"
    printf "${format}" '-p' package "Print out this help message"
    printf "${format}" '-l' lint "Print out this help message"
}

lint()
{
    printf "*****************************************************************\n"
    printf "Run pylint to check for common code convention warnings\n"
    pylint * \
        --ignore-patterns=".*\.md,.*\.sh,pylintrc,LICENSE,build,dist,eo_metadata_tools_cmr.egg-info"
}

unit_test()
{
    printf "*****************************************************************\n"
    printf "Run the unit test for all subdirectories\n"
    python3 -m unittest discover
}

doc_one()
{
    echo $1
    mkdir -p doc/${1}
    pydoc3 -w $(find ${1} -depth 1 -name '*.py')
    #mv -f *.html doc/${1}

    for item in $(find . -depth 1 -name '*.html')
    do
        # remove local file paths
        cat $item | sed 's|<a href=\"file:/.*</a>||' > doc/$1/$item
        rm $item
    done

    index_it $1 >> doc/${1}/index.html
}

doc_all()
{
    rm -rf doc
    doc_one 'cmr/auth'
    doc_one 'cmr/search'
    doc_one 'cmr/util'
    doc_one 'cmr'
}

index_it()
{
    line="%s\n"
    br="%s<br>\n"
    printf $line "<!DOCTYPE html>\n<html><head>"
    printf "\t<title>$1</title>\n"
    printf $line "<head>\n<body>"
    printf "<h1>Directory %s</h1>\n"
    
    printf "<ul>\n"
    list=$(find ${1} -d 1 | \
        grep -v __pycache__ | \
        grep -v .pyc | \
        grep -v .DS_Store | \
        grep -v index.html | \
        sed "s|$1\/||" | \
        sed "s|\.py|\.html|")
    for item in ${list}
    do
        printf "\t<li><a href=\"${item}\">${item}</a></li>\n"
    done
    printf $line "</ul>"

    printf $file "</body>\n</html>"
}

# assume that the following has been called:
# python3 -m pip install --user --upgrade setuptools wheel
package_project()
{
    python3 setup.py sdist bdist_wheel
}

while getopts "dhlpu" opt
do
    case ${opt} in
        d) doc_all ;;
        h) help ;;
        u) unit_test ;;
        p) package_project ;;
        l) lint ;;
    esac
done

# default, no options given
if [[ $# -eq 0 ]] ; then
    lint
    unit_test
fi
