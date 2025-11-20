# Agent Framework Workshop - Use cases  

## Purpose

This folder contains practical examples aimed to go beyond the core learning chapters. These assets demonstrate applications of Microsoft Agent Framework and show how to extend basic concepts into more advanced implementations.

The aim is to add examples that demonstrate how Microsoft Agent Framework can integrate with **Azure services** and **AI Foundry** to build agentic solutions.

### Example 1: RAG Agent

`1-rag-agent`

This example demonstrates:
- Connecting an **Azure AI Search service** (with a pre-created vectorized index from domain-specific PDFs) to a simple agent.
- Using the search service as a **tool** so the agent can answer questions based on specialized knowledge.

**Prerequisites:**
- An Azure AI Search service with a vectorized index.
- Domain-relevant PDFs uploaded and processed.
- Azure OpenAI embedding model used during indexing.

The Azure resource setup and lab directions for this example are based on the official labs [here](https://github.com/Azure/azure-ai-agents-labs) - Lab 1 and Lab 4.