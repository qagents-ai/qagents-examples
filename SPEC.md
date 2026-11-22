# QAgents use-case collection

## Objective

Inspect concrete GitHub agent examples and publish a separate repository
of original implementations using QAgents. Preserve useful behaviors and document
where local fixtures replace an upstream network service.

## Deliverables

- An attributable source catalog covering multiple upstream ecosystems and many
  application domains, pinned to inspected code commits and SHA-256 content hashes.
- Eighteen distinct examples: citation research, customer support, invoice audit,
  SQL analytics, lead qualification, meeting actions, flight planning, recruitment
  review, expense review, inventory procurement, code security review, Greek/English
  localization, document question answering, editorial teams, KA220 proposal
  drafting, incident-team messaging, scoped preferences and durable company analysis.
- A common CLI for listing, running one example, running all offline, alternate
  JSON input and configured OpenAI-compatible, Anthropic and QCloud models.
- Real QAgents tool execution, typed outputs, explicit approvals, independent
  verifiers, persistent state and team/workflow examples. Fixture replay must never
  be advertised as evidence of model intelligence or a live provider result.
- Runnable documentation, example inputs, expected outputs, tests, package checks,
  dependency revision recording and GitHub source publication on main.

## Execution contract

Each run creates a new output directory without replacing an earlier run.
Examples use finite turn, token, tool and time budgets. The application owns
identities, fixture access and artifact paths. The model cannot select another
user's memory scope or arbitrary host filesystem paths. Consequential actions
pause for approval; offline golden demonstrations explicitly simulate approval,
while live runs require a person or a supplied decline/approve decision.

Independent checks validate arithmetic, citations, quoted evidence, constraints,
durability or persisted destination state as appropriate. Incomplete runs and
verification failures produce a nonzero CLI exit rather than successful reports.

No production service deployment, real payment, email delivery, third-party
account setup or live-provider quality claim is part of this collection.
