#!/usr/bin/env python
# coding: utf-8

""" Build all notebook files into HTML pages. """

from __future__ import division, print_function

# Standard library
import os
import re
import sys
import json
import shutil

# protect for 2.* vs. 3.*
try:
    import configparser
    cp = configparser
except ImportError:
    import ConfigParser
    cp = ConfigParser

import sunpy
from astropy import log as logger
from IPython.nbformat.current import read, write
from IPython.nbconvert import RSTExporter
from IPython.display import Image

# A template for the index page
with open("templates/index_template.html") as f:
    INDEX_TEMPLATE = f.read()

def walk_through_tutorials(only_published=True, selected_nb_re=None):
    """ Generator for walking through the tutorials directory structure.
        This returns tuples of (full_tutorial_path, tutorial_name) for
        each tutorial. If published is set to True, this will only return
        the published tutorials.
    """
    nbre = re.compile(selected_nb_re) if selected_nb_re else None

    current_directory = os.getcwd()
    tutorials_base = os.path.join(current_directory,'gallery')

    if not os.path.exists(tutorials_base):
        err = ("Can't find 'gallery' path! You must run this script from the"
               " top-level sunpy-gallery directory.")
        raise IOError(err)

    # walk through each directory in tutorials/ to find all .ipynb file
    for tutorial_name in os.listdir(tutorials_base):
        tutorial_path = os.path.join(tutorials_base, tutorial_name)
        if not os.path.isdir(tutorial_path):
            # skip files / things that are not directories
            continue

        for filename in os.listdir(tutorial_path):
            base,ext = os.path.splitext(filename)

            if ext.lower() == ".ipynb" and "checkpoint" not in base:
                full_filename = os.path.join(tutorial_path, filename)
                notebook = read(open(full_filename), 'json')
                is_published = notebook['metadata']['sunpy-gallery'].get('published', False)
                if not is_published and only_published:
                    continue

                if nbre and nbre.match(base) is None:
                    continue

                yield full_filename,notebook

def run_notebooks(selected_nb_re=None):
    """ Run the tutorial notebooks. """
    from runipy.notebook_runner import NotebookRunner

    _orig_path = os.getcwd()

    # walk through each directory in tutorials/ to find all .ipynb file
    for tutorial_filename,nb in walk_through_tutorials(only_published=True,
                                selected_nb_re=selected_nb_re):
        path,filename = os.path.split(tutorial_filename)

        if filename.startswith("_run_"):
            continue

        logger.info("Running tutorial: {}".format(filename))

        # notebook file
        output_filename = os.path.join(path,"_run_{}"
                                       .format(filename))

        # prepend _run_ to the notebook names to create new files
        #   so the user isn't left with a bunch of modified files.
        os.chdir(path)
        r = NotebookRunner(nb, mpl_inline=True)
        r.run_notebook(skip_exceptions=True)
        write(r.nb, open(output_filename, 'w'), 'json')

    os.chdir(_orig_path)

def extract_notebook_thumbnail(filepath, target_file):
    """
    Returns a thumbnail using the last image found in the specified
    notebook.

    For now, just returns the image at it's original size.
    """
    # RSTExporter saves images separately
    rst_exporter = RSTExporter()
    (body, resources) = rst_exporter.from_filename(filepath)

    # Find image entries
    extensions = ('png', 'jpg')
    images = [x for x in resources['outputs'].keys() if x.endswith(extensions)]

    # Save image
    key = images.pop()
    ext = key[-3:]
    image = Image(data=resources['outputs'][key], format=ext)

    # Write image to disk
    fp = open("{}.{}".format(target_file, ext), 'wb')
    fp.write(image.data)
    fp.close()

def convert_notebooks(selected_nb_re=None):
    """ Convert the tutorials (IPython notebook files) located in tutorials/*
        into static HTML pages.
    """
    from IPython.nbconvert.nbconvertapp import NbConvertApp

    current_directory = os.getcwd()
    html_base = os.path.join(current_directory,"html")
    if not os.path.exists(html_base):
        os.mkdir(html_base)
    template_path = os.path.join(current_directory, 'templates')

    app = NbConvertApp()
    app.initialize(argv=[]) # hack
    app.export_format = 'html'
    app.config.Exporter.template_path = ['templates', template_path]
    app.config.Exporter.template_file = 'sunpy'


    # Construct a JSON representation of all the tutorials in the gallery
    gallery = {}

    gallery['meta'] = {
        'sunpy': sunpy.__version__
    }
    gallery['sections'] = {}

    # walk through each directory in tutorials/ to find all .ipynb file
    re_str = ('_run_' + selected_nb_re) if selected_nb_re else None
    for tutorial_filename,nb in walk_through_tutorials(only_published=True,
                                selected_nb_re=re_str):
        path,filename = os.path.split(tutorial_filename)
        if not filename.startswith("_run_"):
            continue

        # remove _run_ from base filename
        base = os.path.splitext(filename)[0]
        cleanbase = base.lstrip("_run_")

        section_name = nb['metadata']['sunpy-gallery'].get('section_name', 'Examples')
        section_dir = os.path.join(html_base, section_name)
        if not os.path.exists(section_dir):
            os.makedirs(section_dir)

        app.output_base = os.path.join(section_dir, cleanbase)
        app.notebooks = [os.path.join(path,filename)]
        app.start()



        # If we haven't processed this section before make it now
        if gallery['sections'].get(section_name, None) is None:
            gallery['sections'][section_name] = []

        gallery['sections'][section_name].append({'notebook': "{}".format(cleanbase),
                                                  'link_name': nb['metadata']['sunpy-gallery']['link_name']})

        # Extract a tumbnail and save it to the same filename as the notebook
        # with a different extension.
        target_file = os.path.join(section_dir, cleanbase)
        extract_notebook_thumbnail(os.path.join(section_dir, tutorial_filename), target_file)

    # Save index_template to index.html
    with open(os.path.join(current_directory,'html','index.html'), 'w') as f:
        f.write(INDEX_TEMPLATE)

    # Output gallery as JSON
    gallery_json = json.dumps(gallery)

    with open('html/gallery.json', 'w') as fp:
        fp.write(gallery_json)

if __name__ == "__main__":
    from argparse import ArgumentParser

    # Define parser object
    parser = ArgumentParser(description="Prepare the tutorials for deployment.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        default=False, help="Be chatty! (default = False)")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        default=False, help="Be quiet! (default = False)")
    parser.add_argument("-n", "--nameregex", default=None,
                        help="A regular expression to select the names of the "
                             "notebooks to be processed.  If not given, all "
                             "notebooks will be used.")

    parser.add_argument('action', nargs='+', choices=['run', 'convert'],
                        help='The action(s) to take when running the script. '
                             '"run" means to just run the notebooks, while '
                             '"convert" will use nbconvert to turn them to '
                             'convert them to HTML.')

    args = parser.parse_args()

    # Set logger level based on verbose flags
    if args.verbose:
        logger.setLevel('DEBUG')
    elif args.quiet:
        logger.setLevel('ERROR')
    else:
        logger.setLevel('INFO')

    for action in args.action:
        if action == 'run':
            run_notebooks(args.nameregex)
        elif action == 'convert':
            convert_notebooks(args.nameregex)
