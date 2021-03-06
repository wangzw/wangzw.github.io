#!/usr/bin/env bash
BRANCH=master
TARGET_REPO=wangzw/wangzw.github.io.git
PELICAN_OUTPUT_FOLDER=blog/output

echo -e "Testing travis-encrypt"
echo -e "$VARNAME"

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
    echo -e "Starting to deploy to Github Pages\n"
    if [ "$TRAVIS" == "true" ]; then
        git config --global user.email "travis@travis-ci.org"
        git config --global user.name "Travis"
    fi
    #using token clone gh-pages branch
    git clone --quiet --branch=$BRANCH https://${GH_TOKEN}@github.com/$TARGET_REPO built_website > /dev/null
    #go into directory and copy data we're interested in to that directory
    cd built_website
    rm -rf *
    mkdir -p resume
    cp ../CNAME ./
    cp ../index.html ./
    cp ../resume/*.pdf resume/
    #add, commit and push files
    git add -f --all .
    git commit -m "Travis build $TRAVIS_BUILD_NUMBER pushed to Github Pages"
    git push -fq origin $BRANCH > /dev/null
    echo -e "Deploy completed\n"
fi
