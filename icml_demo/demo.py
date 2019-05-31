from azure.cognitiveservices.personalizer import PersonalizerClient
import azure.cognitiveservices.personalizer.models as models
from msrest.authentication import CognitiveServicesCredentials
from helpers import SlidingAverage

client = PersonalizerClient(endpoint="https://westus2.api.cognitive.microsoft.com/",
    credentials=CognitiveServicesCredentials(""))   # Put your credentials here

user=[{'age': 20}]
actions=[
    models.RankableAction(
        id='politics',
        features=[{'topic': 'politics'}]),
    models.RankableAction(
        id='sports',
        features=[{'topic': 'sports'}])]

request=models.RankRequest(
    context_features=user,
    actions=actions
)

# Since we are doing cold start and there is no model, all probabilities are the same
response=client.rank(request)
for action in response.ranking:
    print(action.id + ': ' + str(action.probability))

print("User loves politics")
ctr = SlidingAverage(window_size=10)
n = 100
for i in range(1, n):
    response=client.rank(request)
    reward = 1.0 if response.reward_action_id=="politics" else 0.0
    client.events.reward(event_id=response.event_id, value=reward)

    ctr.update(reward)
    print('CTR: ' + str(ctr.get()))
    for action in response.ranking:
        print(action.id + ': ' + str(action.probability))


print("User changes his preferences to sports")
ctr = SlidingAverage(window_size=10)
for i in range(1, 5 * n):
    response=client.rank(request)
    reward = 1.0 if response.reward_action_id=="sports" else 0.0
    client.events.reward(event_id=response.event_id, value=reward)

    ctr.update(reward)
    print('CTR: ' + str(ctr.get()))
    for action in response.ranking:
        print(action.id + ': ' + str(action.probability))

#Please run counterfactual evaluation and import result policy to your loop
#Then uncomment the following block and execute it

#print("User changes his preferences back to politics")
#ctr = SlidingAverage(window_size=10)
#for i in range(1, 5 * n):
#    response=client.rank(request)
#    reward = 1.0 if response.reward_action_id=="politics" else 0.0
#    client.events.reward(event_id=response.event_id, value=reward)
    
#    ctr.update(reward)
#    print('CTR: ' + str(ctr.get()))
#    for action in response.ranking:
#        print(action.id + ': ' + str(action.probability))