---
id: B004
title: OpenAI Batch API guide
url: "https://platform.openai.com/docs/guides/batch"
final_url: "https://developers.openai.com/api/docs/guides/batch"
author_org: OpenAI
published: unknown
accessed: "2026-09-26T18:41:22+08:00"
language: en
source_type: primary
credibility: A
conflict_of_interest: none
capture_method: script
completeness: full
original_files: [raw/files/B004-openai-batch-guide.html]
sha256: b7eb6479f4c2399f2aacd04fe49d84e7d12202ac0031f34123dd58aae3a752b8
research_line: B
subquestions: [Q4]
supersedes: null
archive_url: null
access_note: 正常
rights_note: none
---

# OpenAI Batch API guide

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
 
  
 
  
 
 
 Cookbook 
 
 Learn how to use the Batch API for async use cases. 
 
 
  (/cookbook/examples/batch_processing) 
 
 
 
  
 
 
 
# Batch API
 
 
Process jobs asynchronously with Batch API.
 
 
 
        Copy Page  
 
 
  
 
 
Learn how to use OpenAI’s Batch API to send asynchronous groups of requests with 50% lower costs, a separate pool of significantly higher rate limits, and a clear 24-hour turnaround time. The service is ideal for processing jobs that don’t require immediate responses. You can also explore the API reference directly here (/api/docs/api-reference/batch).

## Overview

While some uses of the OpenAI Platform require you to send synchronous requests, there are many cases where requests do not need an immediate response or rate limits (/api/docs/guides/rate-limits) prevent you from executing a large number of queries quickly. Batch processing jobs are often helpful in use cases like:

  - Running evaluations

  - Classifying large datasets

  - Embedding content repositories

The Batch API offers a straightforward set of endpoints that allow you to collect a set of requests into a single file, kick off a batch processing job to execute these requests, query for the status of that batch while the underlying requests execute, and eventually retrieve the collected results when the batch is complete.

Compared to using standard endpoints directly, Batch API has:

  - Better cost efficiency: 50% cost discount compared to synchronous APIs

  - Higher rate limits: Substantially more headroom (https://platform.openai.com/settings/organization/limits) compared to the synchronous APIs

  - Fast completion times: Each batch completes within 24 hours (and often more quickly)

## Getting started

### 1. Prepare your batch file

Batches start with a .jsonl file where each line contains the details of an individual request to the API. For now, the available endpoints are:

  - /v1/responses (Responses API (/api/docs/api-reference/responses))

  - /v1/chat/completions (Chat Completions API (/api/docs/api-reference/chat))

  - /v1/embeddings (Embeddings API (/api/docs/api-reference/embeddings))

  - /v1/completions (Completions API (/api/docs/api-reference/completions))

  - /v1/moderations (Moderation guide (/api/docs/guides/moderation))

  - /v1/images/generations (Images API (/api/docs/api-reference/images))

  - /v1/images/edits (Images API (/api/docs/api-reference/images))

For a given input file, the parameters in each line’s body field are the same as the parameters for the underlying endpoint. Each request must include a unique custom_id value, which you can use to reference results after completion. Here’s an example of an input file with 2 requests. Note that each input file can only include requests to a single model.

When targeting /v1/moderations, include an input field in every request body. Batch accepts plain-text inputs and content arrays with text or image inputs using omni-moderation-latest. The Batch worker rejects requests that set stream=true, matching the synchronous moderation endpoint.

{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-3.5-turbo-0125", "messages": [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Hello world!"}],"max_tokens": 1000}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-3.5-turbo-0125", "messages": [{"role": "system", "content": "You are an unhelpful assistant."},{"role": "user", "content": "Hello world!"}],"max_tokens": 1000}}

#### Moderation input examples

Text-only request:

123456789{
 "custom_id": "moderation-text-1",
 "method": "POST",
 "url": "/v1/moderations",
 "body": {
 "model": "omni-moderation-latest",
 "input": "This is a harmless test sentence."
 }
}

Request with text and image input:

1234567891011121314151617181920{
 "custom_id": "moderation-mm-1",
 "method": "POST",
 "url": "/v1/moderations",
 "body": {
 "model": "omni-moderation-latest",
 "input": [
 {
 "type": "text",
 "text": "Describe this image"
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
 }
 }
 ]
 }
}

Prefer referencing remote assets with image_url (instead of base64 blobs) to
keep your .jsonl files well below the 200 MB Batch upload limit,
especially for multimodal Moderations requests.

### 2. Upload your batch input file

Similar to our Fine-tuning API (/api/docs/guides/model-optimization), you must first upload your input file so that you can reference it correctly when kicking off batches. Upload your .jsonl file using the Files API (/api/docs/api-reference/files).

