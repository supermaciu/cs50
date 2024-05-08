import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword: Crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Removing all values from domains that don't match the length of it's variables
        for var in self.crossword.variables:
            to_delete = set()
            for word in self.domains[var]:
                if var.length != len(word):
                    to_delete.add(word)
            self.domains[var] -= to_delete

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        to_delete = set()

        # If two words have no overlap there is no domain to revise
        if overlap is None:
            return revised

        for word_x in self.domains[x]:
            satisfied = False
            for word_y in self.domains[y]:
                i, j = overlap

                if word_x[i] == word_y[j]:
                    satisfied = True
            
            if not satisfied:
                to_delete.add(word_x)
                revised = True
        
        self.domains[x] -= to_delete
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Getting a queue (First-In-First-Out) of all arcs in csp
        queue = list(self.crossword.overlaps.keys()) if arcs == None else list(arcs)
        
        while len(queue) > 0:
            x, y = queue.pop()
            
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                
                for z in self.crossword.neighbors(x):
                    queue.append((z, x))
        
        return True

    def assignment_complete(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Checking if variables assigned are matching initial crossword variables
        return set(assignment.keys()) == self.crossword.variables

    def consistent(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Checking if variables' sizes match with their values
        for var in assignment.keys():
            if var.length != len(assignment[var]):
                return False
        
        # Checking if words are distinct
        for w1 in assignment.values():
            count = 0
            for w2 in assignment.values():
                if w1 == w2:
                    count += 1
                
                if count > 1:
                    return False

        # Checking if overlapping characters match letters in both words
        for (x, y), overlap in self.crossword.overlaps.items():
            if x in assignment.keys() and y in assignment.keys() and overlap is not None:
                word_x = assignment[x]
                word_y = assignment[y]
                i, j = overlap

                if word_x[i] != word_y[j]:
                    return False
        
        return True

    def order_domain_values(self, var, assignment: dict[Variable, str]):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create a dictionary of values and its quantity of instances in all of neighbors' domains
        # except values that are already assigned
        unassigned_values = self.domains[var] - set(assignment.values())
        values = {
            word: 0
            for word in unassigned_values
        }

        for neighbor in self.crossword.neighbors(var):
            for word in self.domains[neighbor]:
                if word in values.keys():
                    values[word] += 1

        # Return a list of values sorted by the descending quantity,
        # first value to have the least instances in all of neighbors' domains
        return list(dict(sorted(values.items(), key=lambda x: x[1])).keys())

    def select_unassigned_variable(self, assignment: dict[Variable, str]):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get all unassigned variables
        unassigned_variables = self.crossword.variables - assignment.keys()

        return sorted(unassigned_variables,
                      key=lambda v: (len(self.domains[v]),  # Sorting by minimum remaining values (MRV) ascending
                                     -len(self.crossword.neighbors(v))))[0]  # Sorting by highest degree descending

    def backtrack(self, assignment: dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for val in self.order_domain_values(var, assignment):
            if self.consistent(assignment):
                assignment[var] = val

                result = self.backtrack(assignment)
                
                if result is not None:
                    return result
        
            # Deleting most recently added variable = value pair
            assignment.popitem()

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
