"""
run_ai_landscape_report.py — Runs Leary directly to produce the AI Landscape 2026 report.
"""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
AGENT_TEAM = PROJECT_ROOT / "Agent Team"

sys.path.insert(0, str(AGENT_TEAM))
sys.path.insert(0, str(PROJECT_ROOT))

TASK = """
Produce a comprehensive executive research report titled:
"The AI Landscape 2026: From Automation to Agentic Intelligence — A Guide to the Leading Models"

This report is for senior banking executives and technology leaders. Use the research data
provided below as your factual foundation — expand upon it with your own knowledge where
relevant, but do not contradict the figures provided.

---

RESEARCH DATA (web-researched, March 2026):

TYPES OF AI:
- RPA (Robotic Process Automation): software robots performing rule-based, repetitive tasks
  (logging into systems, copying data, processing invoices, generating reports). Follows
  predefined instructions without learning or adapting. Vendors: UiPath, Automation Anywhere,
  Blue Prism, SS&C Blue Prism.
- Traditional / Narrow AI: ML models trained for specific tasks — fraud detection, credit
  scoring, image recognition, recommendation engines. Does not generalise beyond training domain.
  Examples: FICO credit scoring, Mastercard fraud detection models.
- Generative AI: systems producing original content (text, images, code, audio, video) in
  response to prompts. Reactive — responds to inputs. Creates new content vs. classifying
  or predicting existing patterns. IBM framing: "Generative AI is the creator."
- Agentic AI: systems pursuing goals autonomously over multiple steps, making decisions,
  using tools, taking real-world actions with minimal human oversight. Proactive — sets and
  pursues goals. Combines LLMs with memory, planning, and tool-use. IBM framing:
  "Agentic AI is the thinker and doer."
- Integration trend 2025-2026: RPA + Agentic AI — RPA handles execution, Agentic AI handles
  complex decisions. Human focuses on strategy and innovation.

CLOSED-SOURCE LARGE LANGUAGE MODELS (March 2026):

1. GPT-5.4 (OpenAI) — released March 5, 2026
   Three variants: Standard, Thinking (reasoning-first), Pro (max capability).
   Context window: up to 1.05 million tokens. Native computer use capability (first for GPT series).
   Reduces claim errors by 33%, full-response errors by 18% vs GPT-5.2.
   API pricing: $2.50/1M input tokens (Standard).
   Strengths: General reasoning leader, versatile, large ecosystem, creative work, everyday tasks.
   Weaknesses: Vendor lock-in, data privacy concerns, expensive at Pro tier, can be verbose.

2. Claude Opus 4.6 / Claude Sonnet 4.6 (Anthropic) — released February 2026
   Context window: 1M tokens (beta), 128K output.
   Pricing: $15/$75 per million tokens (Opus input/output).
   Leads SWE-bench (real-world software engineering tasks) — strongest coding of any commercial model.
   Safety-focused design; excellent for agentic workflows.
   Strengths: Best-in-class coding, long-form content, captures writing style, safety-first,
   reliable for enterprise, agentic-friendly.
   Weaknesses: Text-first (relies on external APIs for vision/audio), premium pricing.

3. Gemini 3.1 Pro (Google DeepMind) — launched February 19, 2026
   Leads 13 of 16 major benchmarks: 80.6% SWE-bench, 94.3% GPQA Diamond, 77.1% ARC-AGI-2.
   Pricing: $2/$12 per million tokens — cost-effective at frontier level.
   Full video processing (Veo 3), 24-language voice support, 75% prompt caching discounts.
   Tiered thinking levels: Low/Medium/High. Native multimodal (text/image/audio/video).
   Strengths: Overall benchmark leader, most cost-effective frontier model, best multimodal,
   real-time web search, best for research and fact-based queries.
   Weaknesses: Can produce verbose outputs, "corporate gibberish" in long reports, Google
   ecosystem dependency.

4. Grok 4 (xAI) — early 2026
   Real-time X/Twitter data integration. Strong reasoning and mathematics benchmarks.
   Strengths: Real-time social data, strong quantitative reasoning, competitive pricing.
   Weaknesses: Smaller ecosystem, less enterprise track record, data privacy concerns.

5. Mistral Large 3 (Mistral AI) — 2025/2026
   European-origin model. GDPR-compliant hosting options available.
   Strengths: Strong multilingual (European languages), data sovereignty for EU regulated firms,
   fine-tunable, competitive on instruction following.
   Weaknesses: Smaller community vs OpenAI/Google, fewer enterprise integrations.

OPEN-SOURCE / OPEN-WEIGHT LARGE LANGUAGE MODELS:

1. Llama 4 Scout & Maverick (Meta) — 2025
   Maverick: highest raw MMLU at 85.5%; strong coding, reasoning, multilingual.
   Scout: 10M token context window — unmatched for long-context tasks.
   Apache 2.0 license (commercial use permitted). Massive community ecosystem.
   Strengths: Free to deploy, fine-tunable, massive community, long-context (Scout),
   strong multilingual, no API costs.
   Weaknesses: Requires significant compute to self-host; not as strong as frontier
   closed models on complex reasoning.

2. DeepSeek V4 (DeepSeek AI) — March 3, 2026
   1-trillion parameter open-weight model. MODEL1 architecture with tiered KV cache:
   40% memory reduction, 1.8x inference speedup. Leads multilingual evaluation benchmarks.
   MIT license.
   Strengths: Open-weight at frontier scale, revolutionary cost-efficiency, strong maths/reasoning,
   free commercial use.
   Weaknesses: Chinese-origin data concerns in some regulated industries; massive compute required.

3. DeepSeek R2 (DeepSeek AI) — January 2026
   Frontier-class reasoning at dramatically lower API cost: $0.55/$2.19 per million tokens.
   Mathematical reasoning rivalling GPT-5.4. DeepSeek V3.2 variant achieved gold-medal
   performance at IMO 2025, IOI 2025, and ICPC World Finals 2025.
   Strengths: Best value reasoning model, exceptional maths, open weights available.
   Weaknesses: Geopolitical concerns for regulated banking jurisdictions.

4. Qwen 3.5 397B-A17B (Alibaba) — 2025/2026
   Apache 2.0 license. Best-in-class multilingual (especially Asian languages).
   Strong general-purpose chat and 2026 AI agent workloads.
   Strengths: Free commercial use, excellent multilingual, strong agentic performance.
   Weaknesses: Community less mature than Llama; Chinese-origin considerations for
   some regulated institutions.

5. Mixtral 8x22B (Mistral AI) — open source
   Mixture-of-Experts: 8 expert networks, 2 activated per token. Fast and efficient.
   Strengths: Open source, MoE efficiency, fast inference, strong instruction following,
   deployable on enterprise hardware.
   Weaknesses: Older architecture vs 2026 frontier; less competitive on complex reasoning.

SMALL LANGUAGE MODELS (SLMs — typically under 20B parameters, edge/on-device deployable):

1. Microsoft Phi-4 (14B) — 2025/2026
   84.8% on MATH benchmark, 82.5% on GPQA Diamond — outperforms models 10x its size.
   Runs 15x faster on local hardware than frontier models. Memory: ~9.1GB quantized.
   Training: curated synthetic data + distillation.
   Strengths: Best maths/logic SLM, local deployment, privacy-first, excellent enterprise edge.
   Weaknesses: 16K token context only — not suitable for long documents.

2. Google Gemma 3 (2B to 27B) — 2025/2026
   Open-weight, built on Gemini research. Multimodal from 4B up (text + images).
   Runs on laptops and private cloud. Context: 128K tokens. Memory: ~8.1GB quantized.
   Strengths: Google-quality in small package, multimodal, long context, open weights,
   ideal for privacy-first SMBs.
   Weaknesses: Google ecosystem dependency; less fine-tuning community than Phi.

3. Mistral Small 4 — March 2026
   119B total parameters, 128 experts, only 6B active per token (MoE architecture).
   NVIDIA NIM compatible. Tekken tokenizer.
   Strengths: Efficient inference despite large total parameters, strong multilingual,
   enterprise-grade with NVIDIA stack.
   Weaknesses: Higher RAM requirement than other SLMs despite active-parameter efficiency.

4. Qwen 3 (0.6B to 32B) — 2025/2026
   Apache 2.0 license. Available from tiny (0.6B smartphone) to mid-size (32B workstation).
   Excellent multilingual, especially Asian languages.
   Strengths: Broadest size range, free commercial use, multilingual, fits from phone to server.
   Weaknesses: Community smaller than Microsoft/Google SLMs.

5. Llama 3.2 (1B to 11B) — Meta
   Multimodal (vision) at 11B. Runs on smartphones and edge devices. Apache 2.0.
   Strengths: Smallest viable vision model, Meta ecosystem, fine-tunable, on-device deployment.
   Weaknesses: Limited reasoning vs larger models.

Key SLM enterprise use cases (2026): factory floor visual inspection (Gemma 3 4B on NVIDIA Jetson),
healthcare on-premises data processing, on-device financial advisory (privacy), regulated industries
requiring local inference, and 75% AI cost reduction vs cloud API (Iterathon, 2026).

---

REPORT REQUIREMENTS:
- 9-section executive report structure (Executive Summary through Recommendations)
- Audience: senior banking executives and technology leaders (non-technical)
- Include at minimum 6 named banking institution case studies spread across relevant sections
  (JPMorgan Chase, Goldman Sachs, HSBC, DBS Bank, Standard Chartered, Morgan Stanley,
  Bank of America, Citigroup, UOB, OCBC — choose the most relevant)
- Attribute all statistics with source and year using [n] inline citations
- Use banking analogies to explain technical concepts throughout
- Further Reading section: 3 authoritative readings + 2 videos with live hyperlinks
- References section: 15-20 cited sources
- Word-document-ready markdown formatting (## for H2, ### for H3, bold, bullets, numbered lists)
- Do NOT include diagram placeholders (Word builder handles figures separately)
"""


async def main():
    spec = importlib.util.spec_from_file_location("Leary", AGENT_TEAM / "leary.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    leary = mod.Leary()

    print("Leary is writing the report — this may take several minutes...")
    result = await leary.run(TASK)

    out = PROJECT_ROOT / "Owner's Inbox" / "result_ai_landscape_report_leary.json"
    out.write_text(json.dumps({"result": result}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE — saved to: {out}")
    print(f"\nPreview (first 500 chars):\n{result[:500]}")


if __name__ == "__main__":
    asyncio.run(main())
