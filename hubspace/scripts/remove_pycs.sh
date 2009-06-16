for i in `find . -iname *.pyc`; do
    svn remove --force $i
done