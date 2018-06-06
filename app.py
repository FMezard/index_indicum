import os
from flask import Flask, render_template

import requests
from lxml import html

from nameparser import HumanName


app = Flask(__name__)
app.debug = True
# app.config.from_object(os.environ['APP_SETTINGS'])

BASE_URL = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'
PAPERS_URLS = [f'{BASE_URL}{i}' for i in range(1,14)]

# Helper functions
def _sort_names(names):
    # Should check for 'last' in keys
    parsed_names = [HumanName(name) for name in names]
    return [' '.join(name) for name in sorted(parsed_names, key=lambda x: x['last'])]


# Routes
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/authors')
def get_authors():

    authors_data = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        a1 = html_content.xpath('//span[@rel="dcterms:creator"]//text()')
        a2 = html_content.xpath('//span[contains(@property, "dcterms:creator")]/text()')
        a3 = html_content.xpath('//h2[contains(@property, "dcterms:creator")]/text()')
        a = _sort_names(list(set(a1+a2+a3)))
        authors_data[f'ISAW Papers {i}'] = a
    return render_template('author.html', authors_data=authors_data)


@app.route('/authors_reversed')
def get_papers():
    authors_papers = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        authors = html_content.xpath('//span[@rel="dcterms:creator"]//text()')
        authors += html_content.xpath('//span[contains(@property, "dcterms:creator")]/text()')
        authors += html_content.xpath('//h2[contains(@property, "dcterms:creator")]/text()')
        authors = list(set(authors))
        for author in authors :
            try :
                authors_papers[author].append(str(i))
            except KeyError:
                authors_papers[author] = [str(i)]

    print(authors_papers)
    return render_template('author_reversed.html', authors_papers=authors_papers)



if __name__ == '__main__':
    app.run()
