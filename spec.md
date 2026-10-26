# Product Specification

## Purpose

Arabic Apparel and Stickers is a catalogue and admin-order-request demo for Arabic-personalized HTV products, Be Seen tags, sweaters, and canvas bags.

## Scope

- Browse the eight-item catalogue and see demonstration GBP prices.
- Personalize supported products with validated Arabic text, fonts, sizes, and HTV colours.
- Receive a backend-calculated quote that supports pair offers.
- Submit an admin-review order request to PostgreSQL.

Payments, customer accounts, checkout, fulfillment, and production-accurate rendering are not in scope.

## Product rules

- The fixed Small Be Seen tag displays `Be س` and cannot accept custom text.
- The rectangular tag supports Arabic names up to 24 graphemes.
- The small letter-only tag accepts exactly one Arabic letter plus optional diacritics.
- HTV sizes are 5 x 5, 9 x 4, and 12 x 3 inches.
- Personalized text uses Amiri, Cairo, or Tajawal and is Unicode NFC normalized.
- Text must contain an Arabic letter. Diacritics, spaces, hyphens, Arabic digits, and Western digits are allowed; Latin characters, emoji, and unsupported symbols are rejected.
- The backend validates every submitted option and calculates the price in integer pence.

## Acceptance criteria

1. `GET /api/products` returns the eight current products, their options, and pence prices.
2. `POST /api/products/{id}/price` rejects invalid options and returns a server-calculated total for a positive quantity.
3. Pair offers apply to each complete pair; any odd item uses its standard unit price.
4. The React UI renders RTL Arabic previews, accessible input labels, validation feedback, product prices, and a mobile-friendly customizer.
5. The HTV customizer offers the twenty documented colour choices and the three inch-size options.
6. `POST /api/orders` recalculates the submitted price, saves the order request with status `new`, and never accepts a client price.
7. Alembic migrates an empty PostgreSQL database to the latest revision without manual SQL.
8. Backend and frontend automated tests pass, and the frontend production build succeeds.

## Delivery validation

CI must run backend tests, isolated PostgreSQL integration after Alembic
migrations, frontend tests/build using the committed npm lockfile, and Docker
image builds on pull requests and pushes to main. Deployment preparation must
separate automatic development from manually approved production and document
rollback. Hosting remains unconfigured; no public deployment is authorized by
this specification. See [CI/CD setup](docs/CI_CD.md) for outstanding prerequisites.
