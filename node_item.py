import functions
from constants import BENEFIT

class NodeItem:
    def __init__(self, name, parent=None):
        self.parent = parent  # Store parent as a NodeItem, not just the parent_id
        self.name = name
        self.size = 1
        self.commission = 0.0  # Commission with default value 0.0
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)
        self.size += child_node.size
        self.distribute_commission(child_node)

    # Method to distribute commission based on the node instance
    def distribute_commission(self, child_node):
        # Get the ancestors from the current child node up to the root (self)
        ancestors = []
        current_node = self
        while current_node is not None:
            ancestors.append(current_node)
            current_node = current_node.parent

        # Set initial benefit
        benefit = BENEFIT

        # Distribute commission among the ancestors
        for i, ancestor in enumerate(ancestors):
            # Fetch the commission rules
            d = i+1
            percent_commission = functions.get_commission_percent_by_distant(d)
            pow = functions.get_prob_backward_pow_by_distant(d)
            pos = functions.get_prob_backward_pos_of_user(ancestor)

            # Calculate the commission
            commission = functions.compute_commission(
                benefit=benefit,
                percent_commission=percent_commission,
                pow=pow,
                pos=pos
            )

            # Deduct the commission from the benefit and add it to the ancestor's total
            benefit -= commission
            ancestor.commission += commission    

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "commission": self.commission,
            "children": [child.to_dict() for child in self.children]
        }

    def __repr__(self):
        parent_name = self.parent.name if self.parent else "None"
        return f"{self.name} (parent: {parent_name}, commission: {self.commission}, size: {self.size}, children: {self.children})"
