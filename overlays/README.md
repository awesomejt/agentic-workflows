# Private Overlays

Tracked configuration should be reusable and contain no secret values. Content
that is personal enough to need separate access control—named Hermes identities,
private relationship context, or non-shareable workflows—belongs in an overlay
repository or the ignored `overlays/private/` directory.

A private overlay may mirror canonical paths such as:

```text
hermes/profiles.yaml
common/personas/<name>.md
targets/<private-target>.yaml
environments/<private-environment>.yaml
```

It still must use secret references rather than values. Deployment tooling
should accept overlay paths explicitly, validate the merged result, and record
overlay provenance without copying private content into its state manifest.

The current public bundle records the unresolved `personal-profiles` overlay in
`hermes/profiles.yaml`. Do not migrate personally identifying profiles until the
repository owner chooses whether they belong here or in a separately controlled
repository.
