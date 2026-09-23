import arxiv

client = arxiv.Client()


def searchArxivPapers(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search arXiv for recent ASR-related research papers.

    Results are normalized into the same structure
    used by Web, Hugging Face, and GitHub.
    """

    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    results = []

    for paper in client.results(search):

        results.append(
            {
                "source": "arxiv",
                "title": paper.title,
                "url": paper.entry_id,
                "description": paper.summary,
                "metadata": {
                    "authors": [author.name for author in paper.authors],
                    "published": (
                        paper.published.isoformat() if paper.published else None
                    ),
                    "updated": (paper.updated.isoformat() if paper.updated else None),
                    "primary_category": (paper.primary_category),
                    "categories": (paper.categories),
                    "pdf_url": (paper.pdf_url),
                },
            }
        )

    return results
