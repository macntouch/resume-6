# -*- coding: utf-8 -*-
import optparse
import pystache
import pypandoc
import datetime
import json
import glob
import os


def main():

    # parse input parameter options
    p = optparse.OptionParser()
    p.add_option('--json', '-j', default="data.json")
    p.add_option('--template', '-t', default="templates/template.mustache")
    p.add_option('--css', '-c', default="templates/template.css")
    p.add_option('--latex', '-l', default="templates/template.latex")
    p.add_option('--name', '-n', default="resume")
    p.add_option('--directory', '-d', default="bin")
    options, arguments = p.parse_args()

    # setup output directory
    if options.directory[-1:] != '/':
        odir = options.directory + '/'
    else:
        odir = options.directory
    try:
        os.makedirs(odir)
    except OSError:
        pass

    # clean output directory
    fl = glob.glob(odir + options.name + ".*")
    for f in fl:
        os.remove(f)

    # load and prepare json data for template
    jdata = open(options.json)
    data = json.load(jdata)
    jdata.close()

    # add links to github and email
    #gh = data['biodata']['github']
    #ghl = gh.split('@')
    #gh = '[' + gh + '](https://github.com/' + ghl[0] + ')'
    #data['biodata']['github'] = gh

    #email = data['biodata']['email']
    # data['biodata']['email'] = '<' + email + '>'

    # sort and chunk jargon section
    jl = data['biodata']['jargon']
    jl.sort()
    nl = ['']
    wc, rc = 0, 0

    for i in jl:
        i = '#' + i + ' '
        wc = wc + len(i)
        if wc <= 100:
            nl[rc] = nl[rc] + i
        else:
            nl[rc] = nl[rc][0:-1]
            rc += 1
            wc = len(i)
            nl.append(i)

    data['biodata']['jargon'] = nl

    # add separators to phone number
    p = data['biodata']['phone']
    if len(p) == 11:
        data['biodata']['phone'] = p[0] + '.' + p[1:4] + '.' + p[4:7] + '.' + p[7:11]
    elif len(p) == 10:
        data['biodata']['phone'] = p[0:3] + '.' + p[3:6] + '.' + p[6:10]
    elif len(p) == 7:
        data['biodata']['phone'] = p[0:3] + '.' + p[3:7]

    # load mustache template
    tdata = open(options.template)
    template = tdata.read()
    tdata.close()

    # create markdown document
    stream = pystache.render(template, data)
    md_file = open(odir + options.name + '.md', 'w')
    md_file.write(stream)
    md_file.close()

    # general use variables
    author = data['firstname'][0].lower() + data['lastname'].lower()
    cdate = datetime.datetime.now().strftime("%Y.%m.%d-%H:%M")

    # pandoc parameter options
    self_contained = '--self-contained'
    html_file = '--output=' + odir + options.name + '.html'
    html_css = '--css=' + options.css
    html_title = '-T - ' + author + '-resume'
    latex_file = '--output=' + odir + options.name + '.tex'
    latex_engine = '--latex-engine=xelatex'
    latex_template = '--template=' + options.latex
    latex_author = '--variable=author:' + author
    latex_title = '--variable=title:' + author + '-resume'
    latex_date = '--variable=date:' + cdate
    pdf_file = '--output=' + odir + options.name + '.pdf'

    # convert markdown to html using custom css
    pypandoc.convert(odir + options.name + '.md', 'html5',
                     extra_args=[html_css, html_file, self_contained,
                                 html_title])

    # convert markdown to latex using custom latex template
    pypandoc.convert(odir + options.name + '.md', 'latex',
                     extra_args=[latex_template, latex_file, latex_engine,
                                 self_contained, latex_author,
                                 latex_title, latex_date])

    # convert markdown to pdf using custom latex template
    pypandoc.convert(odir + options.name + '.md', 'latex',
                     extra_args=[latex_template, pdf_file, latex_engine,
                                 self_contained, latex_author,
                                 latex_title, latex_date])

if __name__ == '__main__':
    main()
