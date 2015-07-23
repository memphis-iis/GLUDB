GLUDB Documentation
===================

This is the main documentation for GLUDB. The current plan is to deploy to
ReadTheDocs.org (aka RTD). Note that RTD will automatically use the mkdocs.yml
file and the contents of this directory.

You may also build/serve it locally using mkdocs. You can use the script
`make_docs.sh` to run mkdocs from an automatically built virtualenv in this
directory. To build the documentation fresh:

    user@GLUDB $ ./docs/make_docs.sh build --clean

You can also serve the documents at port 4000 (as configured in mkdocs.yml):

    user@GLUDB $ ./docs/make_docs.sh serve

And browsing to http://127.0.0.1:4000/
