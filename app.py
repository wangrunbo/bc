from uuid import uuid4
import requests
from time import time

from flask import Flask, request, jsonify
from blockchain.blockchain import Blockchain


app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = uuid4().hex

blockchain = Blockchain()


@app.route('/mine/<wallet_address>', methods=['GET'])
def mine(wallet_address):
    nonce = blockchain.proof_of_work()

    blockchain.reward(recipient=wallet_address)

    block = blockchain.new_block(nonce)

    # TODO 广播
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    timestamp = time()

    values = request.json

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(timestamp, values['sender'], values['recipient'], values['amount'])

    response = {
        'message': 'Transaction has been submitted successfully',
        'block_index': index
    }

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain.chain), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
