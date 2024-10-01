import functions
from constants import BENEFIT, INITIAL_GRAVITY_COMMISSION_PERCENT

# Global pool to collect any remaining benefit
GLOBAL_POOL = 0.0

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
        root, remainning_benefit = self.distribute_commission(child_node)
        # Process the gravity commission for the root node
        self.gravity_commission(remainning_benefit, root)

    def gravity_commission(self, remaining_benefit, root_node):
        selected_child = None

        # Iterate over the children of the root node and apply gravity probability
        for child in root_node.children:
            # Check if the remaining_benefit should be distributed based on gravity_probability
            if functions.gravity_probability(child):
                # Only the first child with gravity_probability true will get the commission
                gravity_commission = (INITIAL_GRAVITY_COMMISSION_PERCENT / 100) * BENEFIT
            
                # Ensure gravity_commission doesn't exceed the remaining_benefit
                if gravity_commission > remaining_benefit:
                    gravity_commission = remaining_benefit
            
                # Add the gravity commission to the child's total commission
                child.commission += gravity_commission
            
                # Deduct the gravity commission from the remaining benefit
                remaining_benefit -= gravity_commission
            
                # Mark this child as the one who received the commission
                selected_child = child
            
                # Stop further distribution, since only one child gets the commission
                break

        # Recursively apply the same logic for the children of the selected child (if any child received the commission)
        if selected_child is not None and remaining_benefit > 0:
            self.gravity_commission(remaining_benefit, selected_child)
        elif remaining_benefit > 0:
            # If there is still remaining benefit, add it to the global pool and print the action
            global GLOBAL_POOL
            GLOBAL_POOL += remaining_benefit
            print(f"Added {remaining_benefit} to the global pool. Total global pool now: {GLOBAL_POOL}")

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

        root_node = None  # Track the root node

        # Distribute commission among the ancestors
        for i, ancestor in enumerate(ancestors):
            # Set root_node as the last ancestor (root node)
            if i == len(ancestors) - 1:
                root_node = ancestor

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

        # Return the root node and the remaining benefit
        return root_node, benefit    

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
