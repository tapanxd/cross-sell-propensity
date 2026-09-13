# Synthetic reference tables

Both live in `data/reference/` and are committed — they are project work, not raw data.
Keys are INTEGER to match `train_cleaned`.

## region_map.csv (53 rows)
`region_code, region_name, zone, area_type`

- Names are GTA municipalities / Toronto areas. Codes were mapped by frequency rank: the most common code (28, 28% of customers) → Toronto Downtown Core; the rarest codes → rural Durham/York.
- `zone` = Toronto / Peel / York / Durham / Halton. Used for drill-down: zone → region.
- `area_type` = urban / suburban / rural. Independent of zone; used for channel-strategy slicing.

## channel_map.csv (155 rows)
`channel_code, channel_name, channel_type`

- `channel_type` has 6 values: Digital, Agent, Partner, Phone, In-person, Mail.
- Only the top 10 codes (92% of rows) were assigned deliberately. The other 145 codes (8% of rows) were assigned round-robin — they are too small individually to matter and will be shown as "Other" in the dashboard.

Top-10 rationale (synthetic, but chosen to look like a real insurer's mix):

| code | share | type | why |
|---|---|---|---|
| 152 | 35% | Digital | the largest channel is usually the cheapest one — web/aggregator |
| 26 | 21% | Agent | second-largest is the traditional tied-agent force |
| 124 | 19% | Partner | bank partnerships are a major insurance channel |
| 160 | 6% | Phone | outbound call centre |
| 156 | 3% | Agent | independent broker network |
| 122 | 3% | Phone | inbound helpline |
| 157 | 2% | In-person | branch walk-in |
| 154 | 2% | Partner | car dealerships — natural for vehicle insurance |
| 151 | 1% | Digital | SMS / WhatsApp |
| 163 | 1% | Mail | direct mail |

Nothing in either table is derived from `Response`.
