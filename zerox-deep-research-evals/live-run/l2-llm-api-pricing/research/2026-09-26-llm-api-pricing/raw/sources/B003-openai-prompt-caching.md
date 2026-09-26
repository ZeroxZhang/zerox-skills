---
id: B003
title: OpenAI Prompt Caching guide
url: "https://platform.openai.com/docs/guides/prompt-caching"
final_url: "https://developers.openai.com/api/docs/guides/prompt-caching"
author_org: OpenAI
published: unknown
accessed: "2026-09-26T18:41:20+08:00"
language: en
source_type: primary
credibility: A
conflict_of_interest: none
capture_method: script
completeness: full
original_files: [raw/files/B003-openai-prompt-caching.html]
sha256: b1399edefa8eccf2c0f3c74e85d22faa5f48d3ec81d7a8a570b2144a38edf920
research_line: B
subquestions: [Q2]
supersedes: null
archive_url: null
access_note: 正常
rights_note: none
---

# OpenAI Prompt Caching guide

For the complete documentation index, see llms.txt (/llms.txt). Markdown versions of documentation pages are available by appending
.md to the page URL.

    
      ChatGPT   (/)  
  Start searching   
 
 
API Dashboard (https://platform.openai.com/login)
 

 
Try ChatGPT (https://chatgpt.com/)
 
 
            
   
  Home  (/) 

  API  (/api/docs) 

  Codex   (https://learn.chatgpt.com/docs) 
 
 
  
 
Docs
 
 Guides, concepts, and product docs for Codex 
 
  (https://learn.chatgpt.com/docs) 
 
Use cases
 
 Example workflows and tasks teams can take on with ChatGPT or Codex 
 
  (https://learn.chatgpt.com/use-cases) 
 
 
 

  Docs  (/codex) 

  Use cases  (/codex/use-cases) 

  Training  (/training) 

  Resources  (/codex/resources) 

  ChatGPT   (/chatgpt) 
 
 
  
 
Plugins
 
 Extend ChatGPT and Codex 
 
  (/plugins) 
 
Workspace Agents
 
 Trigger published ChatGPT workspace agents 
 
  (/workspace-agents) 
 
Commerce
 
 Build commerce flows in ChatGPT 
 
  (/commerce) 
 
Ads
 
 Publish and measure ads in ChatGPT 
 
  (/ads) 
 
 
 

  Resources   (/learn) 
 
 
  
 
Showcase
 
 Demo apps to get inspired 
 
  (/showcase) 
 
Blog
 
 Learnings and experiences from developers 
 
  (/blog) 
 
Cookbook
 
 Notebook examples for building with OpenAI models 
 
  (/cookbook) 
 
Learn
 
 Docs, videos, and demo apps for building with OpenAI 
 
  (/learn) 
 
Community
 
 Programs, meetups, and support for builders 
 
  (/community) 
 
 
 
  
  
   Overview  (/api/docs) Models  (/api/docs/models) Agents  (/api/docs/guides/agents) Tools  (/api/docs/guides/tools) Audio & voice  (/api/docs/guides/audio) Production   (/api/docs/guides/production-best-practices) API reference  (/api/reference/overview)  
 
 

 
 
 
##  Search the API docs 
 
    

Search docs

### Suggested

responses createreasoning_effortrealtimeprompt caching

 
 
 
 
 
 
 
  Primary navigation  
   API  Codex  ChatGPT  Docs  Use cases  Training  Resources  Resources   
     
 
 
 
 
 

Search docs

### Suggested

responses createreasoning_effortrealtimeprompt caching

 
 
 
  Overview  Models  Agents  Tools  Audio & voice  Production  API reference  
 
 

OverviewModelsAgentsToolsAudio & voiceProductionAPI referenceDocsProduction

 
 
 
  
  -   Home  (/api/docs) 
  

 
###  Get started 
  
  -   Quickstart  (/api/docs/quickstart) 

  -   Using GPT-6  (/api/docs/guides/latest-model) 

  -   Key concepts  (/api/docs/concepts) 
  

 
###  Core concepts 
  
  -   Responses API  (/api/docs/guides/migrate-to-responses) 

  -   Conversation state  (/api/docs/guides/conversation-state) 

  -   Background mode  (/api/docs/guides/background) 

  -   Streaming  (/api/docs/guides/streaming-responses) 

  -   WebSocket mode  (/api/docs/guides/websocket-mode) 

  -   Mid-turn steering  (/api/docs/guides/steering) 

  -   Multi-agent  (/api/docs/guides/responses-multi-agent) 

  -   Webhooks  (/api/docs/guides/webhooks) 

  -   File inputs  (/api/docs/guides/file-inputs) 

  -   Compaction  (/api/docs/guides/compaction) 

  -   Counting tokens  (/api/docs/guides/token-counting) 
  

 
###  SDKs and CLI 
  
  -   OpenAI SDK  (/api/docs/libraries) 

  -   OpenAI CLI  (/api/docs/libraries/openai-cli) 
  

 
###  Resources 
  
  -   Changelog  (/api/docs/changelog) 

  -   Deprecations  (/api/docs/deprecations) 

  -   Supported countries  (/api/docs/supported-countries) 

  -   OpenAI Crawlers  (/api/docs/bots) 

  -   Terms and policies   (https://openai.com/policies) 
  

 
###  Legacy APIs 
  
  -    Agent Builder    
    -   Overview  (/api/docs/guides/agent-builder) 

    -   Migration guide  (/api/docs/guides/agent-builder/migrate-from-agent-builder) 

    -   Node reference  (/api/docs/guides/node-reference) 

    -   Safety in building agents  (/api/docs/guides/agent-builder-safety) 
   

  -    Evals    
    -   Getting started  (/api/docs/guides/evaluation-getting-started) 

    -   Working with evals  (/api/docs/guides/evals) 

    -   Prompt optimizer  (/api/docs/guides/prompt-optimizer) 

    -   External models  (/api/docs/guides/external-models) 

    -   Best practices  (/api/docs/guides/evaluation-best-practices) 

    -   Graders  (/api/docs/guides/graders) 
   

  -    Fine-tuning    
    -   Optimization cycle  (/api/docs/guides/model-optimization) 

    -   Supervised fine-tuning  (/api/docs/guides/supervised-fine-tuning) 

    -   Vision fine-tuning  (/api/docs/guides/vision-fine-tuning) 

    -   Direct preference optimization  (/api/docs/guides/direct-preference-optimization) 

    -   Reinforcement fine-tuning  (/api/docs/guides/reinforcement-fine-tuning) 

    -   RFT use cases  (/api/docs/guides/rft-use-cases) 

    -   Best practices  (/api/docs/guides/fine-tuning-best-practices) 
   

  -    Assistants API    
    -   Migration guide  (/api/docs/assistants/migration) 
   
  
 

 
  
  -   Model catalog  (/api/docs/models) 
  

 
###  Choose a model 
  
  -   Pricing  (/api/docs/pricing) 

  -   Model selection  (/api/docs/guides/model-selection) 
  

 
###  Text and code 
  
  -   Text generation  (/api/docs/guides/text) 

  -   Code generation  (/api/docs/guides/code-generation) 

  -   Structured output  (/api/docs/guides/structured-outputs) 
  

 
###  Prompting 
  
  -   Overview  (/api/docs/guides/prompting) 

  -   Prompt engineering  (/api/docs/guides/prompt-engineering) 

  -   Citation formatting  (/api/docs/guides/citation-formatting) 

  -   Migration guide  (/api/docs/guides/prompting/migrate-from-prompt-object) 

  -   Prompt generation  (/api/docs/guides/prompt-generation) 

  -   Frontend prompting  (/api/docs/guides/frontend-prompt) 
  

 
###  Reasoning 
  
  -   Reasoning models  (/api/docs/guides/reasoning) 

  -   Reasoning best practices  (/api/docs/guides/reasoning-best-practices) 
  

 
###  Images 
  
  -     Images and vision  (/api/docs/guides/images-vision)    
    -   Image input cost calculator  (/api/docs/guides/image-cost-calculator) 
   

  -     Image generation  (/api/docs/guides/image-generation)    
    -   Overview  (/api/docs/guides/image-generation) 

    -   Image prompting  (/api/docs/guides/image-prompting) 
   
  

 
###  Realtime and audio 
  
  -   Audio and speech  (/api/docs/guides/audio) 

  -   Getting started  (/api/docs/guides/realtime) 

  -   Voice agents  (/api/docs/guides/voice-agents) 
  

 
###  Specialized models 
  
  -   Deep research  (/api/docs/guides/deep-research) 

  -   Embeddings  (/api/docs/guides/embeddings) 

  -   Moderation  (/api/docs/guides/moderation) 
  
 

 
  
  -   Overview  (/api/docs/guides/agents) 
  

 
###  Agents API 
  
  -   Overview  (/api/docs/guides/agents-api/overview) 

  -   Quickstart  (/api/docs/guides/agents-api/quickstart) 

  -   Architecture  (/api/docs/guides/agents-api/architecture) 

  -   Configuring Agents  (/api/docs/guides/agents-api/configuration) 

  -    Sessions    
    -   Run and continue sessions  (/api/docs/guides/agents-api/sessions) 

    -   Events and items  (/api/docs/guides/agents-api/sessions/events) 

    -   Manage sessions  (/api/docs/guides/agents-api/sessions/manage) 

    -   Webhooks  (/api/docs/guides/agents-api/sessions/webhooks) 
   

  -    Environments and sandboxes    
    -   OpenAI-hosted sandboxes  (/api/docs/guides/agents-api/environments/openai-hosted) 

    -   Self-hosted sandboxes  (/api/docs/guides/agents-api/environments/self-hosted) 

    -   Sandbox lifecycle  (/api/docs/guides/agents-api/environments/lifecycle) 

    -   Sandbox security  (/api/docs/guides/agents-api/environments/security) 

    -   Files and artifacts  (/api/docs/guides/agents-api/environments/files) 
   

  -    Tools and integrations    
    -   Web search  (/api/docs/guides/agents-api/tools/web-search) 

    -   Functions  (/api/docs/guides/agents-api/tools/functions) 

    -   MCP connections  (/api/docs/guides/agents-api/tools/mcp) 

    -   Plugins  (/api/docs/guides/agents-api/tools/plugins) 

    -   Vaults  (/api/docs/guides/agents-api/tools/vaults) 
   

  -   Multi-agent  (/api/docs/guides/agents-api/multi-agent) 

  -   Observability and usage  (/api/docs/guides/agents-api/observability) 

  -   Tracing  (/api/docs/guides/agents-api/tracing) 
  

 
###  Agents SDK 
  
  -   Overview  (/api/docs/guides/agents/sdk) 

  -   Quickstart  (/api/docs/guides/agents/quickstart) 

  -   Agent definitions  (/api/docs/guides/agents/define-agents) 

  -   Models and providers  (/api/docs/guides/agents/models) 

  -   Running agents  (/api/docs/guides/agents/running-agents) 

  -   Sandbox agents  (/api/docs/guides/agents/sandboxes) 

  -   Orchestration  (/api/docs/guides/agents/orchestration) 

  -   Guardrails  (/api/docs/guides/agents/guardrails-approvals) 

  -   Results and state  (/api/docs/guides/agents/results) 

  -   Integrations and observability  (/api/docs/guides/agents/integrations-observability) 

  -   Evaluate agent workflows  (/api/docs/guides/agent-evals) 
  

 
###  ChatKit 
  
  -   Overview  (/api/docs/guides/chatkit) 

  -   Customize  (/api/docs/guides/chatkit-themes) 

  -   Widgets  (/api/docs/guides/chatkit-widgets) 

  -   Actions  (/api/docs/guides/chatkit-actions) 

  -   Advanced integrations  (/api/docs/guides/custom-chatkit) 
  
 

 
  
  -   Overview  (/api/docs/guides/tools) 

  -   Function calling  (/api/docs/guides/function-calling) 
  

 
###  Search and retrieval 
  
  -   Web search  (/api/docs/guides/tools-web-search) 

  -   File search  (/api/docs/guides/tools-file-search) 

  -   Retrieval  (/api/docs/guides/retrieval) 
  

 
###  Connect tools and data 
  
  -   MCP servers  (/api/docs/guides/tools-connectors-mcp) 

  -   Secure MCP Tunnel  (/api/docs/guides/secure-mcp-tunnels) 
  

 
###  Build tool workflows 
  
  -   Skills  (/api/docs/guides/tools-skills) 

  -   Tool search  (/api/docs/guides/tools-tool-search) 

  -   Programmatic tool calling  (/api/docs/guides/tools-programmatic-tool-calling) 

  -   Async tool calling  (/api/docs/guides/async-tool-calling) 
  

 
###  Computer and code 
  
  -   Shell  (/api/docs/guides/tools-shell) 

  -   Computer use  (/api/docs/guides/tools-computer-use) 

  -   Apply Patch  (/api/docs/guides/tools-apply-patch) 

  -   Local shell  (/api/docs/guides/tools-local-shell) 

  -   Code interpreter  (/api/docs/guides/tools-code-interpreter) 
  

 
###  Media 
  
  -   Image generation  (/api/docs/guides/tools-image-generation) 
  
 

 
  
  -   Overview  (/api/docs/guides/audio) 
  

 
###  GPT-Live 
  
  -   Getting started  (/api/docs/guides/live) 

  -   Prompting  (/api/docs/guides/live-prompting) 

  -   Managing sessions  (/api/docs/guides/live-conversations) 

  -   Delegation and tools  (/api/docs/guides/live-delegation) 

  -   Migrate to GPT-Live  (/api/docs/guides/live-migration) 

  -   Partner integrations  (/api/docs/guides/live-partner-integrations) 
  

 
###  Realtime API 
  
  -   Getting started  (/api/docs/guides/realtime) 

  -   Prompting  (/api/docs/guides/voice-prompting) 

  -   Managing conversations  (/api/docs/guides/realtime-conversations) 

  -   Voice activity detection  (/api/docs/guides/realtime-vad) 

  -   Tools and MCP  (/api/docs/guides/realtime-mcp) 
  

 
###  Build with voice 
  
  -   Voice agents  (/api/docs/guides/voice-agents) 

  -   Custom voices  (/api/docs/guides/custom-voices) 

  -   Cost optimization  (/api/docs/guides/voice-latency-cost) 
  

 
###  Connections 
  
  -   WebRTC  (/api/docs/guides/voice-webrtc) 

  -   WebRTC with WARP  (/api/docs/guides/realtime-webrtc-warp) 

  -   WebSockets  (/api/docs/guides/voice-websockets) 

  -   Telephony and SIP  (/api/docs/guides/voice-sip) 

  -   Server-side controls  (/api/docs/guides/voice-server-controls) 
  

 
###  Audio processing 
  
  -   File transcription  (/api/docs/guides/speech-to-text) 

  -   Live transcription  (/api/docs/guides/realtime-transcription) 

  -   Live translation  (/api/docs/guides/realtime-translation) 

  -   Text to speech  (/api/docs/guides/text-to-speech) 

  -   Audio in Chat Completions  (/api/docs/guides/audio-chat-completions) 
  
 

 
 
###  Go live 
  
  -   Production best practices  (/api/docs/guides/production-best-practices) 

  -   Deployment checklist  (/api/docs/guides/deployment-checklist) 
  

 
###  Performance and quality 
  
  -   Latency optimization  (/api/docs/guides/latency-optimization) 

  -   Predicted Outputs  (/api/docs/guides/predicted-outputs) 

  -   Fast mode  (/api/docs/guides/fast-mode) 

  -   Accuracy optimization  (/api/docs/guides/optimizing-llm-accuracy) 
  

 
###  Cost and throughput 
  
  -   Cost optimization  (/api/docs/guides/cost-optimization) 

  -     Prompt caching  (/api/docs/guides/prompt-caching)    
    -   Prompt cache diagnostics  (/api/docs/guides/prompt-caching/diagnostics) 
   

  -   Batch  (/api/docs/guides/batch) 

  -   Flex processing  (/api/docs/guides/flex-processing) 
  

 
###  Safety and governance 
  
  -   Safety best practices  (/api/docs/guides/safety-best-practices) 

  -   Red teaming  (/api/docs/guides/red-teaming) 

  -   Daybreak  (/api/docs/guides/daybreak) 

  -    Safety checks    
    -   Safety classifiers  (/api/docs/guides/safety-checks) 

    -   Cybersecurity checks  (/api/docs/guides/safety-checks/cybersecurity) 

    -   Misalignment monitoring  (/api/docs/guides/safety-checks/misalignment-monitoring) 
   

  -   Under-18 guidance  (/api/docs/guides/safety-checks/under-18-api-guidance) 

  -   CSAM guidance  (/api/docs/guides/csam-guidance) 

  -   Content provenance  (/api/docs/guides/content-provenance) 

  -   Your data  (/api/docs/guides/your-data) 

  -   Private Safety Processing  (/api/docs/guides/private-safety-processing) 

  -   Permissions  (/api/docs/guides/rbac) 
  

 
###  Infrastructure and access 
  
  -     Terraform provider  (/api/docs/guides/terraform)    
    -   Overview  (/api/docs/guides/terraform) 

    -   Projects and access  (/api/docs/guides/terraform/projects-and-access) 

    -   Service accounts  (/api/docs/guides/terraform/service-accounts) 

    -   Rate limits and spend  (/api/docs/guides/terraform/rate-limits-and-spend) 

    -   Model, tool, and data controls  (/api/docs/guides/terraform/project-controls) 

    -   Import and reconciliation  (/api/docs/guides/terraform/import-and-reconcile) 
   

  -   Private Link  (/api/docs/guides/private-link) 

  -   IP allowlist  (/api/docs/guides/ip-allowlist) 

  -   Organization blocking  (/api/docs/guides/organization-blocking) 

  -   Mutual TLS  (/api/docs/guides/mutual-tls) 

  -     Workload identity federation  (/api/docs/guides/workload-identity-federation)    
    -   Federation rules  (/api/docs/guides/workload-identity-federation/federation-rules) 

    -   X.509 certificates  (/api/docs/guides/workload-identity-federation/x509) 

    -   Kubernetes  (/api/docs/guides/workload-identity-federation/kubernetes) 

    -   AWS  (/api/docs/guides/workload-identity-federation/aws) 

    -   Microsoft Azure  (/api/docs/guides/workload-identity-federation/microsoft-azure) 

    -   Google Cloud  (/api/docs/guides/workload-identity-federation/google-cloud) 

    -   Oracle Cloud Infrastructure  (/api/docs/guides/workload-identity-federation/oracle-cloud) 

    -   GitHub Actions  (/api/docs/guides/workload-identity-federation/github-actions) 

    -   SPIFFE  (/api/docs/guides/workload-identity-federation/spiffe) 
   

  -   IP egress ranges  (/api/docs/guides/ip-addresses) 

  -   Amazon Bedrock  (/api/docs/guides/amazon-bedrock) 
  

 
###  Operations 
  
  -   Rate limits  (/api/docs/guides/rate-limits) 

  -   Spend limits  (/api/docs/guides/spend-limits) 

  -   Admin APIs  (/api/docs/guides/admin-apis) 

  -   Error codes  (/api/docs/guides/error-codes) 
  
 

 
 

 
  Docs  (https://learn.chatgpt.com/docs) Use cases  (https://learn.chatgpt.com/use-cases) 
 
 

DocsUse casesDocsDocs

 
 
 

 
 

 
  Plugins  Workspace Agents  Commerce  Ads  
 
 

PluginsWorkspace AgentsCommerceAdsDocsSelect...

 
 
 

 
  
  -   Home  (/plugins) 

  -   Quickstart  (/plugins/quickstart) 
  

 
###  Core concepts 
  
  -   Plugin architecture  (/plugins/concepts/plugins) 

  -   Skills  (/plugins/concepts/skills) 

  -   MCP server  (/plugins/concepts/mcp-server) 
  

 
###  Plan 
  
  -   Brainstorm use cases  (/plugins/plan/use-case) 

  -   Define tools  (/plugins/plan/tools) 
  

 
###  Build 
  
  -   Build an MCP server  (/plugins/build/mcp-server) 

  -   Add UI to your MCP server (optional)  (/plugins/build/chatgpt-ui) 

  -   Authenticate users  (/plugins/build/auth) 

  -   Build skills  (/plugins/build/skills) 

  -   Package your plugin  (/plugins/build/plugins) 

  -   Examples  (/plugins/build/examples) 
  

 
###  Test and publish 
  
  -   Connect and test your plugin  (/plugins/deploy/connect-chatgpt) 

  -   Submit and publish  (/plugins/deploy/submission) 

  -   Submission error reference  (/plugins/deploy/submission-errors) 
  

 
###  Conversion specs 
  
  -   Restaurant reservation spec  (/plugins/guides/restaurant-reservation-conversion-spec) 

  -   Get Quote spec  (/plugins/guides/local-services-request-quote-conversion-spec) 

  -   Product checkout spec  (/plugins/guides/product-checkout-conversion-spec) 
  

 
###  Guides 
  
  -   UI guidelines  (/plugins/concepts/ui-guidelines) 

  -   Optimize Metadata  (/plugins/guides/optimize-metadata) 

  -   Submit a Claude Code plugin  (/plugins/guides/submit-claude-plugin) 

  -   Security & Privacy  (/plugins/guides/security-privacy) 

  -   Troubleshooting  (/plugins/deploy/troubleshooting) 
  

 
###  Resources 
  
  -   Changelog  (/plugins/changelog) 

  -   Plugin guidelines  (/plugins/app-guidelines) 

  -   MCP server review requirements  (/plugins/deploy/app-review) 

  -   Plugin UI reference  (/plugins/reference) 

  -   Checkout API reference  (/plugins/build/monetization) 
  
 

 
  
  -   Home  (/workspace-agents) 
  

 
###  Get started 
  
  -   Trigger workspace agent runs  (/workspace-agents/trigger-runs) 

  -   Authenticate with Workspace Agent access tokens  (/workspace-agents/authentication) 
  
 

 
  
  -   Home  (/commerce) 
  

 
###  Guides 
  
  -   Get started  (/commerce/guides/get-started) 

  -   Best practices  (/commerce/guides/best-practices) 
  

 
###  File Upload 
  
  -   Overview  (/commerce/specs/file-upload/overview) 

  -   Products  (/commerce/specs/file-upload/products) 
  

 
###  API 
  
  -   Overview  (/commerce/specs/api/overview) 

  -   Feeds  (/commerce/specs/api/feeds) 

  -   Products  (/commerce/specs/api/products) 

  -   Promotions  (/commerce/specs/api/promotions) 
  
 

 
  
  -   Ads Overview  (/ads) 
  

 
###  Measurement 
  
  -   Measurement Pixel  (/ads/measurement-pixel) 

  -   Multiple Pixels (Advanced)  (/ads/multiple-pixels) 

  -   Image Tag  (/ads/image-tag) 

  -   Conversions API  (/ads/conversions-api) 

  -   Supported Events  (/ads/supported-events) 
  

 
###  Advertiser API 
  
  -   Overview  (/ads/api-overview) 

  -   API Partner Setup  (/ads/api-partner-setup) 

  -   Campaign Management  (/ads/campaign-management) 

  -   Bidding & Budgets  (/ads/bidding-and-budgets) 

  -   Targeting  (/ads/campaign-targeting) 

  -   Product Feeds  (/ads/product-feeds) 

  -   Conversion Tracking  (/ads/conversion-tracking) 

  -   Reporting  (/ads/reporting) 

  -   Troubleshooting  (/ads/troubleshooting) 

  -   Account Management  (/ads/account-management) 
  

 
###  API Reference 
  
  -   Authentication  (/ads/api-reference/authentication) 

  -   Ad Account  (/ads/api-reference/ad-account) 

  -   Campaigns  (/ads/api-reference/campaigns) 

  -   Ad Groups  (/ads/api-reference/ad-groups) 

  -   Ads  (/ads/api-reference/ads) 

  -   Insights  (/ads/api-reference/insights) 

  -   Files  (/ads/api-reference/files) 

  -   Conversion Setup  (/ads/api-reference/conversion-setup) 
  
 
 

 
  Overview  Features  Configuration  Developers  Security  Administration  Use Cases  Resources  
 
 

OverviewFeaturesConfigurationDevelopersSecurityAdministrationUse CasesResourcesDocsOverview

 
 
 
  
  -   Home  (/codex) 
  

 
###  Get started 
  
  -   Quickstart  (/codex/quickstart) 

  -   Use ChatGPT  (/codex/use-chatgpt) 

  -   Get started with Work  (/codex/get-started-with-work) 

  -   Import from another agent  (/codex/import) 
  

 
###  Foundations 
  
  -   Prompting  (/codex/prompting) 

  -   Model selection  (/codex/model-selection) 

  -   Personalize ChatGPT  (/codex/personalize) 

  -   Skills & Plugins  (/codex/skills-and-plugins) 

  -   Permissions  (/codex/permission-modes) 
  

 
###  Explore 
  
  -   What's new  (/codex/whats-new) 

  -   Models  (/codex/models) 

  -   Pricing  (/codex/pricing) 

  -   Glossary  (/codex/glossary) 
  

 
###  Available on 
  
  -   ChatGPT desktop app  (/codex/app) 

  -   Remote  (/codex/remote) 

  -   ChatGPT on the web  (/codex/web) 

  -   Codex CLI  (/codex/cli) 

  -   Codex IDE extension  (/codex/ide) 

  -   Codex cloud  (/codex/cloud) 
  

 
###  Releases 
  
  -   Changelog  (/codex/changelog) 

  -   Feature Maturity  (/codex/feature-maturity) 

  -   Open Source  (/codex/open-source) 
  
 

 
  
  -   Overview  (/codex/features) 
  

 
###  Workflows 
  
  -   Projects and chats  (/codex/projects) 

  -   Sites  (/codex/sites) 

  -   Build plugins  (/codex/build-plugins) 

  -   Visualizations  (/codex/visualizations) 

  -   Scheduled tasks  (/codex/automations) 

  -   Long-running work  (/codex/long-running-work) 

  -   Notifications  (/codex/notifications) 

  -   Pets  (/codex/pets) 

  -   Codex Micro  (/codex/features/codex-micro) 
  

 
###  Capabilities 
  
  -   Browser  (/codex/browser) 

  -   Computer use  (/codex/computer-use) 

  -   Voice  (/codex/features/voice) 

  -   Plugins  (/codex/plugins) 

  -   Web search  (/codex/web-search) 

  -   Image generation  (/codex/image-generation) 

  -   Image inputs  (/codex/image-inputs) 

  -   Appshots  (/codex/appshots) 

  -   Browser extension  (/codex/chrome-extension) 

  -   Work with files  (/codex/artifacts-viewer) 
  

 
###  Reference 
  
  -   Commands  (/codex/reference/commands) 

  -   Slash commands  (/codex/reference/slash-commands) 

  -   Settings  (/codex/reference/settings) 

  -   Troubleshooting  (/codex/reference/troubleshooting) 
  
 

 
  
  -   Overview  (/codex/configuration) 
  

 
###  Customization 
  
  -   Overview  (/codex/customization/overview) 

  -   Memories  (/codex/customization/memories) 

  -   Computer History  (/codex/customization/computer-history) 
  

 
###  Config file 
  
  -   Config Basics  (/codex/config-file/config-basic) 

  -   Advanced Config  (/codex/config-file/config-advanced) 

  -   Config Reference  (/codex/config-file/config-reference) 

  -   Environment Variables  (/codex/config-file/environment-variables) 

  -   Sample Config  (/codex/config-file/config-sample) 
  

 
###  Agent configuration 
  
  -   AGENTS.md  (/codex/agent-configuration/agents-md) 

  -   Subagents  (/codex/agent-configuration/subagents) 

  -   Speed  (/codex/agent-configuration/speed) 

  -   Rules  (/codex/agent-configuration/rules) 
  

 
###  Extend ChatGPT and Codex 
  
  -   Record & Replay  (/codex/extend/record-and-replay) 

  -   MCP  (/codex/extend/mcp) 
  

 
###  Linux 
  
  -   Desktop app  (/codex/linux/linux-app) 
  

 
###  Windows 
  
  -   Desktop app  (/codex/windows/windows-app) 

  -   Windows sandbox  (/codex/windows/windows-sandbox) 

  -   WSL  (/codex/windows/wsl) 
  
 

 
  
  -   Overview  (/codex/developers) 
  

 
###  Development workflows 
  
  -   Code review  (/codex/code-review) 

  -   Integrated terminal  (/codex/integrated-terminal) 
  

 
###  Extend and automate 
  
  -   Build skills  (/codex/build-skills) 

  -   Site tools (WebMCP)  (/codex/webmcp) 

  -   Hooks  (/codex/hooks) 
  

 
###  Environments 
  
  -   Modes  (/codex/environments/modes) 

  -   Local environments  (/codex/environments/local-environment) 

  -   Cloud environment  (/codex/environments/cloud-environment) 

  -   Git worktrees  (/codex/environments/git-worktrees) 
  

 
###  Build with Codex 
  
  -   Codex SDK  (/codex/codex-sdk) 

  -   App Server  (/codex/app-server) 

  -   GitHub Action  (/codex/github-action) 

  -   Non-interactive mode  (/codex/non-interactive-mode) 
  

 
###  Third-party integrations 
  
  -   GitHub  (/codex/third-party/github) 

  -   GitLab (Beta)  (/codex/third-party/gitlab) 

  -   Slack  (/codex/third-party/slack) 

  -   Linear  (/codex/third-party/linear) 
  

 
###  Reference 
  
  -   CLI customization  (/codex/cli-customization) 

  -   Developer commands  (/codex/developer-commands) 

  -   Developer settings  (/codex/developer-settings) 
  
 

 
  
  -   Overview  (/codex/security-administration) 
  

 
###  Permissions 
  
  -   Profiles  (/codex/permissions) 

  -   Sandboxing  (/codex/sandboxing) 

  -   Auto-review  (/codex/sandboxing/auto-review) 

  -   Agent approvals & security  (/codex/agent-approvals-security) 

  -   Internet access  (/codex/cloud/internet-access) 
  

 
###  Codex Security 
  
  -   Overview  (/codex/security) 

  -    Codex Security plugin    
    -   Quickstart  (/codex/security/plugin) 

    -   Run a security scan  (/codex/security/plugin/scans) 

    -   Run a deep scan  (/codex/security/plugin/deep-scans) 

    -   Review code changes  (/codex/security/plugin/code-changes) 

    -   Use the Security workbench  (/codex/security/plugin/workbench) 

    -   Triage a backlog  (/codex/security/plugin/triage-backlog) 

    -   Fix findings  (/codex/security/plugin/fix-findings) 

    -   Propose security hardening  (/codex/security/plugin/security-hardening) 

    -   Write vulnerability reports  (/codex/security/plugin/vulnerability-reports) 

    -   Export and track findings  (/codex/security/plugin/export-findings) 

    -   Changelog  (/codex/security/plugin/changelog) 
   

  -    Codex Security CLI    
    -   Quickstart  (/codex/security/cli) 

    -   Run bulk scans  (/codex/security/cli/bulk-scans) 

    -   Run scans in CI  (/codex/security/cli/ci) 

    -   GitLab CI/CD  (/codex/security/cli/ci/gitlab) 

    -   Reference  (/codex/security/cli/reference) 

    -   FAQ  (/codex/security/cli/faq) 
   

  -   TypeScript SDK  (/codex/security/sdk) 

  -    Codex Security cloud    
    -   Setup  (/codex/security/setup) 

    -   Security Review  (/codex/security/security-review) 

    -   Improving the threat model  (/codex/security/threat-model) 

    -   FAQ  (/codex/security/faq) 
   
  

 
###  Cyber safety 
  
  -   Models & Trusted Access  (/codex/cyber-safety) 

  -   Recommended configuration  (/codex/cyber-safety/recommended-configuration) 
  
 

 
  
  -   Overview  (/codex/administration) 
  

 
###  Getting started 
  
  -   Admin rollout guide  (/codex/enterprise/admin-setup) 
  

 
###  ChatGPT Work 
  
  -   ChatGPT Work Overview  (/codex/enterprise/chatgpt-work-overview) 

  -   ChatGPT Work cloud security  (/codex/enterprise/chatgpt-work-cloud-security) 

  -   ChatGPT Work local security  (/codex/enterprise/chatgpt-work-local-security) 

  -   ChatGPT Work admin FAQ  (/codex/enterprise/work-admin-faq) 

  -   ChatGPT Work: usage and cost  (/codex/enterprise/chatgpt-work-usage-and-cost) 
  

 
###  Identity and authentication 
  
  -   Authentication overview  (/codex/auth) 

  -   Personal Access Tokens  (/codex/enterprise/access-tokens) 

  -   Service accounts  (/codex/enterprise/service-accounts) 
  

 
###  Workspace access, policy, and models 
  
  -   Groups and provisioning  (/codex/enterprise/groups-and-provisioning) 

  -   User lifecycle management  (/codex/enterprise/user-lifecycle) 

  -   Roles and workspace permissions  (/codex/enterprise/roles-and-workspace-permissions) 

  -   GPTs and Sharing  (/codex/enterprise/gpts-and-sharing) 

  -   Migrate custom GPTs to plugins  (/codex/migrate-custom-gpts) 

  -   Managed configuration  (/codex/enterprise/managed-configuration) 

  -   Prisma AIRS  (/codex/enterprise/prisma-airs) 

  -   HIPAA configuration  (/codex/hipaa-configuration) 

  -   Workspace model availability  (/codex/enterprise/workspace-model-availability) 
  

 
###  Plugin and connector controls 
  
  -   Plugin controls  (/codex/enterprise/apps-and-connectors) 

  -   Plugin management  (/codex/enterprise/plugin-management) 

  -   Skill controls  (/codex/enterprise/skills) 
  

 
###  Usage, governance, and compliance 
  
  -   Governance  (/codex/enterprise/governance) 

  -   Admin plugin  (/codex/enterprise/admin-plugin) 

  -   Workspace analytics  (/codex/enterprise/workspace-analytics) 

  -   Usage Insights  (/codex/enterprise/usage-insights) 

  -   Analytics API  (/codex/enterprise/analytics-api) 

  -   Compliance API and audit events  (/codex/enterprise/compliance-api) 
  

 
###  Deployment and model providers 
  
  -   Manage app updates  (/codex/enterprise/manage-app-updates) 

  -   Windows app deployment  (/codex/enterprise/windows-deployment) 

  -   Remote connections  (/codex/remote-connections) 

  -   Amazon Bedrock  (/codex/amazon-bedrock) 
  
 

 
  
  -   Explore use cases  (/codex/use-cases) 

  -   Collections  (/codex/use-cases/collections) 
  
 

 
  
  -   Home  (/codex/resources) 

  -   Videos  (/codex/videos) 

  -   Showcase   (https://developers.openai.com/showcase) 

  -   OpenAI Academy   (https://openai.com/academy/) 

  -   Online trainings   (https://academy.openai.com/home/events) 
  

 
###  Community 
  
  -   Codex Ambassadors   (https://developers.openai.com/community/codex-ambassadors) 

  -   Codex for Students   (https://developers.openai.com/community/students) 

  -   Codex for Open Source   (https://developers.openai.com/community/codex-for-oss) 

  -   Events   (https://luma.com/codex-community?utm_source=oaidevs) 
  

 
###  Blog 
  
  -   Company blog   (https://openai.com/news/) 

  -   Developer blog   (https://developers.openai.com/blog) 
  
 
 

 
 
  
  -   Explore use cases  (/codex/use-cases) 

  -   Collections  (/codex/use-cases/collections) 
  
 
 

 
 
  
  -   Home  (/codex/resources) 

  -   Videos  (/codex/videos) 

  -   Showcase   (https://developers.openai.com/showcase) 

  -   OpenAI Academy   (https://openai.com/academy/) 

  -   Online trainings   (https://academy.openai.com/home/events) 
  

 
###  Community 
  
  -   Codex Ambassadors   (https://developers.openai.com/community/codex-ambassadors) 

  -   Codex for Students   (https://developers.openai.com/community/students) 

  -   Codex for Open Source   (https://developers.openai.com/community/codex-for-oss) 

  -   Events   (https://luma.com/codex-community?utm_source=oaidevs) 
  

 
###  Blog 
  
  -   Company blog   (https://openai.com/news/) 

  -   Developer blog   (https://developers.openai.com/blog) 
  
 
 

 
  Showcase  (/showcase) Blog  Cookbook  Learn  Community  
 
 

ShowcaseBlogCookbookLearnCommunityDocsSelect...

 
 
 

 

 
  
  -   All posts  (/blog) 
  

 
###  Recent 
  
  -   Bringing my LED display to life with GPT-Live-1 and Codex  (/blog/bringing-my-led-display-to-life) 

  -   Rethinking skills and prompts for GPT-6 Astra  (/blog/rethinking-skills-and-prompts-for-gpt-6-astra) 

  -   Architectural visualization with Astra  (/blog/architectural-visualization-with-astra) 

  -   Building games with Astra  (/blog/how-to-build-games-with-astra) 

  -   Meet Rosalind Workbench: Empowering every scientist to be their own research team  (/blog/rosalind-workbench) 
  

 
###  Topics 
  
  -   General  (/blog/topic/general) 

  -   API  (/blog/topic/api) 

  -   Apps SDK  (/blog/topic/apps-sdk) 

  -   Audio  (/blog/topic/audio) 

  -   Codex  (/blog/topic/codex) 

  -   Life sciences  (/blog/topic/life-sciences) 
  
 

 
  
  -   Home  (/cookbook) 
  

 
###  Topics 
  
  -   Agents  (/cookbook/topic/agents) 

  -   Evals  (/cookbook/topic/evals) 

  -   Multimodal  (/cookbook/topic/multimodal) 

  -   Text  (/cookbook/topic/text) 

  -   Guardrails  (/cookbook/topic/guardrails) 

  -   Optimization  (/cookbook/topic/optimization) 

  -   ChatGPT  (/cookbook/topic/chatgpt) 

  -   Codex  (/cookbook/topic/codex) 

  -   gpt-oss  (/cookbook/topic/gpt-oss) 
  

 
###  Contribute 
  
  -   Cookbook on GitHub   (https://github.com/openai/openai-cookbook) 
  
 

 
  
  -   Home  (/learn) 

  -   OpenAI Developers plugin  (/learn/developers-codex-plugin) 

  -   Docs MCP  (/learn/docs-mcp) 
  

 
###  Categories 
  
  -   Demo apps  (/learn/code) 

  -   Videos  (/learn/videos) 
  

 
###  Topics 
  
  -   Agents  (/learn/agents) 

  -   Audio & Voice  (/learn/audio) 

  -   Computer Use  (/learn/cua) 

  -   Codex  (/learn/codex) 

  -   Evals  (/learn/evals) 

  -   gpt-oss  (/learn/gpt-oss) 

  -   Fine-tuning  (/learn/fine-tuning) 

  -   Image generation  (/learn/imagegen) 

  -   Scaling  (/learn/scaling) 

  -   Tools  (/learn/tools) 

  -   Video generation  (/learn/videogen) 
  
 

 
  
  -   Community  (/community) 
  

 
###  Programs 
  
  -   Codex Ambassadors  (/community/codex-ambassadors) 

  -   Codex for Students  (/community/students) 

  -   Codex for Open Source  (/community/codex-for-oss) 

  -   OpenAI for Startups   (https://openai.com/business/why-openai/startups/) 
  

 
###  Spaces 
  
  -   Events   (https://luma.com/codex-community?utm_source=oaidevs) 

  -   Developer Forum   (https://community.openai.com/) 

  -   Discord   (https://discord.com/invite/openai) 

  -   Reddit   (https://www.reddit.com/r/OpenAI/) 

  -   X   (https://x.com/OpenAIDevs) 
  
 
 
 
 
 
 
 
API Dashboard (https://platform.openai.com/login)
 

 
Try ChatGPT (https://chatgpt.com/)
 
 
 
 
 
 
 
   
 
 
  
 
### Go live
  
  -    Production best practices   (/api/docs/guides/production-best-practices) 

  -    Deployment checklist   (/api/docs/guides/deployment-checklist) 
  

 
### Performance and quality
  
  -    Latency optimization   (/api/docs/guides/latency-optimization) 

  -    Predicted Outputs   (/api/docs/guides/predicted-outputs) 

  -    Fast mode   (/api/docs/guides/fast-mode) 

  -    Accuracy optimization   (/api/docs/guides/optimizing-llm-accuracy) 
  

 
### Cost and throughput
  
  -    Cost optimization   (/api/docs/guides/cost-optimization) 

  -      Prompt caching   (/api/docs/guides/prompt-caching)    
    -    Prompt cache diagnostics   (/api/docs/guides/prompt-caching/diagnostics) 
   

  -    Batch   (/api/docs/guides/batch) 

  -    Flex processing   (/api/docs/guides/flex-processing) 
  

 
### Safety and governance
  
  -    Safety best practices   (/api/docs/guides/safety-best-practices) 

  -    Red teaming   (/api/docs/guides/red-teaming) 

  -    Daybreak   (/api/docs/guides/daybreak) 

  -    Safety checks    
    -    Safety classifiers   (/api/docs/guides/safety-checks) 

    -    Cybersecurity checks   (/api/docs/guides/safety-checks/cybersecurity) 

    -    Misalignment monitoring   (/api/docs/guides/safety-checks/misalignment-monitoring) 
   

  -    Under-18 guidance   (/api/docs/guides/safety-checks/under-18-api-guidance) 

  -    CSAM guidance   (/api/docs/guides/csam-guidance) 

  -    Content provenance   (/api/docs/guides/content-provenance) 

  -    Your data   (/api/docs/guides/your-data) 

  -    Private Safety Processing   (/api/docs/guides/private-safety-processing) 

  -    Permissions   (/api/docs/guides/rbac) 
  

 
### Infrastructure and access
  
  -      Terraform provider   (/api/docs/guides/terraform)    
    -    Overview   (/api/docs/guides/terraform) 

    -    Projects and access   (/api/docs/guides/terraform/projects-and-access) 

    -    Service accounts   (/api/docs/guides/terraform/service-accounts) 

    -    Rate limits and spend   (/api/docs/guides/terraform/rate-limits-and-spend) 

    -    Model, tool, and data controls   (/api/docs/guides/terraform/project-controls) 

    -    Import and reconciliation   (/api/docs/guides/terraform/import-and-reconcile) 
   

  -    Private Link   (/api/docs/guides/private-link) 

  -    IP allowlist   (/api/docs/guides/ip-allowlist) 

  -    Organization blocking   (/api/docs/guides/organization-blocking) 

  -    Mutual TLS   (/api/docs/guides/mutual-tls) 

  -      Workload identity federation   (/api/docs/guides/workload-identity-federation)    
    -    Federation rules   (/api/docs/guides/workload-identity-federation/federation-rules) 

    -    X.509 certificates   (/api/docs/guides/workload-identity-federation/x509) 

    -    Kubernetes   (/api/docs/guides/workload-identity-federation/kubernetes) 

    -    AWS   (/api/docs/guides/workload-identity-federation/aws) 

    -    Microsoft Azure   (/api/docs/guides/workload-identity-federation/microsoft-azure) 

    -    Google Cloud   (/api/docs/guides/workload-identity-federation/google-cloud) 

    -    Oracle Cloud Infrastructure   (/api/docs/guides/workload-identity-federation/oracle-cloud) 

    -    GitHub Actions   (/api/docs/guides/workload-identity-federation/github-actions) 

    -    SPIFFE   (/api/docs/guides/workload-identity-federation/spiffe) 
   

  -    IP egress ranges   (/api/docs/guides/ip-addresses) 

  -    Amazon Bedrock   (/api/docs/guides/amazon-bedrock) 
  

 
### Operations
  
  -    Rate limits   (/api/docs/guides/rate-limits) 

  -    Spend limits   (/api/docs/guides/spend-limits) 

  -    Admin APIs   (/api/docs/guides/admin-apis) 

  -    Error codes   (/api/docs/guides/error-codes) 
  
  
   
 
 
 

 
        Copy Page   
 
 
 
  
 
 
 
# Prompt caching
 
 
Reduce latency and cost with prompt caching.
 
 
 
        Copy Page  
 
 
  
 
 
## Why prompt caching matters

Prompt caching reuses work when requests share the same prompt prefix. This provides three main benefits:

  - Compute-efficient: Avoid recalculating a prompt prefix that the model has already processed.

  - Cheaper input tokens: Pay the model’s reduced cached-input rate for reused tokens, discounted up to 90%.

  - Faster: Reduce the time spent processing input before the response starts.

Prompt caching is enabled by default for supported OpenAI models. Use the Prompt Caching Dashboard (https://platform.openai.com/usage?usage_section=prompt-caching) to monitor cache read hit rates and use the Prompt Cache Diagnostics tool (/api/docs/guides/prompt-caching/diagnostics) to diagnose cache misses and improve cache reuse.

Agents API model calls use the same prompt-caching behavior as the Responses API. Reusing context within a session can preserve a shared prompt prefix, but maintaining a session doesn’t guarantee a cache hit. See Observability and usage (/api/docs/guides/agents-api/observability) for session usage fields and subagent accounting.

Prompt caching pricing varies by model. See API pricing (/api/docs/pricing) for current cached-input and cache-write rates. Cache-write pricing is not an additive fee: input tokens use the uncached-input, cached-input, or cache-write rate.

## What is the prompt cache?

When the model processes input tokens, it must calculate intermediate states, known as key-value (KV) states. These states let the model refer back to earlier tokens while processing new input and generating output tokens.

Prompt caching preserves that state for a reusable prefix: the unchanged tokens at the beginning of a prompt. When a later request has the same prefix and finds a matching cache entry, the model can reuse the saved state instead of processing those tokens again. It still needs to process any new input to generate a new response.

The prompt cache stores key-value (KV) tensors, not the tokens themselves.

Ask ChatGPT for a deeper explanation
 (codex://threads/new?prompt=Explain+how+prompt+caching+works+inside+a+language+model.+Use+the+illustrative+token+sequence+tiny%2C+chips%2C+power%2C+big%2C+ideas+to+explain+attention%2C+key-value+%28KV%29+states%2C+and+how+saved+prefix+state+avoids+repeated+computation.+Distinguish+token-by-token+generation+from+prompt-cache+reuse+across+API+requests.+Keep+the+explanation+approachable+and+note+that+the+token+boundaries+are+illustrative.%0A%0AUse+%5B%40OpenAI+Developers%5D%28plugin%3A%2F%2Fopenai-developers%40openai-curated%29+and+https%3A%2F%2Fdevelopers.openai.com%2Fapi%2Fdocs%2Fguides%2Fprompt-caching.)
 
 
 
 
 
 Step 1 
 
  tiny  chips  
 ↓ 
 Model 
 Computes  
 
 
↓
 Generates    power  
 
 → 
  KV cache  
  
  Reused  
   →  
 
 
 Step 2 
 
  tiny  chips  power  
 ↓ 
 Model 
 Computes  
 
 
↓
 Generates    big  
 
 → 
  KV cache  
  
  Reused  
   →  
 
 
 Step 3 
 
  tiny  chips  power  big  
 ↓ 
 Model 
 Computes  
 
 
↓
 Generates    ideas  
 
 
 
 

OpenAI caches the model’s full rendered context including OpenAI-provided instructions, developer messages (/api/docs/guides/prompt-engineering#message-roles-and-instruction-following), tool definitions (/api/docs/guides/function-calling), and conversation history (/api/docs/guides/conversation-state) containing text (/api/docs/guides/text), images (/api/docs/guides/images-vision), documents (/api/docs/guides/file-inputs), and supported audio (/api/docs/guides/audio).

Cache reuse requires the entire rendered prefix to match. If content or a relevant setting changes before a breakpoint, the prefix after that change cannot match the existing cache entry.

 
 
 
 
 

 
 
 
 
 Hidden system message 
 
 OpenAI-provided instructions 
 

 
 Tools 
 
 Definitions and schemas 
 

 
 Developer message 
 
 Application instructions 
 

 
 Context history 
 
 Conversation messages, tool calls and results, text and multimodal content 
 
 
 
 
 
 

Which settings affect the cached prefix?

Changing a request does not necessarily discard an existing cache entry. What matters is whether a subsequent request has the same prefix and can find an eligible matching breakpoint. The main settings to check are:

| Setting | Impact |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20model%20%3E%20%28schema%29)
| model | A different model can use different weights and caching behavior. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20tools%20%3E%20%28schema%29)
| tools | Changes tool names, descriptions, schemas, ordering, or tool-specific instructions. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20parallel_tool_calls%20%3E%20%28schema%29)
| parallel_tool_calls | Can change instructions about calling multiple tools in one turn. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20text%20%3E%20%28schema%29) (/api/docs/guides/structured-outputs)
| text.format(Structured Outputs) | Adds output-format instructions and the requested schema. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20reasoning%20%3E%20%28schema%29) (#change-reasoning-effort-without-rewriting-the-prefix)
| reasoning.effort | Can change model-side reasoning instructions. On supported models, use aconfiguration updateto change effort while preserving the earlier prefix. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20text%20%3E%20%28schema%29)
| text.verbosity | Can change instructions about response detail. |

 (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20context_management%20%3E%20%28schema%29) (/api/docs/guides/compaction)
| context_management(Compaction) | Replaces earlier conversation content with a compacted context that can prevent reuse from the first changed token onward. |

## How caching works

A cache breakpoint marks the end of a prompt prefix that OpenAI can save to the cache and reuse in later requests. The first request writes an eligible prefix to the cache and subsequent requests look for the longest matching cached prefix available, working backward through eligible breakpoints until they find a match.

A prompt prefix must meet the model’s minimum cacheable token length before it can be cached. Tokens in the OpenAI-provided hidden system content do not count toward this minimum. The minimum cacheable prompt length is 1,024 tokens for GPT-5.6 and later and varies by request settings for earlier models. See the model comparison (#summary-of-model-differences) for details.

After the minimum cacheable token length, you can choose where to place cache breakpoints explicitly, or let OpenAI choose their locations implicitly. The available options depend on the model.

GPT-5.6 and later

For GPT-5.6 and later, cache writes cost 1.25× the standard, uncached input-token rate. It is worth incurring this charge when you know a prefix will be reused, because subsequent reads cost only 0.1× that rate. Writing a prefix once and fully reusing it once costs 1.35× its ordinary input cost, compared with 2× for processing it twice without caching. The savings grow with each additional cache read: across ten requests, one write and nine full reads cost 2.15×, compared with 10× without caching.

Both implicit and explicit caching are supported, where explicit caching gives you more control over which context is written to cache.

Explicit mode: You choose where to place cache breakpoints based on your context management.

  - Set prompt_cache_options.mode to explicit to use only developer-selected breakpoints and mark each desired breakpoint by adding prompt_cache_breakpoint: { "mode": "explicit" } to a supported content block inside an input message.

  - When no explicit breakpoints are placed, the request does not use prompt caching or create cache writes.

  - Explicit-only mode lets you choose where cache writes end. Content after the last selected breakpoint is processed at the uncached input-token rate without a cache-write charge, so you can avoid writing changing content that is unlikely to be reused.

  - Multiple explicit breakpoints can preserve prefixes that change at different rates. Each request can create up to four cache writes.

  - additional_tools input items do not currently accept prompt_cache_breakpoint.

Top-level instructions cannot contain an explicit breakpoint. To mark reusable developer instructions, place them in an input_text block inside a developer message.

Implicit mode: OpenAI chooses breakpoint locations out of the box that work well for most use cases.

  - When prompt_cache_options.mode is implicit, OpenAI places a breakpoint at the end of the latest eligible message. Eligible messages are:

    - user messages

    - the last tool response in a consecutive group of tool responses

    - the last developer message in the initial consecutive group of developer messages.

  - You can add explicit breakpoints without turning off the implicit breakpoint; an implicit breakpoint uses one of the four cache write slots to leave three usable explicit cache write slots.

Earlier models

Only implicit caching is supported. OpenAI places implicit breakpoints at model-dependent intervals (#summary-of-model-differences), counted from the beginning of the hidden OpenAI system message. Only breakpoints at or beyond the minimum cacheable length (counted from the end of the hidden context) are eligible.

Reported cached_tokens is calculated by subtracting the hidden system tokens from the last matched breakpoint, then rounding down to the nearest multiple of 128.

### How prefix matching works

OpenAI walks through only the cache lookup boundaries (explained below) in the incoming request, from longest prefix to shortest, looking for an available matching prefix already cached on the machine.

For GPT-5.6 and later, the cache lookup boundaries in the incoming request are:

  - Explicit-only mode: The first 2 and latest 50 explicit breakpoints.

  - Implicit mode: The first 2 and latest 50 explicit breakpoints, the implicit breakpoint, up to 20 earlier eligible message endings, and the endpoint of the initial consecutive block of developer messages. This lets implicit mode reuse a prefix ending at an earlier message without explicit breakpoints there.

Model generation

Earlier modelsGPT-5.6+

Caching mode

Implicit

Explicit

Implicit breakpoints are placed at the latest eligible user message.

Hidden systemToolsDeveloperContext historyFollow-upCached inputUncached input

Minimum cacheable length (varies by model)

#### Request 1
12,000 input tokens

3,000 tokens(illustrative)

▼⋮⋮⋮

#### Request 2
15,000 input tokens

3,000 tokens(illustrative)

▼⋮⋮⋮⋮

0

2.5k

5k

7.5k

10k

12.5k

15k

17.5k

20k

Input tokens (including illustrative hidden tokens)

15,000

Last matched breakpoint

−

3,000

Hidden tokens

=

12,000

Reported cached tokens

Request parameters and response usage

JavaScriptPython

#### Request 1 · Responses API request

import OpenAI from "openai";

const client = new OpenAI();
const response = await client.responses.create({
 "model": "gpt-5.6",
 "reasoning": {
 "effort": "medium",
 "context": "all_turns"
 },
 "text": { "verbosity": "medium" },
 "input": [
 {
 "role": "developer",
 "content": [
 {
 "type": "input_text",
 "text": "8,000 tokens"
 }
 ]
 },
 {
 "role": "user",
 "content": [
 {
 "type": "input_text",
 "text": "2,000 tokens"
 }
 ]
 }
 ],
 "tools": [
 "Tool definitions, 2,000 tokens"
 ],
 "prompt_cache_key": "shared-workflow-v1",
 "prompt_cache_options": {
 "mode": "implicit",
 "ttl": "30m"
 }
});

#### Request 2 · Responses API request

import OpenAI from "openai";

const client = new OpenAI();
const response = await client.responses.create({
 "model": "gpt-5.6",
 "reasoning": {
 "effort": "medium",
 "context": "all_turns"
 },
 "text": { "verbosity": "medium" },
 "input": [
 {
 "role": "developer",
 "content": [
 {
 "type": "input_text",
 "text": "8,000 tokens"
 }
 ]
 },
 {
 "role": "user",
 "content": [
 {
 "type": "input_text",
 "text": "2,000 tokens"
 }
 ]
 },
 {
 "role": "user",
 "content": [
 {
 "type": "input_text",
 "text": "3,000 tokens"
 }
 ]
 }
 ],
 "tools": [
 "Tool definitions, 2,000 tokens"
 ],
 "prompt_cache_key": "shared-workflow-v1",
 "prompt_cache_options": {
 "mode": "implicit",
 "ttl": "30m"
 }
});

#### Request 1 · Response usage

{
 "usage": {
 "input_tokens": 12000,
 "input_tokens_details": {
 "cached_tokens": 0,
 "cache_write_tokens": 12000
 }
 }
}

#### Request 2 · Response usage

{
 "usage": {
 "input_tokens": 15000,
 "input_tokens_details": {
 "cached_tokens": 12000,
 "cache_write_tokens": 3000
 }
 }
}

## Cache lifetime

Cache entries are not stored indefinitely. A later request can reuse a cached prefix only while its entry remains available, and reusing the prefix refreshes its lifetime without another cache-write charge. The lifetime and retention settings depend on the model (#summary-of-model-differences).

GPT-5.6 and later

Use prompt_cache_options.ttl to control the minimum cache lifetime. The only supported value, 30m, is also the default. A cached prefix remains eligible for reuse for 30 minutes after its most recent write or reuse, though OpenAI may retain it longer.

Earlier models

Use prompt_cache_retention, with supported values that depend on the model:

  - in_memory: Entries typically remain active for around 5 to 10 minutes of inactivity, up to one hour.

  - 24h: Extended retention typically keeps entries available for around 30 minutes and can retain them for up to 24 hours.

Retention defaults and Zero Data Retention

Prompt caching may store encrypted key/value tensors in GPU-local storage as application state. For models that support both in_memory and 24h, the default depends on your organization’s data retention policy:

  - Organizations without Zero Data Retention enabled default to 24h.

  - Organizations with Zero Data Retention enabled default to in_memory.

Verify the available retention policies for your model and organization before selecting a value.

## Cache location

Cached states live on individual machines, where traffic above 15 requests per minute can lead to overflow routing. A request can reuse a cached prefix only if it reaches a machine holding a matching entry that has not expired. Routing requests to the right machine is therefore important for cache reuse.

Caches are not shared across organizations and cannot be reused across regional processing boundaries (/api/docs/guides/your-data#data-residency-controls).

OpenAI handles routing automatically. Within an organization and processing region, routing for a given model depends on:

  - Current machine load and available capacity.

  - A hash of the initial tokens after the hidden OpenAI content, including tool definitions when present. The number of tokens hashed varies by model.

  - A supplied prompt_cache_key (#prompt-cache-keys), which separates cache reuse between groups of requests and helps optimize cache routing on models before GPT-5.6.

Prompt cache keys

On models before GPT-5.6, use a stable prompt_cache_key (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20prompt_cache_key%20%3E%20%28schema%29) for requests that share a reusable prefix to help route related requests to the same cache. For busy groups, aim for about 15 requests per minute in total across all prefixes using each key. Partition higher-volume traffic across multiple keys using a stable, deterministic mapping. Keep related requests on the same prompt_cache_key so they can reuse its cache. Keys influence routing; they do not pin requests to a machine or guarantee a cache hit.

On GPT-5.6 and later, OpenAI handles cache routing automatically; the key is not needed to optimize caching. You can use separate keys to maintain separate cache accounting for customers or users within your application.

Using separate keys can make cached token usage and billing easier to explain for each customer or user. For example, separate keys help prevent cache-hit probing across users: submitting candidate prompts and observing cache hits to learn whether matching content was previously cached. See Separate cache accounting with keys (#separate-prompts-with-cache-keys).

## Summary of model differences

| Behavior | GPT-5.6 and later | GPT-5.5 and GPT-5.5 Pro | Other earlier models |

| Implicit breakpoints | At the end of the latest eligible message. | Spaced at regular 2,048-token intervals. | Spaced at regular, model-dependent intervals. |

| Explicit breakpoints | Supported | Not supported | Not supported |

| prompt_cache_key | Optional for separate cache accounting | Use a stable key to optimize cache routing | Use a stable key to optimize cache routing |

| Minimum cacheable prefix | 1,024 visible input tokens | Varies by request settings | Varies by request settings |

| Cached-token reporting | Exact eligible boundary, excluding hidden tokens | Excludes hidden tokens and rounds down to a multiple of 128 | Excludes hidden tokens and rounds down to a multiple of 128 |

| Cache read charge | 0.1× the uncached input-token rate | Model-dependent cached-input rate | Model-dependent cached-input rate |

| Cache write charge | 1.25× the uncached input-token rate | No additional cache-write charge | No additional cache-write charge |

| Cache lifetime control | prompt_cache_options.ttl | prompt_cache_retention | prompt_cache_retention |

 (#extended-retention-models)
| Supported retention values | "30m" | "24h"only | "in_memory"or"24h"* |

| Cache lifetime | At least 30 minutes after the latest write or reuse | Typically around 30 minutes, up to 24 hours | Typically 5 to 10 minutes inactive forin_memory, or up to 24 hours for24h |

* Extended retention is supported by gpt-5.5, gpt-5.5-pro, gpt-5.4, gpt-5.2, gpt-5.1-codex-max, gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-mini, gpt-5.1-chat-latest, gpt-5, gpt-5-codex, and gpt-4.1.

For models before GPT-5.6, the minimum cacheable input length varies with request settings, including tools, images, output schemas, reasoning effort, and verbosity.

Ask ChatGPT to find the cache minimum for my request
 (codex://threads/new?prompt=Use+%5B%40OpenAI+Developers%5D%28plugin%3A%2F%2Fopenai-developers%40openai-curated%29+and+the+official+prompt-caching+guide+at+https%3A%2F%2Fdevelopers.openai.com%2Fapi%2Fdocs%2Fguides%2Fprompt-caching.%0A%0AHelp+me+find+the+prompt-caching+minimum+for+my+request+configuration+on+a+model+earlier+than+GPT-5.6.%0A%0AUse+this+workflow+to+investigate+the+approximate+minimum+input+length+needed+for+prompt+caching+with+a+developer%E2%80%99s+request+configuration+on+models+earlier+than+GPT-5.6.+Factors+such+as+images%2C+tools%2C+output+schemas%2C+reasoning+effort+or+verbosity+can+affect+the+rendered+input.+Consult+the+current+%5Bprompt-caching+guide%5D%28https%3A%2F%2Fdevelopers.openai.com%2Fapi%2Fdocs%2Fguides%2Fprompt-caching%29+for+model-specific+guidance.+For+GPT-5.6+or+later%2C+return+the+documented+minimum+without+running+this+search.%0A%0A1.+**Confirm+the+experiment.**+Before+preparing+or+running+the+experiment%2C+safely+check+whether+an+API+credential+is+available+without+printing+it+and+ask+whether+I+want+to+reuse+it+or+create+a+new+key.+Do+not+expose+credentials+in+prompts%2C+logs+or+artifacts.+Find+the+actual+request+JSON+or+request-building+code.+Confirm+the+model%2C+inputs+and+settings+with+the+developer.+Explain+the+test+modifications+and+input%2Foutput+costs.+Get+approval+before+making+API+calls+with+their+credentials%2C+including+any+server-executed+tool+effects.+For+Chat+Completions+requests%2C+explain+that+this+workflow+uses+a+Responses-format+version+for+both+token+counting+and+cache-hit+testing%2C+and+ask+whether+the+developer+wants+to+proceed.+Use+that+approved+version+for+the+counts+and+results+reported+throughout+the+workflow%2C+noting+that+the+findings+apply+to+that+version+and+results+may+differ+for+Chat+Completions.%0A%0A2.+**Prepare+faithful+test+copies.**+Leave+the+original+request+and+application+code+unchanged.+Use+the+%5Btoken-counting+API%5D%28https%3A%2F%2Fdevelopers.openai.com%2Fapi%2Fdocs%2Fguides%2Ftoken-counting%29+%28%60POST+%2Fv1%2Fresponses%2Finput_tokens%60%29+to+measure+total+input+tokens+for+the+original+request+and+test+candidates+rather+than+relying+on+local+token+estimates+such+as+%60tiktoken%60.+Shorten+or+pad+ordinary+text+while+preserving+the+model%2C+request+structure%2C+tools%2C+images%2C+files%2C+schemas+and+settings.+Account+for+unintended+cache+reuse+between+candidates+while+keeping+repeated+trials+identical.%0A%0A3.+**Measure+repeated+cache+hits.**+Warm+and+repeat+candidates.+Reject+responses+containing+an+API+error%2C+even+if+their+status+says+%60completed%60.+Before+using+counts+from+either+the+token-counting+API+or+response+usage%2C+require+non-negative+integers+%28not+booleans%29%2C+with+cached+tokens+no+greater+than+input+tokens.+Read+cached-token+usage+from+completed+responses+or+responses+incomplete+solely+because+of+an+output-token+limit%2C+with+valid+usage.+Errors+are+not+cache+misses+and+misses+alone+do+not+prove+the+input+is+below+the+minimum.+Do+not+execute+returned+tool+calls+or+continue+the+conversation.%0A%0A4.+**Narrow+the+result.**+Use+an+efficient+search+to+narrow+the+observed+boundary.+Respect+any+limits+the+developer+specifies.+Stop+when+the+result+is+sufficiently+resolved+or+further+testing+would+not+help.+Do+not+remove+fixed+inputs+to+reach+shorter+lengths.+Recheck+the+boundary+and+report+conflicting+evidence+rather+than+forcing+a+minimum.%0A%0A5.+**Report+the+results+and+offer+further+testing.**+Return+the+original+input-token+count%2C+lowest+observed+repeated-hit+length+or+boundary+range%2C+additional+tokens+needed+to+reach+the+observed+hit+and+uncertainty.+If+no+reliable+result+was+found%2C+say+so.+Observations+do+not+guarantee+future+cache+hits.+Suggest+optional+follow-up+experiments+where+useful+and+ask+whether+the+developer+would+like+to+explore+them.)

## How to optimize prompt caching

Focus on preserving conversation history (#preserve-conversation-history), keeping tool definitions stable (#manage-tools-with-append-only-updates), and choosing where caching occurs. On GPT-5.6 and later, use prompt_cache_options.mode and prompt_cache_breakpoint (#choose-a-caching-mode) to control cache breakpoints. You can also use an optional prompt_cache_key (#separate-prompts-with-cache-keys) if your application needs separate cache accounting for customers. On models before GPT-5.6, use a stable prompt_cache_key to optimize cache routing for requests that share a reusable prefix.

Ask ChatGPT to optimize my prompt caching
 (codex://threads/new?prompt=Use+%5B%40OpenAI+Developers%5D%28plugin%3A%2F%2Fopenai-developers%40openai-curated%29+and+the+official+prompt-caching+guide+at+https%3A%2F%2Fdevelopers.openai.com%2Fapi%2Fdocs%2Fguides%2Fprompt-caching.%0A%0AAnalyze+the+OpenAI+API+usage+in+my+selected+repository+and+suggest+how+to+optimize+prompt+caching.+If+no+repository+is+selected%2C+ask+me+to+choose+one.%0A%0AInspect+request+construction%2C+reusable+prompt+prefixes%2C+conversation+history%2C+tool+definitions%2C+cache+keys%2C+caching+modes%2C+retention%2C+and+any+available+usage+measurements.+Apply+only+guidance+supported+by+the+models+in+use.%0A%0AGive+prioritized+recommendations+with+file+references%2C+tradeoffs%2C+and+a+plan+to+measure+cache+reads%2C+writes%2C+and+input+cost.+Distinguish+measured+results+from+estimates.+Do+not+change+files+or+run+paid+API+requests+until+I+approve.)

Preserve conversation history

In multi-turn applications, reusing the growing conversation history can save more input tokens than caching only the initial instructions. Preserve earlier messages and tool results so later turns can reuse the full shared prefix.

  - Keep the prefix stable. Put stable developer instructions and shared reference material first. If developer instructions or shared material contain timestamps, user-specific content, or other dynamic content, place those at the end rather than the beginning, or move them into later conversation messages.

  - Preserve conversation history. Append new messages rather than rewriting earlier turns. Summarization, compaction (#compaction-can-reduce-cache-reuse), or context truncation can change the prefix and reset cache reuse.

  - Change reasoning effort without rewriting the prefix. On GPT-6 models, append a configuration_update input item to change reasoning effort between responses while keeping request-level reasoning.effort unchanged. This preserves the original prefix for cache reuse. See Change reasoning mid-conversation (/api/docs/guides/reasoning#change-reasoning-mid-conversation) for examples and compatibility limits.

Keep changing content after the breakpoint

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26{
 "model": "gpt-5.6",
 "reasoning": { "effort": "low", "context": "all_turns" },
 "text": { "verbosity": "medium" },
 "prompt_cache_options": { "mode": "explicit" },
 "input": [
 {
 "role": "developer",
 "content": [
 {
 "type": "input_text",
 "text": "Stable instructions and shared reference material...",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 }
 ]
 },
 {
 "role": "developer",
 "content": "Dynamic developer instructions, such as user-specific content and timestamps..."
 },
 {
 "role": "user",
 "content": "The user's current question..."
 }
 ]
}

Change reasoning effort without rewriting the prefix

On supported GPT-6 and later models, append a configuration_update input item to change reasoning effort during a conversation (/api/docs/guides/reasoning?api-mode=responses#change-reasoning-mid-conversation) while preserving the earlier cached prefix. Keep the top-level reasoning.effort at its original value as changing that setting can rewrite instructions in the hidden system instructions.

The latest configuration update controls the reasoning effort for subsequent responses. For example, append this item to the existing input array to switch to high reasoning for the subsequent requests:

Item to append to the input array

1
2
3
4{
 "type": "configuration_update",
 "reasoning": { "effort": "high" }
}

Manage tools with append-only updates

When the tools your application needs vary between requests, change which tools are callable while keeping their definitions stable to preserve reusable prefixes.

  - Keep tools consistent. Preserve tool definitions, ordering, and schemas.

  - Disable tool use for a request. Set tool_choice (/api/docs/guides/function-calling#tool-choice) to "none" instead of removing the tool definitions.

  - Enable only selected tools. Use allowed_tools (/api/docs/guides/function-calling#tool-choice) to restrict which tools are callable while keeping the supplied tools list stable.

  - Load tools when needed. Use tool search (/api/docs/guides/tools-tool-search) with defer_loading: true to reduce input tokens spent on tool definitions in early requests of multi-turn threads. Discovered tools are appended at the end of context, preserving earlier reusable content.

  - Preserve tool-loading history. Use a developer-role additional_tools input item (/api/docs/guides/tools-tool-search#add-tools-at-a-specific-point-in-the-input) to add tools during a thread according to your application’s logic.

Choose a caching mode

On GPT-5.6 and later, two controls determine where cache breakpoints are placed: prompt_cache_options.mode selects implicit or explicit-only caching, and prompt_cache_breakpoint marks a boundary you choose.

  - Place breakpoints automatically. Use implicit caching to place a breakpoint at the end of the latest eligible message. This is convenient for multi-turn threads that append to existing context.

  - Choose breakpoints deliberately. Place explicit markers at the end of stable content. Use explicit-only mode to avoid unnecessary cache writes for changing suffixes.

 

Shared cached prefix for breakpoint 2

Hidden system message

Tools

Developer message · stable prefix

Developer message · variable suffix A

User message

Tool call

Tool result

Assistant message

Developer message · variable suffix B

New user input A

New user input B

Breakpoint 1

Breakpoint 2

Shared cached prefix for breakpoint 1

Unreused suffix: no cache-write charge

New user inputs: no cache-write charge

 

Prewarm the cache

For GPT-5.6 and later, prepare known context ahead of time to reduce time to first token on a subsequent request. For example, an interactive application can prewarm shared instructions, tool definitions, or reference material during startup, before the user asks their first question.

Set prompt_cache_options.prewarm (/api/reference/resources/responses/methods/create#%28resource%29%20responses%20%3E%20%28method%29%20create%20%3E%20%28params%29%200.non_streaming%20%3E%20%28param%29%20prompt_cache_options%20%3E%20%28schema%29%20%3E%20%28property%29%20prewarm) to true in a Responses API request to prepare the prompt cache without generating output. Once it completes, send your actual request with the same prompt prefix and prewarm omitted or set to false.

Prewarm the cache

1
2
3
4
5
6
7
8
9
10
11
12{
 "model": "gpt-5.6",
 "input": [
 {
 "role": "developer",
 "content": "Your app's shared instructions and reference material..."
 }
 ],
 "prompt_cache_options": {
 "prewarm": true
 }
}

Send a follow-up request

1
2
3
4
5
6
7
8
9
10
11
12
13{
 "model": "gpt-5.6",
 "input": [
 {
 "role": "developer",
 "content": "Your app's shared instructions and reference material..."
 },
 {
 "role": "user",
 "content": "The user's question..."
 }
 ]
}

Note: Tokens written to the cache during a prewarm request are billed at the standard cache-write rate.

Separate cache accounting with keys

On GPT-5.6 and later, use prompt_cache_key when you want to maintain separate cache accounting for customers, users, or workspaces within your application. This can make cached token usage and billing easier to explain within each group. The key is optional and is not needed to optimize caching on these models.

  - Choose how to separate cache accounting. Assign a distinct key to each customer or user whose cache accounting should remain separate. For example, support:customer_123 and support:customer_456 maintain separate cache accounting for two customers, even when their requests contain the same prefix.

  - Keep keys stable within each group. Reuse the same key for a customer’s related requests. Generate a separate key for a session or thread only when it needs its own cache accounting.

  - Apply keys consistently. Use the customer’s key across their requests to maintain separate cache accounting. This also helps prevent cache-hit probing across customers.

On models before GPT-5.6, prompt_cache_key is important for optimizing cache hit rates. Use a stable key for requests that share a reusable prefix to help route them to the same cache. For busy groups, follow the guidance for distributing traffic across more keys (#prompt-cache-keys).

Configure cache retention

For earlier models, prefer setting prompt_cache_retention to "24h" for extended retention when the model and your data-retention requirements allow it. See Cache lifetime (#cache-lifetime) for supported settings and defaults.

Escape the minimum cacheable length cost trap

If many requests reuse the same developer instructions and tool definitions, but that shared prefix falls below the model’s minimum cacheable length (#summary-of-model-differences), consider shortening it or expanding it with useful, stable instructions, examples, or reference material. Measure whether cache reuse offsets the additional input tokens and any cache-write charges, and ensure evaluations and behaviour remain stable.

The chart highlights the minimum cacheable length cost trap where short prefix lengths can cost more uncached than expanding to the minimum cacheable token length.
Prompt length and input cost
Minimum cacheable tokensFull cache reads per writeCache-read multiplierCache-write multiplier

0

500

1,000

1,500

2,000

Reusable prefix length (tokens)

Mathematical details

For a cost-only comparison, let MMM be the minimum cacheable length, L<ML < ML<M the original prefix length, rrr the cache-read multiplier, www the cache-write multiplier, and NNN the total number of requests. Assume the expanded prefix is exactly MMM tokens, is written once, and is fully reused on every later request. In uncached-input-token equivalents, keeping the original prefix costs N×LN \times LN×L, while expanding it costs M[w+(N−1)r]M \left[w + (N - 1)r\right]M[w+(N−1)r]. The break-even original length is:
Lbreak-even=M(r+w−rN)L_{\mathrm{break\text{-}even}} = M\left(r + \frac{w-r}{N}\right)Lbreak-even​=M(r+Nw−r​)
Expand when L>Lbreak-evenL > L_{\mathrm{break\text{-}even}}L>Lbreak-even​; keeping the shorter prefix costs less when L<Lbreak-evenL < L_{\mathrm{break\text{-}even}}L<Lbreak-even​. At equality, the costs are the same. The smallest whole-token length for which expansion is cheaper is ⌊Lbreak-even⌋+1\left\lfloor L_{\mathrm{break\text{-}even}} \right\rfloor + 1⌊Lbreak-even​⌋+1. Conversely, shrinking a cacheable prefix below MMM loses caching: under the same assumptions, the shorter uncached prefix must fall below Lbreak-evenL_{\mathrm{break\text{-}even}}Lbreak-even​ to cost less than caching MMM tokens. There is no universal maximum-cost prompt length; the crossover depends on reuse and pricing.

For example, with M=1,024M = 1{,}024M=1,024, r=0.1r = 0.1r=0.1, and w=1.25w = 1.25w=1.25, the crossover is 102.4+1,177.6N102.4 + \frac{1{,}177.6}{N}102.4+N1,177.6​ tokens. Across 10 requests, expanding an original prefix of at least 221 tokens to 1,024 tokens is cheaper. As reuse grows, the crossover approaches 102.4 tokens. A 103-token prefix needs at least 1,963 total requests to benefit; a prefix of 102 tokens or fewer never does under these assumptions. This comparison excludes performance, output tokens, and unchanged request costs. Additional misses, writes, or different model rates change the result.

Monitor cache performance

  - Measure actual cache performance. Track usage.input_tokens_details.cached_tokens, usage.input_tokens_details.cache_write_tokens, input-token counts, latency, and realized cost. Track the token cache-hit rate by dividing total cached tokens by total input tokens, aggregating both counts by user, workspace, day, or another useful grouping.

  - Calculate input cost. Use the token counts in response.usage and the model’s prices per million tokens (/api/docs/pricing).

  - Use the prompt caching dashboard. Monitor cache hit rates in the Prompt Caching Dashboard (https://platform.openai.com/usage?usage_section=prompt-caching).

Calculate input cost

JavaScript

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18function calculateInputCost(
 usage,
 inputPricePerMillion,
 cacheInputMultiplier = 0.1,
 cacheWriteMultiplier = 1.25
) {
 const inputTokens = usage.input_tokens;
 const cachedTokens = usage.input_tokens_details.cached_tokens;
 const cacheWriteTokens = usage.input_tokens_details.cache_write_tokens;
 const ordinaryInputTokens = inputTokens - cachedTokens - cacheWriteTokens;

 const weightedInputTokens =
 ordinaryInputTokens +
 cachedTokens * cacheInputMultiplier +
 cacheWriteTokens * cacheWriteMultiplier;
 const inputCost = (weightedInputTokens * inputPricePerMillion) / 1_000_000;
 return inputCost;
}

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21from openai.types.responses import ResponseUsage

def calculate_input_cost(
 usage: ResponseUsage,
 input_price_per_million: float,
 cache_input_multiplier: float = 0.1,
 cache_write_multiplier: float = 1.25,
) -> float:
 input_tokens = usage.input_tokens
 cached_tokens = usage.input_tokens_details.cached_tokens
 cache_write_tokens = usage.input_tokens_details.cache_write_tokens
 ordinary_input_tokens = input_tokens - cached_tokens - cache_write_tokens

 weighted_input_tokens = (
 ordinary_input_tokens
 + cached_tokens * cache_input_multiplier
 + cache_write_tokens * cache_write_multiplier
 )
 input_cost = weighted_input_tokens * input_price_per_million / 1_000_000
 return input_cost

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17def calculate_input_cost(
 usage,
 input_price_per_million,
 cache_input_multiplier = 0.1,
 cache_write_multiplier = 1.25
)
 input_tokens = usage.input_tokens
 details = usage.input_tokens_details
 cached_tokens = details.cached_tokens
 cache_write_tokens = details.cache_write_tokens
 ordinary_input_tokens = input_tokens - cached_tokens - cache_write_tokens

 weighted_input_tokens = ordinary_input_tokens +
 (cached_tokens * cache_input_multiplier) +
 (cache_write_tokens * cache_write_multiplier)
 (weighted_input_tokens * input_price_per_million) / 1_000_000
end

Migrate prompt caching from an earlier model to GPT-5.6 and later

  - Keep existing stable prefixes.

  - If you use prompt_cache_key, keep existing values to preserve separate cache accounting for customers or users.

  - Replace prompt_cache_retention with prompt_cache_options.ttl.

  - Confirm that reusable prefixes meet the model’s minimum cacheable length (#summary-of-model-differences).

  - If the default breakpoint includes content that changes between requests, add an explicit breakpoint after the stable prefix.

  - Use prompt_cache_options.mode: "explicit" when later content is not worth writing.

  - Compare cached_tokens, cache_write_tokens, latency, and total cost (#monitor-cache-performance) before and after migration.

## Examples

The following examples apply to GPT-5.6 and later models.

Single-turn LLM-as-a-Judge

Consider a single-turn LLM judge that determines whether a completed interaction shows evidence that the user is satisfied after an interaction with a chatbot. Each request uses the same grading rubric and labeled few-shot examples to evaluate a different interaction.

  - Preserving the prefix: The fixed rubric and examples come first. Their combined length is deliberately kept just above the model’s minimum cacheable length (#summary-of-model-differences), using material that helps calibrate the judge. The interaction being evaluated comes last.

  - Caching mode and breakpoint: Explicit-only caching is enabled, with a breakpoint after the fixed rubric and examples. The user–chatbot conversation being evaluated comes after that breakpoint and is not written to the cache, avoiding a cache-write charge for content that is unlikely to be reused.

An example deployment using these principles reported a token cache-hit rate of ~70%. This figure illustrates a possible outcome. Actual cache-hit rate ceilings will depend upon your context and application usage.

Responses API request for a single-turn judge

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22{
 "model": "gpt-5.6-sol",
 "reasoning": { "effort": "medium", "context": "all_turns" },
 "text": { "verbosity": "low" },
 "prompt_cache_options": { "mode": "explicit" },
 "input": [
 {
 "role": "developer",
 "content": [
 {
 "type": "input_text",
 "text": "Judge whether the completed interaction provides evidence that the user is satisfied. Return true or false. Full grading rubric and labeled few-shot examples...",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 }
 ]
 },
 {
 "role": "user",
 "content": "Completed interaction to evaluate..."
 }
 ]
}

Multi-turn agent

Consider a multi-turn agent with long, shared developer instructions and frequent tool calls. Typical usage sees users running multiple sessions with the agent at once, and often forking the threads.

  - Preserving the prefix: Each turn appends new messages, tool calls, and results without rewriting earlier context, so the reusable prefix grows over time.

  - Optional prompt cache key: This example uses agent_123_v1:user_456 to maintain separate cache accounting for user 456, making their cached token usage and billing easier to explain. This also helps prevent cache-hit probing across users. The key stays the same across that user’s sessions and forks with the agent. Omit it if your application does not need this separation.

  - Implicit caching mode: Implicit caching is enabled so the latest eligible user or tool message provides a breakpoint.

  - Explicit breakpoints: A breakpoint is added after each tool result to preserve earlier reusable prefixes and improve cache efficiency of forking.

An example deployment using these principles reported a token cache-hit rate >90%. This figure illustrates a possible outcome. Actual cache-hit rate ceilings will depend upon your context and application usage.

Responses API request for a multi-turn agent

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41{
 "model": "gpt-5.6-sol",
 "reasoning": { "effort": "medium", "context": "all_turns" },
 "text": { "verbosity": "medium" },
 "prompt_cache_key": "agent_123_v1:user_456",
 "prompt_cache_options": { "mode": "implicit" },
 "tools": [
 {
 "type": "function",
 "name": "function_name",
 "description": "Function description",
 "parameters": { "...": "..." }
 }
 ],
 "input": [
 {
 "role": "developer",
 "content": "Stable developer instructions and reference material..."
 },
 { "role": "user", "content": "Can you do...?" },
 {
 "type": "function_call",
 "call_id": "call_123",
 "name": "function_name",
 "arguments": "..."
 },
 {
 "type": "function_call_output",
 "call_id": "call_123",
 "output": [
 {
 "type": "input_text",
 "text": "Tool result...",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 }
 ]
 },
 { "role": "assistant", "content": "Assistant response..." },
 { "role": "user", "content": "Can you also do...?" }
 ]
}

## Gotchas

A shared prefix is not always a cached prefix

This is particularly prevalent when migrating from earlier models to GPT-5.6 or later (#migrate-prompt-caching-from-an-earlier-model-to-gpt-5-6-and-later) due to the change in implicit caching behaviour. If requests share a long prefix but have different suffixes, caching the first complete request implicitly-only does not make the shorter shared prefix reusable.

Consider a static developer message followed by a dynamic user message in each request. This request writes through the dynamic content. Changing that content in the next request does not match the longer cached prefix, and there is no separate breakpoint after the static content.

Without a breakpoint after the static content

1
2
3
4
5
6
7
8
9
10{
 "model": "gpt-5.6-sol",
 "reasoning": { "effort": "medium", "context": "all_turns" },
 "text": { "verbosity": "low" },
 "prompt_cache_options": { "mode": "implicit" },
 "input": [
 { "role": "developer", "content": "Static content..." },
 { "role": "user", "content": "Dynamic content..." }
 ]
}

To remediate, place an explicit breakpoint after the static content in both requests. The first request writes the reusable prefix; the next can reuse it even when the dynamic content changes. This example uses explicit-only mode to avoid writing the dynamic content to cache.

With a breakpoint after the static content

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17{
 "model": "gpt-5.6-sol",
 "reasoning": { "effort": "medium", "context": "all_turns" },
 "text": { "verbosity": "low" },
 "prompt_cache_options": { "mode": "explicit" },
 "input": [
 {
 "role": "developer",
 "content": [{
 "type": "input_text",
 "text": "Static content...",
 "prompt_cache_breakpoint": { "mode": "explicit" }
 }]
 },
 { "role": "user", "content": "Dynamic content..." }
 ]
}

Switching to explicit-only mode can miss an implicit cache write

Suppose request 1 uses implicit mode and caches a prefix through the end of a user message, then follow-up request 2 preserves that prefix but switches to prompt_cache_options.mode: "explicit". As explained in How prefix matching works (#how-prefix-matching-works), request 2 checks only the explicit breakpoints in its own input, so it will not reuse that saved implicit prefix from request 1 (unless one of the explicit breakpoints in request 2 matches the cached endpoint from request 1).

▼ = breakpoint

- Request 1: implicit mode
 [Developer message][User message] ▼

- Request 2: explicit-only mode. Does not hit cache.
 [Developer message][User message][Follow-up] ▼

To reuse the implicit prefix from request 1, place an explicit breakpoint at the matching content-block boundary in request 2, or keep implicit mode enabled so the earlier eligible message ending remains a lookup candidate.

Extending a message can prevent reuse of its cached prefix

Even when both requests use implicit mode, preserving the same initial tokens is not always enough. Suppose request 1 ends with a user message containing Content A, then follow-up request 2 extends that same message to Content A + Content B. The old endpoint after Content A is now inside a message, rather than at its end. As explained in How prefix matching works (#how-prefix-matching-works), without an explicit breakpoint at that boundary, request 2 does not reuse the prefix saved there.

▼ = breakpoint

- Request 1: implicit mode
 [Developer message][User message: Content A] ▼

- Request 2: implicit mode. Cannot reuse the prefix through Content A.
 [Developer message][User message: Content A + Content B] ▼

When the conversation structure permits, preserve the original message and append a new message instead. Otherwise, keep the reusable text in a separate content block and place an explicit breakpoint after it in both requests.

Not all developer messages are automatic implicit mode cache lookup boundaries

In implicit mode, developer messages after the initial consecutive block of developer messages are not automatic cache lookup boundaries. Add an explicit breakpoint at the end of the reusable developer message to preserve that breakpoint in subsequent requests so OpenAI can check for a matching cached prefix.

Minimum cacheable length varies by model

A prefix that qualifies for caching on one model may be too short on another. Check the model comparison (#summary-of-model-differences) and measure the reusable prefix with the model and settings you actually use. When changing models, repeat that check rather than assuming the previous model’s threshold still applies.

Compaction can reduce cache reuse

Compaction (/api/docs/guides/compaction) replaces earlier conversation context with a shorter representation. That can change the prefix, so the first request after compaction may reuse less of the previous cache even when the conversation is logically the same.

Keep reusable instructions and reference material stable where possible, then let subsequent turns build on the compacted context. Compare total input cost before and after compaction: fewer input tokens can still save money even when the cache-hit rate falls.

## Frequently asked questions

Does prompt caching affect output generation?

No. Prompt caching does not change how the model generates output tokens. The model generates a new response using the cached prefix, so identical requests are not guaranteed to produce identical outputs.

Can I manually clear the cache?

No. Manual cache clearing is not currently available. Cache entries expire according to the model’s cache lifetime (#cache-lifetime) and retention settings.

Do cached prompts count toward rate limits?

Yes. Cached input tokens still count toward tokens-per-minute limits. Prompt caching does not change how rate limits (/api/docs/guides/rate-limits) are calculated.

 
 
 
 
  
 
  
   
 
 Previous 
 
 Cost optimization 
 
  (/api/docs/guides/cost-optimization)  
 
 Next 
 
 Batch 
 
   (/api/docs/guides/batch) 
  

 
 
  
 
    
  Ask AI  
  
## 
Docs agent

 
       
  
 

Loading docs agent...
