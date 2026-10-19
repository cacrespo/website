import os
from bs4 import BeautifulSoup
from django.conf import settings
import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent


def _get_default_model() -> str:
    configured = getattr(settings, "LLM_MODEL", None) or os.getenv(
        "LLM_MODEL", "google:gemini-3.8-flash"
    )
    if configured.startswith("google-gla:"):
        return "google:" + configured.removeprefix("google-gla:")
    return configured


DEFAULT_MODEL = _get_default_model()


class ExtractedArticle(BaseModel):
    title: str = Field(
        description="The title of the article. Maximum 200 characters.",
        max_length=200,
    )
    author: str = Field(
        description=(
            "The author of the article. If an individual author is not identified, "
            "use the name of the publication, organization, or website domain. Max 200 characters."
        ),
        max_length=200,
    )
    description: str = Field(
        description="A concise summary or description of the article's core content."
    )


article_agent = Agent(
    model=DEFAULT_MODEL,
    output_type=ExtractedArticle,
    defer_model_check=True,
    system_prompt=(
        "You are an expert content analyzer. Given the URL, metadata, and text content "
        "of a webpage, extract the title of the article, the author's name (or site/publication "
        "name if the author is not explicitly stated), and provide a concise description/summary."
    ),
)


def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """
    Fetches the web page at url and returns structured text including metadata and body.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    with httpx.Client(
        timeout=timeout, follow_redirects=True, headers=headers
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content tags
    for tag in soup(
        ["script", "style", "nav", "footer", "header", "aside", "noscript"]
    ):
        tag.decompose()

    meta_parts = []
    if soup.title and soup.title.string:
        meta_parts.append(f"HTML Title: {soup.title.string.strip()}")

    # Meta author candidates
    author_meta = (
        soup.find("meta", attrs={"name": "author"})
        or soup.find("meta", attrs={"property": "article:author"})
        or soup.find("meta", attrs={"name": "byl"})
        or soup.find("meta", attrs={"name": "twitter:creator"})
    )
    if author_meta and author_meta.get("content"):
        meta_parts.append(f"Author Meta: {author_meta['content'].strip()}")

    # Meta description candidates
    desc_meta = (
        soup.find("meta", attrs={"name": "description"})
        or soup.find("meta", attrs={"property": "og:description"})
        or soup.find("meta", attrs={"name": "twitter:description"})
    )
    if desc_meta and desc_meta.get("content"):
        meta_parts.append(f"Description Meta: {desc_meta['content'].strip()}")

    # OpenGraph title candidates
    og_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
        "meta", attrs={"name": "twitter:title"}
    )
    if og_title and og_title.get("content"):
        meta_parts.append(f"OG Title: {og_title['content'].strip()}")

    # Main article body
    main_el = soup.find("article") or soup.find("main") or soup.body or soup
    body_text = main_el.get_text(separator=" ", strip=True)

    truncated_body = body_text[:12000]
    metadata_section = "\n".join(meta_parts) if meta_parts else "None"

    return (
        f"Article URL: {url}\n\n"
        f"Metadata:\n{metadata_section}\n\n"
        f"Extracted Content:\n{truncated_body}"
    )


def ensure_api_key(agent: Agent | None = None):
    """
    Ensure GOOGLE_API_KEY is synchronized from GEMINI_API_KEY if present,
    or raise a clear descriptive error if missing.
    """
    target_agent = agent if agent is not None else article_agent
    override_model = getattr(target_agent, "_override_model", None)
    if override_model is not None and override_model.get() is not None:
        return

    gemini_key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get(
        "GEMINI_API_KEY"
    )
    google_key = getattr(settings, "GOOGLE_API_KEY", None) or os.environ.get(
        "GOOGLE_API_KEY"
    )

    if gemini_key and not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key

    if not os.environ.get("GOOGLE_API_KEY") and not google_key and not gemini_key:
        raise ValueError(
            "GEMINI_API_KEY o GOOGLE_API_KEY no está configurada en el servidor."
        )


def extract_article_from_url(
    url: str, agent: Agent | None = None, timeout: float = 10.0
) -> ExtractedArticle:
    """
    Fetches the webpage at the given URL and uses Pydantic AI to extract
    the title, author, and description.
    """
    ensure_api_key(agent)
    content_prompt = fetch_webpage_content(url, timeout=timeout)
    active_agent = agent if agent is not None else article_agent
    result = active_agent.run_sync(content_prompt)
    return result.output
