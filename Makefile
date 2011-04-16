clean:
	-find . -name '*~' -exec rm {} \;
	-rm MANIFEST
	-debuild clean 
	-rm -Rf build
	-rm -Rf dist

deb: clean
	debuild binary
	scp -r ../*.deb scm:/home/groups/slideotracker/htdocs/debs/	

pydist:	clean
	python setup.py bdist
	python setup.py sdist
	scp -r dist/* scm:/home/groups/slideotracker/htdocs/dist/

uptest:
	tar -pczf  /tmp/demo.tar.gz tests/data/videos/video.avi tests/data/slides/ tests/data/test.txt
	scp /tmp/demo.tar.gz scm:/home/groups/slideotracker/htdocs/demo/

