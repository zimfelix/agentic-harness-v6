# Confirmed change — correcting an active deal's title

Continue this already-built CRM from persisted project files, without relying on a previous conversation. Complete any remaining authorized checks first. Then implement ONLY this new behavior, updating the existing contract and tests; retain all other requirements.

PATCH /deals/{id} now accepts `version` plus `title`, `status`, or both; at least one of title/status is required. Keep rejecting unknown fields and invalid versions/types. Title must be nonblank text. Title edits are permitted only while the CURRENT deal is new or qualified; won/lost are immutable. A title-only edit increments version exactly once and emits one `deal.updated` audit event. A combined title+valid status transition atomically applies both, increments once and emits one existing `deal.transitioned` event, not two. Invalid/stale/unauthorized requests change neither title/status/version nor audit. Existing status-only transitions remain unchanged. Existing tenant/role restrictions apply.

No new UI, provider, dependency or deferred feature. Ordinary implementation decisions remain delegated. Run your own change tests and affected original regression; report actual results and update the single active work record for a fresh session.
