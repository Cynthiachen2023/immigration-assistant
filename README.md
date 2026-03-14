# Immigration Assistant

An AI-powered assistant that helps users understand Australian immigration policies and answers questions in plain language.

## Project Vision

Immigration policy documents are complex, scattered across multiple government websites, and frequently updated. This project aims to build a conversational assistant that:

- Answers questions about visa types, eligibility, and application processes
- Pulls answers from official Australian government sources
- Keeps information up to date
- Is accessible to people without a legal or immigration background

## Target Data Sources

| Source                            | Coverage                                        |
|-----------------------------------|-------------------------------------------------|
| <https://immi.homeaffairs.gov.au> | Federal immigration policy, visas, citizenship  |
| <https://migration.wa.gov.au>     | Western Australia state-nominated migration     |

## Architecture (Planned)

```text
┌─────────────────────────────────────────────────────┐
│                    User Interface                   │
│          (Web app / Chat interface / API)           │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                   LLM + RAG Layer                   │
│   (Retrieval-Augmented Generation with context)     │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Vector Store / Index               │
│         (Semantic search over policy content)       │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Content Pipeline                   │
│  Collect URLs → Classify → Scrape → Chunk → Embed   │
└─────────────────────────────────────────────────────┘
```

