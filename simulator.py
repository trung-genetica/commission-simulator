import argparse
import sys
from enum import Enum
from direct_tree_generator import DirectTreeGenerator


class Command(str, Enum):
    @classmethod
    def get_list(cls):
        return [cmd.value for cmd in Command]


class TreeSimulator:
    input_file = ""
    referral_log = []

    def __init__(self):
        pass

    def load_input_file(self, input_file):
        self.input_file = input_file
        # Implement your input file loading logic here
        # This example simply reads the contents of the file
        try:
            with open(self.input_file, "r") as f:
                data = f.read()
        except FileNotFoundError:
            print(f"Find {self.input_file} not found")
            exit(1)

        self.referral_log = []
        return data

    def validate_input(self):
        errors = []
        # Implement your validation logic here
        # This example simply checks if the file exists

        if not errors:
            print(f"Input file {self.input_file} is valid")
        else:
            print(f"Input file {self.input_file} is not valid", {"\n-\t".join(errors)})

    def generate_direct_tree(self):
        # Generate direct tree using DirectTreeGenerator
        output_file = "direct_tree.html"
        tree_generator = DirectTreeGenerator(self.input_file)
        tree_generator.parse_csv_to_commission_list()  # Parse the input CSV
        tree_data = tree_generator.build_tree()  # Build the tree structure
        html_content = tree_generator.generate_html(tree_data.to_dict())  # Generate HTML content
        tree_generator.save_html(output_file, html_content)  # Save the HTML file
        print(f"Direct tree has been generated and saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Tree Simulator")

    parser.add_argument("input_file", help="Name of the input file")

    args = parser.parse_args(sys.argv[1:])

    simulator = TreeSimulator()
    simulator.load_input_file(args.input_file)
    simulator.validate_input()

    simulator.generate_direct_tree()


if __name__ == "__main__":
    main()
