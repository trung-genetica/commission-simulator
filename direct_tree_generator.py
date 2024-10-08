import csv
import json
from collections import defaultdict
from node_item import NodeItem

class DirectTreeGenerator:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.commission_list = []
        self.root = None

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

    # Method to build the tree structure
    def build_tree(self):
        children_map = defaultdict(list)
        all_nodes = []          # List to maintain order
        all_nodes_set = set()   # Set to track uniqueness
        child_nodes = set()     # Set to track child nodes

        # Create a map of parent-child relationships
        for parent, child in self.commission_list:
            children_map[parent].append(child)
        
            # Add to all_nodes if not already present (to maintain order and uniqueness)
            if parent not in all_nodes_set:
                all_nodes.append(parent)
                all_nodes_set.add(parent)
            if child not in all_nodes_set:
                all_nodes.append(child)
                all_nodes_set.add(child)
        
            # Track child nodes
            child_nodes.add(child)

        # Maintain order while finding root nodes (those with no parent)
        root_children = [node for node in all_nodes if node not in child_nodes]

        # Initialize the root node
        root = NodeItem("GENESIS", None)
        self.root = root

        # Recursively build the tree from root
        def build_node(person, parent_node):
            node = NodeItem(person, parent_node)  # Create NodeItem for each person
            for child in children_map.get(person, []):
                child_node = build_node(child, node)
                node.add_child(child_node)
            return node

        for root_child in root_children:
            root.add_child(build_node(root_child, root))

        # print(root)
        return root

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

                // Append multiple tspans for multi-line text
                nodeEnter.append("text")
                .attr("x", function(d) {{ return d.children || d._children ? -10 : 10; }})
                .attr("dy", ".35em")
                .attr("text-anchor", function(d) {{ return d.children || d._children ? "end" : "start"; }})
                .style("fill-opacity", 1e-6)
                .selectAll("tspan")
                .data(function(d) {{
                    // Provide two lines of text
                    return [
                        d.name,
                        "(Size: " + d.size + ", Com: " + d.commission.toFixed(2) + ")"
                    ];
                }})
                .enter()
                .append("tspan")
                .attr("x", 0)
                .attr("dy", function(d, i) {{ return i === 0 ? "0em" : "1.2em"; }})  // Control the line spacing
                .text(function(d) {{ return d; }});

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

