from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import json
from typing import Optional, Dict, List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Node:
    def __init__(self, left: Optional['Node'] = None, right: Optional['Node'] = None, value: Optional[str] = None):
        self.left = left
        self.right = right
        self.value = value
    

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    rule_string = db.Column(db.Text, nullable=False)
    rule_tree = db.Column(db.Text, nullable=False)

def to_json(root: Optional[Node]) -> Optional[Dict]:
    if root is None:
        return None
    return {
        "value": root.value,
        "left": to_json(root.left),
        "right": to_json(root.right)
    }

def change_json(node):
    if node is None:
        return None
    if node['value'] == '$':
        node['value'] = 'AND'
    elif node['value'] == '|':
        node['value'] = 'OR'
    node['left'] = change_json(node.get('left'))
    node['right'] = change_json(node.get('right'))
    return node

def create_rules(rule_string: str) -> List:
    rule_string = rule_string.strip()
    
    rule_string_mod = rule_string.replace('AND', '$').replace('OR', '|').replace('(', '( ').replace(')', ' )').replace("'", "")
    inf = rule_string_mod.split()
    #print(inf)
    root = None
    or_stack = []
    od_stack= []
    for i in inf:
        node=Node(value=i)
        if i=='(':
            continue
        elif i.isalnum():
            od_stack.append(node)
        elif i==')':
            opr=od_stack.pop()
            opl=od_stack.pop()
            op=or_stack.pop()
            op.left=opl
            op.right=opr
            od_stack.append(op)
            root=op
        else:
            or_stack.append(node)
            #print(op_stack,char_stack)
    while(len(or_stack)):
        #print(1,or_stack,od_stack)
        opr=od_stack.pop()
        opl=od_stack.pop()
        op=or_stack.pop()
        op.left=opl
        op.right=opr
        od_stack.append(op)
        root=op
        #print(op_stack,char_stack)
    json_tree = change_json(to_json(root))
    return [rule_string, json.dumps(json_tree)]

# Evaluate function
def evaluate_rule(node, data):
    if node['left'] is None and node['right'] is None:
        value = node['value']
        # Return the value from the data if it's a field, otherwise return the literal value
        if value in data:
            return data[value]
        return value

    # Evaluate left and right sides recursively
    left_value = evaluate_rule(node['left'], data)
    right_value = evaluate_rule(node['right'], data)

    # Handle comparison and logical operations
    if node['value'] == '>':
        return int(left_value) > int(right_value)
    elif node['value'] == '<':
        return int(left_value) < int(right_value)
    elif node['value'] == '=':
        return str(left_value) == str(right_value)
    elif node['value'] == 'AND':
        return left_value and right_value
    else:
        raise ValueError(f"Unsupported operator: {node['value']}")

def combine_rules(rule_strings):
    temp=""
    print(len(rule_strings),rule_strings)
    for i in range(len(rule_strings)-1):
        temp+='('+rule_strings[i]+') AND '
    temp+='('+rule_strings[-1]+')'
    return create_rules(temp)

#---------------------------------------------------------------------------------------------------------------------------------

# New endpoint to fetch all rule names
@app.route('/get_rule_names', methods=['GET'])
def get_rule_names():
    rules = Rule.query.all()
    rule_names = [rule.name for rule in rules]
    return jsonify(rule_names)

@app.route('/get_rule_data', methods=['GET'])
def get_rule_data():
    rules = Rule.query.all()
    rule_data = [{"name": rule.name, "rule_string": rule.rule_string} for rule in rules]
    return jsonify(rule_data)

# Route to add a new rule
@app.route('/add_rule', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get('rule')
    
    print(rule_string)

    if not rule_string:
        return jsonify({'error': 'Rule string is required'}), 400

    rule_name = f"Rule_{len(Rule.query.all()) + 1}"  
    try:
        ast_node = create_rules(rule_string)
        ast_representation = ast_node[1]  
        new_rule = Rule(name=rule_name, rule_string=ast_node[0],rule_tree=ast_node[1])
        db.session.add(new_rule)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': f'Error creating AST: {str(e)}'}), 500

    return jsonify({
        'message': 'Rule added successfully',
        'rule': {
            'name': rule_name,
            'rule_string': rule_string,
            'ast': ast_representation
        }
    })

# Modify the evaluate endpoint to accept either rule string or rule name
@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    rule_string = data.get('rule')
    rule_name = data.get('rule_name')
    eval_data = data.get('data')
    print(type(eval_data),eval_data)

    if rule_name:
        rule = Rule.query.filter_by(name=rule_name).first()
        if rule:
            rule_string = rule.rule_string
        else:
            return jsonify({'error': 'Rule name not found'}), 404

    if not rule_string or not eval_data:
        return jsonify({'error': 'Rule string/name and data are required'}), 400

    try:
        # Ensure eval_data is a valid dictionary
        if not isinstance(eval_data, dict):
            return jsonify({'error': 'Invalid data format, expected JSON object'}), 400

        ast = json.loads(create_rules(rule_string)[1])
        print(type(ast),ast)
        result = evaluate_rule(ast, eval_data)
    except Exception as e:
        return jsonify({'error': f'Error Evaluating rule: {str(e)}'}), 500
    
    return jsonify({'result': result})



# Modify the combine_rules endpoint to accept either rule strings or rule names
@app.route('/combine_rules', methods=['POST'])
def combine_rules_endpoint():
    data = request.json
    rule_strings = data.get('rules')
    rule_names = data.get('rule_names')

    combined_rule_strings = []

    if rule_strings[0] !='':
        combined_rule_strings=rule_strings

    if rule_names:
        for name in rule_names:
            rule = Rule.query.filter_by(name=name).first()
            if rule:
                combined_rule_strings.append(rule.rule_string)
            else:
                return jsonify({'error': f'Rule name {name} not found'}), 404

    if not combined_rule_strings:
        return jsonify({'error': 'No valid rules or rule names provided'}), 400

    try:
        combined_ast = combine_rules(combined_rule_strings)
        print(combined_ast)
        rule_name = f"Rule_{len(Rule.query.all()) + 1}"  
        ast_representation = combined_ast[1]  # Get string representation of the AST node
        new_rule = Rule(name=rule_name, rule_string=combined_ast[0],rule_tree=combined_ast[1])
        db.session.add(new_rule)
        db.session.commit()
        
    except Exception as e:
        return jsonify({'error': f'Error combining rules: {str(e)}'}), 500

    return jsonify({'combined_rule_ast': ast_representation})

    
@app.route('/get_rule_string', methods=['GET'])
def get_rule_string():
    rule_name = request.args.get('name')
    rule = Rule.query.filter_by(name=rule_name).first()
    if rule:
        return jsonify({'rule_string': rule.rule_string})
    return jsonify({'error': 'Rule not found'}), 404

# Route to serve index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
