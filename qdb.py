from defusedxml import sax
from xml.sax.handler import ContentHandler
import htmlentitydefs
import re

HTML_RE = re.compile(r'<.+?>')
HTML_ENT_RE = re.compile(r'&(\w+);')

def indent(string):
  return '\n'.join(map(lambda x: '    ' + x, string.split('\n')))

def stripHtml(string):
  return HTML_RE.sub('', string)

def decodeHtmlEntities(string):
  return HTML_ENT_RE.sub(
    lambda x: unichr(htmlentitydefs.name2codepoint[x.group(1)]),
    string
  )

class QuoteParser(ContentHandler):
  # Cache some funny stuff
  quotes = []
  stepper = iter(quotes)

  # XML parser state
  # f@*# I hate XML
  _item = False
  _description = ''

  # Public API
  def reset(self):
    self.quotes = []
    self.stepper = iter(self.quotes)

  def parse(self, string):
    self.reset()
    sax.parseString(string, self)

  def getRandomQuote(self):
    '''Return a bare string stripped of HTML.'''
    return indent(decodeHtmlEntities(stripHtml(self.stepper.next())).strip())

  # XML parser API
  def startElement(self, name, attrs):
    if name == 'item':
      self._item = True
    elif name == 'description' and self._item:
      self._description = ''

  def characters(self, content):
    if self._item:
      self._description += content

  def endElement(self, name):
    if name == 'item':
      self._item = False
      self.quotes.append(self._description)
