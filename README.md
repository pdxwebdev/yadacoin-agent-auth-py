# yadacoin-agent-auth (Python)

Server-side Python SDK for the [YadaCoin KEL Agent Auth Protocol](https://pdxwebdev.github.io/yadacoin-agent-auth-spec).

Implements protocol version **1.2**.

## Install

```bash
# Core (uses public REST API for KEL lookup — no local node required)
pip install yadacoin-agent-auth[rest]

# With a locally running YadaCoin node
pip install yadacoin-agent-auth[node]
```

## Quick start (Tornado)

```python
import os
from yadacoin_agent_auth import AgentAuthValidator, YadaCoinRestKelProvider, AuthError

validator = AgentAuthValidator(
    challenge_secret=os.environ["YADACOIN_AGENT_SECRET"].encode(),
    kel_provider=YadaCoinRestKelProvider("https://yadacoin.io"),
)

# GET /challenge?public_key=<hex>
class ChallengeHandler(BaseHandler):
    async def get(self):
        public_key = self.get_argument("public_key")
        self.write(validator.make_challenge(public_key))

# POST /action
class ActionHandler(BaseHandler):
    async def post(self):
        body = json.loads(self.request.body)
        try:
            auth = await validator.validate(
                public_key=body["public_key"],
                challenge=body["challenge"],
                signature=body["signature"],
            )
        except AuthError as exc:
            self.set_status(exc.http_status)
            return self.write({"error": str(exc)})

        # auth.scope — normalised from W3C VC 2.0 or legacy flat format
        # auth.address — P2PKH address of the verified agent key
        validator.enforce_scope(auth, services=body.get("services"), dest=body.get("dest"))
        # ... your service logic ...
```

## Credential status modes

VCs issued with `credentialStatus.mode: "rotation"` (default) are one-time-use —
the key is revoked once it appears in the KEL. VCs with `mode: "temporal"` survive
key rotations; the verifier instead checks that the VP is signed with the _current_
active key per the KEL.

See [§5.1 of the spec](https://pdxwebdev.github.io/yadacoin-agent-auth-spec#yadakelstatus)
for full semantics.

## Related

- [JS SDK](https://github.com/pdxwebdev/yadacoin-agent-auth-js) — `@yadacoin/agent-auth`
- [Protocol specification](https://pdxwebdev.github.io/yadacoin-agent-auth-spec)
- [did:yadacoin method spec](https://pdxwebdev.github.io/yadacoin/did-yadacoin-method-spec.html)
- [YadaCoin node](https://github.com/pdxwebdev/yadacoin)

## License

YadaCoin Open Source License (YOSL) v1.1 — Copyright © 2017-2026 Matthew Vogel, Inc.
