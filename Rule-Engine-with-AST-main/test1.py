from typing import Optional, Dict, List

class Node:
    def __init__(self, left: Optional['Node'] = None, right: Optional['Node'] = None, value: Optional[str] = None):
        self.left = left
        self.right = right
        self.value = value
    
    def __repr__(self):
        return f"Node(value={self.value}, left={self.left}, right={self.right})"

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

def create_rule(rule_string: str) -> List:
    rule_string = rule_string.strip()
    
    rule_string_mod = rule_string.replace('AND', '$').replace('OR', '|').replace('(', '( ').replace(')', ' )').replace("'", "")
    inf = rule_string_mod.split()
    print(inf)
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
    return [rule_string, json_tree]

def combine_rules(rule_strings):
    temp=""
    for i in range(len(rule_strings)-1):
        temp+='('+rule_strings[i]+') AND '
    temp+=rule_strings[-1]
    return create_rule(temp)

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
    elif node['value'] == '=':
        return left_value == right_value
    elif node['value'] == 'AND':
        return left_value and right_value
    else:
        raise ValueError(f"Unsupported operator: {node['value']}")

# Example rule string
rule_strings= "(age > 20)"
data={'age': 2}
print(evaluate_rule(create_rule(rule_strings)[1],data))
