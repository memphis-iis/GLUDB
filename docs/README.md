GLUDB Documentation
===================

This is the main documentation for GLUDB. The current plan is to deploy to
ReadTheDocs.org (aka RTD). Note that RTD will automatically use the mkdocs.yml
file and the contents of this directory.

You may also build/serve it locally using mkdocs. You can use the script
`make_docs.sh` to run mkdocs from an automatically built virtualenv in this
directory. It also has an additional command to run our make_api_docs.py
script. To build the documentation fresh:


    user@GLUDB $ ./docs/make_docs.sh api
    user@GLUDB $ ./docs/make_docs.sh build --clean

You can also serve the documents at port 4000 (as configured in mkdocs.yml):

    user@GLUDB $ ./docs/make_docs.sh serve

And browsing to http://127.0.0.1:4000/

Please note that api.md is only generated when your run `make_docs.sh` with
the `api` parameter. As a result, the auto-generate feature of the serve
command above won't update api.md to match new docstrings.
