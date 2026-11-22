# Run the same applications with a configured model

Offline mode is the default. Live provider runs require an explicit provider and
model ID. Select a model that supports tool calling and JSON output in prompted
mode. These adapters use the public QAgents interfaces. No upstream agent
framework is installed.

## OpenAI and compatible endpoints

Set `OPENAI_API_KEY`, a model ID passed through `--model`, and the model's actual
USD prices per million input and output tokens. In PowerShell:

```powershell
$env:OPENAI_API_KEY = '<your key>'
$env:QAGENTS_INPUT_USD_PER_MILLION = '<actual input price as a number>'
$env:QAGENTS_OUTPUT_USD_PER_MILLION = '<actual output price as a number>'
uv run --locked qagents-examples run flight_planner --provider openai --model '<model-id>' --output .runs/provider-flight
```

Replace all placeholders before running. Prices must be finite and nonnegative;
zero is an explicit choice for an unbilled local inference endpoint. Estimates
cover the supplied token prices, not infrastructure costs or every possible
provider billing component. No model/pricing value is silently guessed.

`OPENAI_BASE_URL` defaults to `https://api.openai.com/v1`. Set it to your authorized
OpenAI-compatible service, for example `http://127.0.0.1:8000/v1`. Use the provider's
required key. The official OpenAI endpoint defaults to `max_completion_tokens`;
other endpoints default to `max_tokens`. Override with `OPENAI_MAX_TOKENS_PARAM`
when your server requires the other field.

The native adapter is tested with a local HTTPX transport, including streaming
tool calls, follow-up tool results, token accounting, explicit pricing and the
token-limit request field. This does not establish compatibility with every
hosted model or a live-provider quality score.

## Anthropic

```console
uv sync --locked --extra dev --extra anthropic
uv run --locked --extra anthropic qagents-examples run citation_research --provider anthropic --model <model-id> --output .runs/anthropic-research
```

Set `ANTHROPIC_API_KEY` in the environment. QAgents' Anthropic adapter supplies
the native Messages API integration and known pricing. A model absent from the
pricing table may stop at the dollar guard when its cost is unknown. Check the
[runtime's provider guide](https://github.com/qagents-ai/qagents/blob/db4813c15b4b6c6efa180a02df157ca115329d12/docs/providers.md).

## QCloud

Install the QCloud SDK as documented by the
[runtime](https://github.com/qagents-ai/qagents/blob/db4813c15b4b6c6efa180a02df157ca115329d12/README.md#providers),
then set `QCLOUD_API_KEY` and select a tool-capable catalog model. If the SDK was
installed manually into the environment, preserve it for this run:

```console
uv run --no-sync qagents-examples run citation_research --provider qcloud --model <catalog-model-id> --output .runs/qcloud-research
```

QCloud's catalog supplies capabilities and prices. Its SDK is a separate prerequisite
and is not in this collection's default environment or lockfile. No QCloud or
Anthropic service call was made during the recorded verification.

## Budgets, approvals and artifacts

Each root run has at most 12 model turns, 16,000 total tokens, 16 tool calls, a
90-second execution deadline and a USD 0.50 reported-cost guard. Child agents
share their parent's remaining budget. Separate workflow/session runs have
separate budgets. Requests ask for at most 4,000 output tokens. A provider that
omits usage or known pricing causes the dollar guard to stop the run. It does
not receive a fabricated zero cost. Usage limits use reported responses and do
not guarantee an exact maximum final invoice.

Live action tools prompt on stderr for approval. Answer `y` to approve or press
Enter to decline. `--approval approve` and `--approval decline` supply an explicit
operator decision for the whole demonstration. The model cannot grant approval.
Refusal paths are verified against the local destination database.

Output directories must be new. Reports and SQLite journals can contain task
data. `.runs/` is ignored by Git. Keep credentials in environment variables.
The CLI never copies environment variables into reports and redacts provider
keys from validation errors. Provider exceptions are reported by class.
