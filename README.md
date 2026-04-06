# AstrBot Android Plugin Market

AstrBot Android Plugin Market is the central index repository for Android Native plugins.

This repository is an index only:

- It does not store plugin source code.
- It does not store plugin zip packages.
- Every plugin must live in its own independent repository.
- This repository only maintains the market catalog consumed by the Android client.

## How It Works

1. Each plugin author maintains an independent GitHub repository.
2. The plugin author publishes a plugin zip in that repository, usually through GitHub Releases.
3. The plugin author submits a catalog entry update to this repository.
4. The Android client fetches this repository's `catalog.json`.
5. The market page shows plugins from the catalog and installs packages through each plugin's `packageUrl`.

## Distribution

The first-stage distribution model is static:

- `catalog.json` should be published through GitHub Raw or GitHub Pages.
- Plugin packages should be published through each plugin repository's GitHub Releases.

The Android client should fetch a direct `catalog.json` URL. It should not use:

- a GitHub repository homepage
- a GitHub Release page
- a GitHub `blob` page

## Current Files

- `catalog.json`: the live market index
- `catalog.schema.json`: reference schema for catalog maintenance
- `CONTRIBUTING.md`: how plugin authors add or update entries

## Before Publishing

Before the client uses this repository, replace the placeholder values in `catalog.json`:

- `sourceId`
- `title`
- `catalogUrl`

`catalogUrl` must be the final direct URL that returns the raw JSON file.
