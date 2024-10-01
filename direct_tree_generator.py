import csv
import json
from collections import defaultdict

class NodeItem:
    def __init__(self, name, parent=None):
        self.parent = parent  # Store parent as a NodeItem, not just the parent_id
        self.name = name
        self.size = 1
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)
        self.size += child_node.size

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "children": [child.to_dict() for child in self.children]
        }

    def __repr__(self):
        parent_name = self.parent.name if self.parent else "None"
        return f"{self.name} (parent: {parent_name}, size: {self.size}, children: {self.children})"

class DirectTreeGenerator:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.commission_list = []
        self.node_map = {}

    # Method to read and parse the CSV file into a commission list
    def parse_csv_to_commission_list(self):
        try:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # The structure: (parent, child)
                    parent = row['life_app_ref_code']
                    child = row['life_app_personal_ref_code']
                    self.commission_list.append((parent, child))
        except FileNotFoundError:
            print(f"Error: File '{self.csv_file}' not found.")
            exit(1)

    # Method to build the tree structure with size and store nodes in node_map
    def build_tree(self):
        children_map = defaultdict(list)
        all_nodes = set()
        child_nodes = set()

        for parent, child in self.commission_list:
            children_map[parent].append(child)
            all_nodes.add(parent)
            all_nodes.add(child)
            child_nodes.add(child)

        root_children = all_nodes - child_nodes

        root = NodeItem("GENESIS", None)
        self.node_map["GENESIS"] = root

        def build_node(person, parent_node):
            node = NodeItem(person, parent_node)  # Set the parent as the actual NodeItem
            self.node_map[person] = node  # Store node in node_map with its ID

            for child in children_map.get(person, []):
                child_node = build_node(child, node)
                node.add_child(child_node)

            return node

        for root_child in root_children:
            root.add_child(build_node(root_child, root))

        return root

    # Method to get a list of ancestors from a node to the root
    def get_backward_node_list_to_root(self, node_id):
        result = []
        current_node = self.node_map.get(node_id)

        if current_node is None:
            print(f"Error: Node '{node_id}' not found in the tree.")
            return []

        # Traverse upwards using the parent pointer
        while current_node.parent is not None:
            result.append(current_node.parent.name)
            current_node = current_node.parent

        return result

    # Method to generate HTML content with embedded tree data
    def generate_html(self, tree_data):
        # Convert the tree data to JSON
        tree_data_json = json.dumps(tree_data)

        # Define the HTML template, embedding the JSON data and the D3.js script
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>D3.js Tree Visualization</title>
            <script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
            <style>
                .node {{
                    cursor: pointer;
                }}
                .node circle {{
                    fill: #fff;
                    stroke: steelblue;
                    stroke-width: 1.5px;
                }}
                .node text {{
                    font: 10px sans-serif;
                }}
                .link {{
                    fill: none;
                    stroke: #ccc;
                    stroke-width: 1.5px;
                }}
                .svg-container {{
                    width: 100%;
                    height: 100%;
                    overflow-x: auto;
                    overflow-y: auto;
                    white-space: nowrap;
                    display: block;
                    min-width: 200%; 
                    min-height: 200%; 
                }}
            </style>
        </head>
        <body>

        <!-- Add buttons for expanding and collapsing all nodes -->
        <button onclick="expandAll()">Expand All</button>
        <button onclick="collapseAll()">Collapse All</button>

        <div class="svg-container">
            <svg id="treeSVG"></svg>
        </div>

        <script src="//d3js.org/d3.v3.min.js"></script>
        <script>
            var margin = {{top: 20, right: 120, bottom: 20, left: 220}},
                width = 3000 - margin.right - margin.left,
                height = window.innerHeight * 2;

            var i = 0,
                duration = 750,
                root;

            var tree = d3.layout.tree()
                .size([height, width]);

            var diagonal = d3.svg.diagonal()
                .projection(function(d) {{ return [d.y, d.x]; }});

            var svg = d3.select("#treeSVG")
                .attr("width", width + margin.right + margin.left)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var treeData = {tree_data_json};

            root = treeData;
            root.x0 = height / 2;
            root.y0 = 0;

            // Collapse all nodes except root and its immediate children
            function collapse(d) {{
                if (d.children) {{
                    d.children.forEach(collapse);
                    d._children = d.children;
                    d.children = null;
                }}
            }}

            root.children.forEach(collapse);
            update(root);

            function update(source) {{
                var nodes = tree.nodes(root).reverse(),
                links = tree.links(nodes);

                // Increase both horizontal and vertical spacing between nodes
                nodes.forEach(function(d) {{ 
                    d.y = d.depth * 100;  // Horizontal spacing (depth-based)
                    // d.x = d.x * 1.2;      // Increase vertical spacing between nodes
                }});

                var node = svg.selectAll("g.node")
                    .data(nodes, function(d) {{ return d.id || (d.id = ++i); }});

                var nodeEnter = node.enter().append("g")
                    .attr("class", "node")
                    .attr("transform", function(d) {{ return "translate(" + source.y0 + "," + source.x0 + ")"; }});

                nodeEnter.append("circle")
                    .attr("r", 1e-6)
                    .style("fill", function(d) {{ return d._children ? "lightsteelblue" : "#fff"; }})
                    .on("click", click);

                nodeEnter.append("text")
                    .attr("x", function(d) {{ return d.children || d._children ? -10 : 10; }})
                    .attr("dy", ".35em")
                    .attr("text-anchor", function(d) {{ return d.children || d._children ? "end" : "start"; }})
                    .text(function(d) {{ return d.name; }})
                    .style("fill-opacity", 1e-6);

                var nodeUpdate = node.transition()
                    .duration(duration)
                    .attr("transform", function(d) {{ return "translate(" + d.y + "," + d.x + ")"; }});

                nodeUpdate.select("circle")
                    .attr("r", 10)
                    .style("fill", function(d) {{ return d._children ? "lightsteelblue" : "#fff"; }});

                nodeUpdate.select("text")
                    .style("fill-opacity", 1);

                var nodeExit = node.exit().transition()
                    .duration(duration)
                    .attr("transform", function(d) {{ return "translate(" + source.y + "," + source.x + ")"; }})
                    .remove();

                nodeExit.select("circle")
                    .attr("r", 1e-6);

                nodeExit.select("text")
                    .style("fill-opacity", 1e-6);

                var link = svg.selectAll("path.link")
                    .data(links, function(d) {{ return d.target.id; }});

                link.enter().insert("path", "g")
                    .attr("class", "link")
                    .attr("d", function(d) {{
                        var o = {{x: source.x0, y: source.y0}};
                        return diagonal({{source: o, target: o}});
                    }});

                link.transition()
                    .duration(duration)
                    .attr("d", diagonal);

                link.exit().transition()
                    .duration(duration)
                    .attr("d", function(d) {{
                        var o = {{x: source.x, y: source.y}};
                        return diagonal({{source: o, target: o}});
                    }})
                    .remove();

                nodes.forEach(function(d) {{
                    d.x0 = d.x;
                    d.y0 = d.y;
                }});
            }}

            function click(d) {{
                if (d.children) {{
                    d._children = d.children;
                    d.children = null;
                }} else {{
                    d.children = d._children;
                    d._children = null;
                }}
                update(d);
            }}

            // Function to expand all nodes
            function expandAll() {{
                function expand(d) {{
                    if (d._children) {{
                        d.children = d._children;
                        d._children = null;
                    }}
                    if (d.children) {{
                        d.children.forEach(expand);
                    }}
                }}
                expand(root);
                update(root);
            }}

            // Function to collapse all nodes
            function collapseAll() {{
                function collapse(d) {{
                    if (d.children) {{
                        d.children.forEach(collapse);
                        d._children = d.children;
                        d.children = null;
                    }}
                }}
                root.children.forEach(collapse);
                update(root);
            }}
        </script>
        </body>
        </html>
        """

        return html_template

    # Method to save the generated HTML file
    def save_html(self, output_filename, html_content):
        with open(output_filename, "w") as html_file:
            html_file.write(html_content)

