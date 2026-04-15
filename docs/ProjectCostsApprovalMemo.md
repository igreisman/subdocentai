# Project Cost Approval Memo

## Key Risk

The primary technical and budget risk for Pampanito deployment is not the app server or AI usage. It is delivering full-vessel bring-your-own-device connectivity inside the submarine.

Full-vessel BYOD coverage is a launch requirement. That means network engineering is a required launch cost, not an optional enhancement. If visitor phones cannot stay connected across the full required route, the deployment should be treated as not ready for launch.

## Budget Summary

### Recurring Costs

- Cloud hosting: `7` to `25` dollars per month
- Domain renewals: `25` to `50` dollars per year if both domains are retained
- Groq transcription: variable usage cost only if voice transcription is enabled
- Email delivery: `0` incremental dollars if an existing account is used, otherwise a small provider-dependent monthly cost

### One-Time Pampanito Costs

- Local host machine: `0` to `1,500` dollars depending on whether existing hardware is reused
- Network hardware and installation: `200` dollars to low thousands, depending on access point count, wired backhaul, cable/power work, mounting, and repeat on-site RF testing
- Certificate trust, device testing, and deployment setup: staff labor

## Approval-Level View

- The software itself is relatively low-cost in its current form.
- The main fixed recurring cost is hosting.
- The main variable operating cost is transcription, and only if it is enabled.
- The main launch cost and main technical uncertainty is the submarine-specific network required to achieve full-vessel BYOD coverage.

## Recommendation

Approve the project with the understanding that:

- Software and hosting costs are modest.
- Network design and validation are the critical launch work.
- Full-vessel BYOD coverage must be proven by real phone testing before launch approval.
