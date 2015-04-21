from flowdock import JSONStream
import requests
import urllib
import random
import yaml

fd = open('./config.yml','r')
config_yml = yaml.load(fd)
fd.close()

api_token = config_yml.get('FLOWDOCK',{}).get('API_TOKEN')

random_giphy = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC'

# Incase of emergency

# requests.delete('https://<API_TOKEN>:blarg@api.flowdock.com/flows/<ORG>/<FLOW_NAME>/messages/<MESSAGE_ID>')

org = config_yml.get('FLOWDOCK',{}).get('ORGANIZATION')

fetch_flows = ['%s/%s' % (org, flow,) for flow in config_yml.get('FLOWDOCK',{}).get('FLOWS',[])]

flows = requests.get('https://%s:blarg@api.flowdock.com/flows' % api_token).json()
users = requests.get('https://%s:blarg@api.flowdock.com/users' % api_token).json()

def getFlowNameFromId(id):
  return [x for x in flows if x['id'] == id][0]['parameterized_name']

def getUserNameFromID(id):
  return [x for x in users if x['id'] == id][0].get('nick','')

def postMessageToFlow(flow_name, content, thread_id = None):
  try:

    message_data = {
      'event':'message',
      'content':content,
      'external_user_name': 'FlowBot'
    }

    if thread_id != None:
      message_data['thread_id'] = thread_id

    requests.post('https://%s:blarg@api.flowdock.com/flows/%s/%s/messages' % (api_token, org, flow_name, ), data = message_data)

  except:
    pass

def getGiphyUrlFromContent(content):
  
  tag = ''

  try:
    tag = urllib.quote_plus(content.split(' ', 1)[1])
  except:
    pass

  try:
    if len(tag) != 0:
      giphy = requests.get(random_giphy + '&tag=%s' % tag).json().get('data',{}).get('image_original_url','')
    else:
      giphy = requests.get(random_giphy).json().get('data',{}).get('image_original_url','')  
  except:
    giphy = 'Failed to find something funny. Whoops.'
    print 'Failed to find something for the following tag: %s' % tag
    pass

  return giphy


stream = JSONStream(api_token)
gen = stream.fetch(fetch_flows)

for data in gen:
    if isinstance(data, dict):
      if data.get('event','') == 'message':

        content = data.get('content','')
        thread_id = data.get('thread_id', None)
        flow_name = 'main'
        user_name = 'FlowBot'

        try:
          flow_name = getFlowNameFromId(data.get('flow'))
          user_name = getUserNameFromID(int(data.get('user')))
        except:
          pass

        if content.startswith('\giphy'):

          try:
            message = getGiphyUrlFromContent(content)
            postMessageToFlow(flow_name, message, thread_id)
          except:
            pass

        elif content.startswith('\\roll'):

          try:
            message = '%s rolled: %s' % (user_name, random.randint(0, 100),)
            postMessageToFlow(flow_name, message, thread_id)
          except:
            pass

        elif content.startswith('\\dance'):

          try:
            message = '%s bursts into dance~' % (user_name,)
            postMessageToFlow(flow_name, message, thread_id)
          except:
            pass