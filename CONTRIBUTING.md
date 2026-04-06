# Contributing

This repository accepts catalog entry updates for AstrBot Android Native plugins.

## Rules

- Every plugin must have its own independent repository.
- Do not submit plugin source code to this repository.
- Do not submit plugin zip files to this repository.
- Submit only catalog entry updates.

## Plugin Author Checklist

Before you open a PR here, make sure your own plugin repository already has:

1. A valid Android Native plugin package structure.
2. A published zip package that can be downloaded directly.
3. A public repository homepage.
4. A stable version number.

## Required Catalog Fields

Each plugin entry must provide:

- `pluginId`
- `title`
- `author`
- `description`
- `entrySummary`
- `versions`

Each version must provide:

- `version`
- `packageUrl`
- `minHostVersion`

## URL Rules

- `repoUrl` should point to the plugin repository homepage.
- `packageUrl` should point to a direct downloadable zip package.
- Do not use GitHub `blob` pages.
- Do not use GitHub Release HTML pages.
- Prefer `https://github.com/<owner>/<repo>/releases/download/<tag>/<file>.zip`

## Review Notes

Catalog maintainers should verify:

1. The plugin repository exists.
2. The zip package downloads correctly.
3. The package is importable by the Android client.
4. The version information is accurate.
5. The entry uses the expected catalog fields.