Upload files for Batch API

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
10import fs from "fs";
import OpenAI from "openai";
const openai = new OpenAI();

const file = await openai.files.create({
 file: fs.createReadStream("fixtures/batchinput.jsonl"),
 purpose: "batch",
});

console.log(file);

1
2
3
4
5
6
7
8
9from openai import OpenAI

client = OpenAI()

batch_input_file = client.files.create(
 file=open("batchinput.jsonl", "rb"), purpose="batch"
)

print(batch_input_file)

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
27package main

import (
 "context"
 "fmt"
 "os"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 file, err := os.Open("batchinput.jsonl")
 if err != nil {
 panic(err)
 }
 defer file.Close()

 uploaded, err := client.Files.New(context.Background(), openai.FileNewParams{
 File: file,
 Purpose: openai.FilePurposeBatch,
 })
 if err != nil {
 panic(err)
 }
 fmt.Println(uploaded.ID)
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
16import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.files.FileCreateParams;
import com.openai.models.files.FilePurpose;
import java.nio.file.Path;

var file =
 client
 .files()
 .create(
 FileCreateParams.builder()
 .file(Path.of(System.getenv("OPENAI_EXAMPLE_FILE_PATH")))
 .purpose(FilePurpose.BATCH)
 .build());

System.out.println(file.id());

1
2
3
4
5
6
7require "openai"
require "pathname"

client = OpenAI::Client.new
file = Pathname("batchinput.jsonl")
uploaded = client.files.create(file: file, purpose: :batch)
puts(uploaded.id)

1
2
3
4curl https://api.openai.com/v1/files \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -F purpose="batch" \
 -F file="@batchinput.jsonl"

1
2
3openai files create \
 --file batchinput.jsonl \
 --purpose batch

### 3. Create the batch

Once you’ve successfully uploaded your input file, you can use the input File object’s ID to create a batch. In this case, let’s assume the file ID is file-abc123. For now, the completion window can only be set to 24h. You can also provide custom metadata via an optional metadata parameter.

Create the Batch

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
10import OpenAI from "openai";
const openai = new OpenAI();

const batch = await openai.batches.create({
 input_file_id: "file-abc123",
 endpoint: "/v1/chat/completions",
 completion_window: "24h",
});

console.log(batch);

1
2
3
4
5
6
7batch = client.batches.create(
 input_file_id=batch_input_file.id,
 endpoint="/v1/chat/completions",
 completion_window="24h",
 metadata={"description": "nightly eval job"},
)
print(batch)

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
21package main

import (
 "context"
 "fmt"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 batch, err := client.Batches.New(context.Background(), openai.BatchNewParams{
 InputFileID: "file-abc123",
 Endpoint: openai.BatchNewParamsEndpointV1ChatCompletions,
 CompletionWindow: openai.BatchNewParamsCompletionWindow24h,
 })
 if err != nil {
 panic(err)
 }
 fmt.Println(batch.ID)
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
17import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.batches.BatchCreateParams;

String fileId = "file-abc123";

var batch =
 client
 .batches()
 .create(
 BatchCreateParams.builder()
 .inputFileId(fileId)
 .endpoint(BatchCreateParams.Endpoint.V1_RESPONSES)
 .completionWindow(BatchCreateParams.CompletionWindow._24H)
 .build());

System.out.println(batch.id());

1
2
3
4
5require "openai"

client = OpenAI::Client.new
batch = client.batches.create(input_file_id: "file-abc123", endpoint: "/v1/responses", completion_window: "24h")
puts(batch.id)

1
2
3
4
5
6
7
8curl https://api.openai.com/v1/batches \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "input_file_id": "file-abc123",
 "endpoint": "/v1/chat/completions",
 "completion_window": "24h"
 }'

1
2
3
4openai batches create \
 --input-file-id file-abc123 \
 --endpoint /v1/chat/completions \
 --completion-window 24h

This request will return a Batch object (/api/docs/api-reference/batch/object) with metadata about your batch:

1234567891011121314151617181920212223{
 "id": "batch_abc123",
 "object": "batch",
 "endpoint": "/v1/chat/completions",
 "errors": null,
 "input_file_id": "file-abc123",
 "completion_window": "24h",
 "status": "validating",
 "output_file_id": null,
 "error_file_id": null,
 "created_at": 1714508499,
 "in_progress_at": null,
 "expires_at": 1714536634,
 "completed_at": null,
 "failed_at": null,
 "expired_at": null,
 "request_counts": {
 "total": 0,
 "completed": 0,
 "failed": 0
 },
 "metadata": null
}

### 4. Check the status of a batch

You can check the status of a batch at any time, which will also return a Batch object.

Check the status of a batch

JavaScript

1
2
3
4
5import OpenAI from "openai";
const openai = new OpenAI();

const batch = await openai.batches.retrieve("batch_abc123");
console.log(batch);

1
2batch = client.batches.retrieve(batch.id)
print(batch)

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
17package main

import (
 "context"
 "fmt"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 batch, err := client.Batches.Get(context.Background(), "batch_abc123")
 if err != nil {
 panic(err)
 }
 fmt.Println(batch.Status)
}

1
2
3
4
5
6
7
8import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;

String batchId = "batch_abc123";

var batch = client.batches().retrieve(batchId);

System.out.println(batch.status());

1
2
3
4
5require "openai"

client = OpenAI::Client.new
batch = client.batches.retrieve("batch_abc123")
puts(batch.status)

1
2
3curl https://api.openai.com/v1/batches/batch_abc123 \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json"

1
2openai batches retrieve \
 --batch-id batch_abc123

The status of a given Batch object can be any of the following:

| Status | Description |

| validating | the input file is being validated before the batch can begin |

| failed | the input file has failed the validation process |

| in_progress | the input file was successfully validated and the batch is currently being run |

| finalizing | the batch has completed and the results are being prepared |

| completed | the batch has been completed and the results are ready |

| expired | the batch was not able to be completed within the 24-hour time window |

| cancelling | the batch is being cancelled (may take up to 10 minutes) |

| cancelled | the batch was cancelled |

### 5. Retrieve the results

Once the batch is complete, you can download the output by making a request against the Files API (/api/docs/api-reference/files) via the output_file_id field from the Batch object and writing it to a file on your machine, in this case batch_output.jsonl

Retrieving the batch results

JavaScript

1
2
3
4
5
6
7import OpenAI from "openai";
const openai = new OpenAI();

const fileResponse = await openai.files.content("file-xyz123");
const fileContents = await fileResponse.text();

console.log(fileContents);

1
2
3
4
5
6
7
8
9# Replace the illustrative IDs and URLs below with your own resource values.

from openai import OpenAI

output_file_id = "file_123"
client = OpenAI()

file_response = client.files.content(output_file_id)
print(file_response.text)

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
23package main

import (
 "context"
 "fmt"
 "io"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 response, err := client.Files.Content(context.Background(), "file-xyz123")
 if err != nil {
 panic(err)
 }
 defer response.Body.Close()
 contents, err := io.ReadAll(response.Body)
 if err != nil {
 panic(err)
 }
 fmt.Println(string(contents))
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
14import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.core.http.HttpResponse;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

String fileId = "file-xyz123";

try (HttpResponse content = client.files().content(fileId)) {
 Files.copy(
 content.body(), Path.of("batch_output.jsonl"), StandardCopyOption.REPLACE_EXISTING);
}

1
2
3
4
5require "openai"

client = OpenAI::Client.new
content = client.files.content("file-xyz123")
puts(content.read)

1
2curl https://api.openai.com/v1/files/file-xyz123/content \
 -H "Authorization: Bearer $OPENAI_API_KEY" > batch_output.jsonl

1
2
3openai files content \
 --file-id file-xyz123 \
 --output batch_output.jsonl

The output .jsonl file will have one response line for every successful request line in the input file. Any failed requests in the batch will have their error information written to an error file that can be found via the batch’s error_file_id.

Note that the output line order may not match the input line order.
Instead of relying on order to process your results, use the custom_id field
which will be present in each line of your output file and allow you to map
requests in your input to results in your output.

{"id": "batch_req_123", "custom_id": "request-2", "response": {"status_code": 200, "request_id": "req_123", "body": {"id": "chatcmpl-123", "object": "chat.completion", "created": 1711652795, "model": "gpt-3.5-turbo-0125", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello."}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 22, "completion_tokens": 2, "total_tokens": 24}, "system_fingerprint": "fp_123"}}, "error": null}
{"id": "batch_req_456", "custom_id": "request-1", "response": {"status_code": 200, "request_id": "req_789", "body": {"id": "chatcmpl-abc", "object": "chat.completion", "created": 1711652789, "model": "gpt-3.5-turbo-0125", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello! How can I assist you today?"}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 20, "completion_tokens": 9, "total_tokens": 29}, "system_fingerprint": "fp_3ba"}}, "error": null}

The output file will automatically be deleted 30 days after the batch is complete.

### 6. Cancel a batch

If necessary, you can cancel an ongoing batch. The batch’s status will change to cancelling until in-flight requests are complete (up to 10 minutes), after which the status will change to cancelled.

Cancelling a batch

JavaScript

1
2
3
4
5import OpenAI from "openai";
const openai = new OpenAI();

const batch = await openai.batches.cancel("batch_abc123");
console.log(batch);

1
2
3
4
5
6
7
8# Replace the illustrative IDs and URLs below with your own resource values.

from openai import OpenAI

batch_id = "batch_123"
client = OpenAI()

client.batches.cancel(batch_id)

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
17package main

import (
 "context"
 "fmt"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 batch, err := client.Batches.Cancel(context.Background(), "batch_abc123")
 if err != nil {
 panic(err)
 }
 fmt.Println(batch.Status)
}

1
2
3
4
5
6import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;

String batchId = "batch_abc123";

System.out.println(client.batches().cancel(batchId).status());

1
2
3
4
5require "openai"

client = OpenAI::Client.new
batch = client.batches.cancel("batch_abc123")
puts(batch.status)

1
2
3
4curl https://api.openai.com/v1/batches/batch_abc123/cancel \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -X POST

1
2openai batches cancel \
 --batch-id batch_abc123

### 7. Get a list of all batches

At any time, you can see all your batches. For users with many batches, you can use the limit and after parameters to paginate your results.

Getting a list of all batches

JavaScript

1
2
3
4
5
6
7
8import OpenAI from "openai";
const openai = new OpenAI();

const list = await openai.batches.list();

for await (const batch of list) {
 console.log(batch);
}

1
2
3
4
5from openai import OpenAI

client = OpenAI()

client.batches.list(limit=10)

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
19package main

import (
 "context"
 "fmt"

 "github.com/openai/openai-go/v3"
)

func main() {
 client := openai.NewClient()
 list := client.Batches.ListAutoPaging(context.Background(), openai.BatchListParams{Limit: openai.Int(10)})
 for list.Next() {
 fmt.Println(list.Current().ID)
 }
 if err := list.Err(); err != nil {
 panic(err)
 }
}

1
2
3
4
5
6
7
8
9import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.batches.BatchListParams;

client
 .batches()
 .list(BatchListParams.builder().limit(10).build())
 .autoPager()
 .forEach(batch -> System.out.println(batch.id()));

1
2
3
4
5
6require "openai"

client = OpenAI::Client.new
client.batches.list(limit: 10).auto_paging_each do |batch|
 puts(batch.id)
end

1
2
3curl https://api.openai.com/v1/batches?limit=10 \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json"

1
2openai batches list \
 --limit 10

## Model availability

The Batch API is widely available across most of our models, but not all. Please refer to the model reference docs (/api/docs/models) to ensure the model you’re using supports the Batch API. For GPT-6 Sol and Luna, EU data residency is available only with Standard processing. See data residency eligibility (/api/docs/guides/your-data#which-models-and-features-are-eligible-for-data-residency).

## Rate limits

Batch API rate limits are separate from existing per-model rate limits. The Batch API has three types of rate limits:

  - Per-batch limits: A single batch may include up to 50,000 requests, and a batch input file can be up to 200 MB in size. Note that /v1/embeddings batches are also restricted to a maximum of 50,000 embedding inputs across all requests in the batch.

  - Queued prompt tokens per model: Each model has a maximum number of prompt tokens that can be queued for batch processing. You can find these limits on the Platform Settings page (https://platform.openai.com/settings/organization/limits).

  - Batch creation rate limit: You can create up to 2,000 batches per hour. If you need to submit more requests, increase the number of requests per batch.

The Batch API currently has no output-token limit. Because Batch API rate limits are a new, separate pool, using the Batch API will not consume tokens from your standard per-model rate limits, thereby offering you a convenient way to increase the number of requests and processed tokens you can use when querying our API.

## Batch expiration

Batches that do not complete in time eventually move to an expired state; unfinished requests within that batch are cancelled, and any responses to completed requests are made available via the batch’s output file. You will be charged for tokens consumed from any completed requests.

Expired requests will be written to your error file with the message as shown below. You can use the custom_id to retrieve the request data for expired requests.

{"id": "batch_req_123", "custom_id": "request-3", "response": null, "error": {"code": "batch_expired", "message": "This request could not be executed before the completion window expired."}}
{"id": "batch_req_123", "custom_id": "request-7", "response": null, "error": {"code": "batch_expired", "message": "This request could not be executed before the completion window expired."}}
 
 
 
 
  
 
  
   
 
 Previous 
 
 Prompt caching 
 
  (/api/docs/guides/prompt-caching)  
 
 Next 
 
 Flex processing 
 
   (/api/docs/guides/flex-processing) 
  

 
 
  
 
    
  Ask AI  
  
## 
Docs agent

 
       
  
 

Loading docs agent...
