# Optional database audit examples

Read only for database-related editorial audits. These inherited examples are
investigation prompts, not mandatory book-production gates or universal product
claims. Verify the actual implementation and version before publishing a note.

- Transaction start: distinguish client boundaries, engine registration,
  snapshots and ID allocation; compare a first read with a first write.
- Lock advice: check global acquisition order across code paths before endorsing
  locally shorter hold time; test deadlock counterexamples.
- Feature eligibility: separate configuration enablement/capacity from rules
  for inserts, uniqueness checks and cleanup; check each relevant version.
- Diagnostics: distinguish estimates, executed rows, filtering and server/engine
  scopes. Establish whether collecting an actual plan executes the statement.
- SQL rewrites: test ties, NULL, collation, duplicates, deterministic ordering,
  LIMIT/OFFSET and inner/outer ordering. Separate language guarantees from
  optimizer transformations; sample-data agreement does not prove equivalence.
- Maintenance: check object/global precedence, synchronous/asynchronous work,
  sampling, locks, logging and replication. Determine whether nodes sample
  independently before promising consistent estimates.

Keep new product-specific details in the book's audit records, not the general
skill's mandatory workflow.
