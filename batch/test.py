from common import parser, context, client, types
import datetime

line = '{"_label_cost":-1,"_label_probability":0.2,"_label_Action":1,"_labelIndex":0,"o":[{"v":0.0,"EventId":"f5e774da-28a8-4a1d-a7fb-f8a1ce6f65f4","ActionTaken":false}],"Timestamp":"2019-11-12T14:22:37.2290000Z","Version":"1","EventId":"f5e774da-28a8-4a1d-a7fb-f8a1ce6f65f4","a":[1,2],"c":{ "GUser":{"id":"rnc", "major": "engineering", "hobby": "hiking", "favorite_character":"spock"}, "_multi": [{ "TAction": { "topic": "HerbGarden" } },{ "TAction": { "topic": "MachineLearning" } }] },"p":[0.2,0.8],"VWState":{"m":"N/A"}}\n'
ccb_line = '{"Timestamp":"2019-09-10T14:43:37.2010000Z","Version":"1","c":{ "GUser":{"id":"mk","major":"psychology","hobby":"kids","favorite_character":"7of9"}, "_multi": [ { "TAction":{"topic":"SkiConditions-VT"} }, { "TAction":{"topic":"HerbGarden"} }, { "TAction":{"topic":"BeyBlades"} }, { "TAction":{"topic":"NYCLiving"} }, { "TAction":{"topic":"MachineLearning"} } ], "_slots": [ { "_id":"52766012-9fae-4579-a6cb-09d5b324ba2b"}, { "_id":"7390b838-616f-4533-a62d-d05f16fe56af"}, { "_id":"52f61a43-7804-4cbb-8702-e70fb46a5a74"}]  },"_outcomes":[{"_label_cost":0.0,"_id":"52766012-9fae-4579-a6cb-09d5b324ba2b","_a":[1,4,0,2,3],"_p":[0.8399999,0.0399999954,0.0399999954,0.0399999954,0.0399999954],"_o":[{"v":0.0,"EventId":"52766012-9fae-4579-a6cb-09d5b324ba2b","ActionTaken":false}]},{"_label_cost":0.0,"_id":"7390b838-616f-4533-a62d-d05f16fe56af","_a":[4,0,3,2],"_p":[0.85,0.05,0.05,0.05],"_o":[{"v":0.0,"EventId":"7390b838-616f-4533-a62d-d05f16fe56af","ActionTaken":false}]},{"_label_cost":0.0,"_id":"52f61a43-7804-4cbb-8702-e70fb46a5a74","_a":[0,3,2],"_p":[0.8666667,0.06666667,0.06666667],"_o":[{"v":0.0,"EventId":"52f61a43-7804-4cbb-8702-e70fb46a5a74","ActionTaken":false}]}],"VWState":{"m":"e787a8ea-11ed-47ee-85a1-09208b068fce/09175024-f7bc-4918-9cd3-07c600b10e71"}}'
parser = parser.DSJsonParser(problem=types.Problem.CB, is_dense=False)
for e in parser.parse(line):
    print(e)


c = context.Context(account_name='ataymanodev',
                    account_key='WxDBTcax+bxLNc6ECKWLKU0ZTj5ZKUV67ei5eiyi2dR2NlONZrh8jby9YpONf8sHH8kJGA9ZAz6FDR9CQOyd2g==',
                    container='small', folder='folder')
logs = client.DSJsonLogsClient(context=c, problem=types.Problem.CB, is_dense=False)
i = 0
start = datetime.datetime(2018, 10, 12)
end = datetime.datetime(2018, 10, 12)
for batch in logs.iterate(start, end, 2):
    print(list(map(lambda fs: list(fs), batch)))
    print('-----------')
