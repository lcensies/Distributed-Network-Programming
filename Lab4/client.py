import random
import re
import sys
import grpc
import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc


debug = False

if len(sys.argv) > 2 and sys.argv[2].isdigit():
    debug = True
    serv_addr = sys.argv[1]
    n_nums = int(sys.argv[2])
elif len(sys.argv) > 1:
    serv_addr = sys.argv[1]
else:
    serv_addr = "localhost:5555"

channel = grpc.insecure_channel(serv_addr)
stub = pb2_grpc.ServiceStub(channel)

put_regex = re.compile("(?<=^reverse ).*$")
split_regex = re.compile("(?<=^split ).*$")
isprime_regex = re.compile("(?<=^isprime )[\d\s]+$")
nums = []

def isprime_req_iter():
    for i in range(len(nums)):
        req = pb2.IntegerMessage(num=nums[i])
        yield req

if debug:
    nums = [random.randint(0,10000) for i in range(n_nums)]
    isprime_answers = []
    for response in stub.GetIsPrimeStream(isprime_req_iter()):
        isprime_answers.append(response.message)
    for ans in isprime_answers:
        print(ans)
    exit()

while True:
    try:
        req = input().strip()
        if match := re.search(put_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.ReverseText(msg)
            print(response.message)
        elif match := re.search(split_regex, req):
            msg = pb2.SplitTextRequest(message=match.group(0), delim=" ")
            response = stub.SplitText(msg)
            print(f"N_parts: {response.n_parts}, parts: {response.parts}")
        elif match := re.search(isprime_regex, req):
            nums = list(map(lambda x: int(x), filter(lambda x: x.isdigit(), match.group(0).split())))
            isprime_answers = []
            for response in stub.GetIsPrimeStream(isprime_req_iter()):
                isprime_answers.append(response.message)
            for ans in isprime_answers:
                print(ans)
    except KeyboardInterrupt:
        print("Shutting client down")