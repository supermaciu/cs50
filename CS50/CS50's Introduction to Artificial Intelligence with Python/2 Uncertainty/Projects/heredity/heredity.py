import csv
import itertools
import sys

# to delete
import pprint

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage and load data
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    print("people:")
    pprint.pprint(people)
    print("prob:")
    pprint.pprint(probabilities)
    print("\n")

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                print(f"joint_probability(people, {one_gene}, {two_genes}, {have_trait}) =", joint_probability(people, one_gene, two_genes, have_trait))
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename: str) -> dict:
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s: set) -> list[set]:
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def joint_probability(people: dict, one_gene: set, two_genes: set, have_trait: set):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set `have_trait` does not have the trait.
    """

    # every person considered
    persons = set(people.keys())

    # persons having no gene
    zero_gene = (persons - one_gene).intersection(persons - two_genes)

    # everyone in set `one_gene` has one copy of the gene
    one_gene_prob = 1
    
    for person in one_gene:
        f = people[person]["father"]
        m = people[person]["mother"]

        if not (f and m):
            one_gene_prob *= PROBS["gene"][1]
            continue

        # P(father_gene v mother_gene) = P(fg) + P(mg) - P(fg ^ mg)
        # 1. If father has 0 copies and mother has 0 copies:
        # * P(g) = mutation * (1 - mutation) = chance for father/mother gene to mutate to 1 copy * the change for mother/father gene to not mutate, stay at 0 copies
        #
        # 2. If father has 1 copy and mother has 1 copy:
        # * P(g) = 0.5 * (1 - mutation) = the chance for passing 1 copy over * the chance for it to not mutate to 0 copies
        #
        # 3. If father has 2 copies and mother has 2 copies:
        # * P(g) = (1 - mutation) * mutation = chance for father/mother gene to not mutate * the chance for mother/father gene to mutate to 0 copies
        #
        # 4. If father has 1 copy and mother has 0 copies:
        # * P(fg) = 0.5 * (1 - mutation) = chance for passing for 1 copy * chance for mother gene not to mutate
        # * P(mg) = mutation * mutation
        #
        # 5. If father has 2 copies and mother has 0 copies:
        # * P(fg) = (1 - mutation) * (1 - mutation) = chance for father gene to not mutate, stay at 2 copies therefore passing over 1 copy * chance for mother to not mutate, stay at 0 copies
        # * P(mg) = mutation * mutation = chance for father gene to mutate to 0 copies * chance for mother gene to mutate to target gene
        #
        # 6. If father has 2 copies and mother has 1 copy:
        # * P(fg) = (1 - mutation) * mutation = the chance for father gene to not mutate * the chance for mother gene to mutate to target gene
        # * P(mg) = 0.5 * mutate = the chance for passing for 1 copy * the chance for father gene to mutate to target gene

        if f in zero_gene and m in zero_gene:
            one_gene_prob *= PROBS["mutation"] * (1 - PROBS["mutation"]) + PROBS["mutation"] * (1 - PROBS["mutation"])
        elif f in one_gene and m in one_gene:
            one_gene_prob *= 0.5 * (1 - PROBS["mutation"]) + 0.5 * (1 - PROBS["mutation"])
        elif f in two_genes and m in two_genes:
            one_gene_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + (1 - PROBS["mutation"]) * PROBS["mutation"]
        elif f in one_gene and m in zero_gene or m in one_gene and f in zero_gene:
            one_gene_prob *= 0.5 * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in zero_gene or m in two_genes and f in zero_gene:
            one_gene_prob *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in one_gene or m in two_genes and f in one_gene:
            one_gene_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + 0.5 * PROBS["mutation"]


    # everyone in set `two_genes` has two copies of the gene
    two_genes_prob = 1

    for person in two_genes:
        f = people[person]["father"]
        m = people[person]["mother"]

        if not (f and m):
            two_genes_prob *= PROBS["gene"][2]
            continue

        if f in zero_gene and m in zero_gene:
            two_genes_prob *= PROBS["mutation"] * (1 - PROBS["mutation"]) + PROBS["mutation"] * (1 - PROBS["mutation"])
        elif f in one_gene and m in one_gene:
            two_genes_prob *= 0.5 * (1 - PROBS["mutation"]) + 0.5 * (1 - PROBS["mutation"])
        elif f in two_genes and m in two_genes:
            two_genes_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + (1 - PROBS["mutation"]) * PROBS["mutation"]
        elif f in one_gene and m in zero_gene or m in one_gene and f in zero_gene:
            two_genes_prob *= 0.5 * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in zero_gene or m in two_genes and f in zero_gene:
            two_genes_prob *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in one_gene or m in two_genes and f in one_gene:
            two_genes_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + 0.5 * PROBS["mutation"]

    # everyone not in `one_gene` or `two_gene` does not have the gene
    zero_gene_prob = 1
    
    for person in zero_gene:
        f = people[person]["father"]
        m = people[person]["mother"]

        if not (f and m):
            zero_gene_prob *= PROBS["gene"][0]
            continue

        if f in zero_gene and m in zero_gene:
            zero_gene_prob *= PROBS["mutation"] * (1 - PROBS["mutation"]) + PROBS["mutation"] * (1 - PROBS["mutation"])
        elif f in one_gene and m in one_gene:
            zero_gene_prob *= 0.5 * (1 - PROBS["mutation"]) + 0.5 * (1 - PROBS["mutation"])
        elif f in two_genes and m in two_genes:
            zero_gene_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + (1 - PROBS["mutation"]) * PROBS["mutation"]
        elif f in one_gene and m in zero_gene or m in one_gene and f in zero_gene:
            zero_gene_prob *= 0.5 * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in zero_gene or m in two_genes and f in zero_gene:
            zero_gene_prob *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
        elif f in two_genes and m in one_gene or m in two_genes and f in one_gene:
            zero_gene_prob *= (1 - PROBS["mutation"]) * PROBS["mutation"] + 0.5 * PROBS["mutation"]

    # everyone in set `have_trait` has the trait
    have_trait_prob = 1

    for person in have_trait:
        if person in zero_gene:
            have_trait_prob *= PROBS["trait"][0][True]
        elif person in one_gene:
            have_trait_prob *= PROBS["trait"][1][True]
        elif person in two_genes:
            have_trait_prob *= PROBS["trait"][2][True]

    # everyone not in set `have_trait` does not have the trait
    no_trait = persons - have_trait
    no_trait_prob = 1

    for person in no_trait:
        if person in zero_gene:
            no_trait_prob *= PROBS["trait"][0][False]
        elif person in one_gene:
            no_trait_prob *= PROBS["trait"][1][False]
        elif person in two_genes:
            no_trait_prob *= PROBS["trait"][2][False]
    
    result = zero_gene_prob * one_gene_prob * two_genes_prob * have_trait_prob * no_trait_prob
    return result


def update(probabilities: dict, one_gene: set, two_genes: set, have_trait: set, p) -> None:
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    persons = set(probabilities.keys())
    zero_gene = (persons - one_gene).intersection(persons - two_genes)

    for person in zero_gene:
        probabilities[person]["gene"][0] += p

    for person in one_gene:
        probabilities[person]["gene"][1] += p
    
    for person in two_genes:
        probabilities[person]["gene"][2] += p

    for person in have_trait:
        probabilities[person]["trait"][True] += p
    
    no_trait = persons - have_trait

    for person in no_trait:
        probabilities[person]["trait"][False] += p

def normalize(probabilities: dict) -> None:
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    # return

    for person in probabilities:
        # gene
        alpha = 1 / sum(probabilities[person]["gene"].values())

        probabilities[person]["gene"][0] *= alpha
        probabilities[person]["gene"][1] *= alpha
        probabilities[person]["gene"][2] *= alpha

        # trait
        if sum(probabilities[person]["trait"].values()) == 0:
            probabilities[person]["trait"][True] = 0
            probabilities[person]["trait"][False] = 1
        else:
            alpha = 1 / sum(probabilities[person]["trait"].values())

            probabilities[person]["trait"][True] *= alpha
            probabilities[person]["trait"][False] = (1 - probabilities[person]["trait"][True])

if __name__ == "__main__":
    main()
