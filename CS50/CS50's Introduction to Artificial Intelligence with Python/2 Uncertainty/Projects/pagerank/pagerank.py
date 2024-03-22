import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probabilites = dict()

    for p in corpus:
        if p == page or p not in corpus[page]:
            probabilites[p] = (1.0 - damping_factor) / len(corpus)
        else:
            # Equation derived from probability marginalization:
            # p - calculated page probability knowing that we are on page
            # damping - damping factor (0.85)
            # NumberOfLinks(page) - number of links on page, if calculated p is on page,
            # if not probability is calculated the same as page
            # N = number of pages in corpus

            # P(p) = P(p and damping) + P(p and not damping) =
            # = 1 / NumberOfLinks(page) + 1 / N
            probabilites[p] = damping_factor/len(corpus[page]) + (1 - damping_factor)/len(corpus)

    return probabilites


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    distribution = dict()
    
    # Setting sample count / probability distribution
    for p in corpus.keys():
        distribution[p] = 0

    # Starting sample
    sample = random.choice(list(corpus.keys()))

    for i in range(n):
        distribution[sample] += 1
        tm = transition_model(corpus, sample, damping_factor)

        sample = random.choices(list(tm.keys()), list(tm.values()))[0]
    
    for p in corpus.keys():
        distribution[p] /= n

    return distribution


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    distribution = dict()
    new_distribution = dict()
    emptyPages = set()

    converged = False
    # Accuracy for the convergence
    eps = 0.001

    # Setting initial values
    for page in corpus.keys():
        distribution[page] = 1 / len(corpus)
        new_distribution[page] = 1 / len(corpus)

    # Getting pages that link to each one
    pageLinks = dict()
    for page in corpus.keys():
        pageLinks[page] = set()

        if len(corpus[page]) == 0:
            emptyPages.add(page)

        for i in corpus.keys():
            if page in corpus[i]:
                pageLinks[page].add(i)

    # Iterative formula
    while not converged:
        for p in corpus.keys():
            sigma = 0
            for i in pageLinks[p]:
                if len(corpus[i]) != 0:
                    sigma += distribution[i] / len(corpus[i])
            
            # Handling pages with no links by adding it's probability divided by length of the corpus
            for i in emptyPages:
                sigma += distribution[i] / len(corpus)
            
            new_distribution[p] = (1 - damping_factor) / len(corpus) + damping_factor * sigma

        # Checking for difference between new values and old values to see if they are converged
        for p in corpus.keys():
            if abs(new_distribution[page] - distribution[page]) < eps:
                converged = True
            else:
                converged = False
        distribution = copy.deepcopy(new_distribution)
    
    return distribution


if __name__ == "__main__":
    main()
