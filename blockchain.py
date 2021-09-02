import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # 새로운 제네시스 블록 만들기
        self.new_block(previous_hash=1, proof=100)
    
    def new_block(self, proof, previous_hash=None):
        # 블록체인에 들어갈 새로운 블록을 만드는 코드이다.
        # index는 블록의 번호, timestamp는 블록이 만들어진 시간
        # transaction은 블록에 포함될 거래이다.
        # proof는 논스값이고, previous_hash는 이전 블록의 해시값

        block = {
            'index' : len(self.chain)+1,
            'timestamp' : time(),
            'transactions' : self.current_transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
        }
        
        # 거래의 리스트를 초기화한다.
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # 새로운 거래는 다음으로 채굴될 블록에 포함되게 된다. 거래는 3개의 인자로 구성되어 있다.
        # sender와 recipient는 string으로 각각 수신자와 송신자의 주소이다.
        # amount는 int로 전송되는 양을 의미한다. return은 해당 거래가 속해질 블록의 숫자를 의미한다.

        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        # 체인의 가장 마지막 블록을 반환한다
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # SHA-256을 이용하여 블록의 해시값을 구한다.
        # 해시값을 만드는데 block이 input 값으로 사용된다.

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # 작업증명에 대한 설명
        # - p는 이전값, p'는 새롭게 찾아야하는 값이다.
        # hash(pp')의 결과값이 첫 4개의 0으로 이루어질 때까지 p'를 찾는 과정이 작업증명 과정이다.

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1 

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # 작업증명 결과값을 검증하는 코드이다. 
        # hash(p,p')값의 앞의 4자리가 0으로 이루어져 있는가를 확인한다.
        # 결과값은 boolean으로 조건을 만족하지 못하면 false가 반환된다.

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



# 노드를 인스턴스화 한다.
app = Flask(__name__)

# 이 노드에 대해 전역적으로 고유한 주소를 생성한다.
node_identifier = str(uuid4()).replace('-', '')

# 블록체인 클래스를 인스턴스화 한다.
blockchain = Blockchain()

# /mine의 endpoint를 만든다(요청을 GET하는곳)
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 블록 채굴에 대한 보상을 설정한다.
    # 송신자를 0으로 표현한 것은 블록 채굴에 대한 보상이기 때문.
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )

    # 체인에 새로운 블록을 추가하는 코드
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200



# /transaction/new의 endpoint를 만든다(데이터를 보내고 요청을 post 하는곳)
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    return "We'll add an new transaction"
    values = request.get_json()

    #필요한 값이 모두 존재하는지 확인
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 새로운 거래를 추가한다.
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


    
# /chain의 endpoint를 만든다.(전체 블록체인을 반환하는 곳)
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200




# 5000번 포트로 서버를 돌려라
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)








        

    

    