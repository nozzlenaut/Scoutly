# PriceSift v0.6.17

See `README-v0617.md` for the KEH shadow-feed setup and testing steps.

# PriceSift v0.6.16

This release keeps public marketplace searches inside PriceSift's supported catalog and repairs the price-history admin networking path.

## Public catalog guard

- Public searches now require a confident match to a supported PriceSift catalog product.
- Unsupported text such as a drone query inside Cameras no longer falls through to a raw eBay search.
- The result page explains that the product is not supported yet and shows close catalog suggestions when available.
- No fixed-price or auction provider request is made for an unresolved supported-category query.
- RAM, CPU, camera, GPU, console, and LEGO catalog behavior remains unchanged for valid products.

## Price admin repair

- `/admin/prices` now loads its overview and collector actions through same-origin Vercel route handlers.
- Vercel performs the server-to-server request to Railway, matching the networking pattern used by the working admin dashboard.
- The browser no longer needs direct access to the Railway API URL.
- Detailed proxy/backend error text is shown if loading still fails.
- `API_URL` may be set in Vercel as a server-only backend URL; the proxy falls back to `NEXT_PUBLIC_API_URL` when it is absent.

## Deployment

Backend/Railway:

- Deploy the backend normally.
- No new required environment variables.

Frontend/Vercel:

- Existing `NEXT_PUBLIC_API_URL` remains supported.
- Recommended: add `API_URL` with the same Railway backend base URL. This value is used only by Vercel server routes.

## Validation

- Backend regression suite includes unsupported fixed-price and auction search guards.
- Production frontend build includes the two Vercel proxy route handlers.
