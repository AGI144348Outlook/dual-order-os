# Shared workspace — Group Canvas

**Problem:** let a person and AI tools create and update persistent notes, quizzes and other widgets in one workspace.

**Contribution:** Timothy's product direction and iterative requirements; AI-assisted implementation, testing and documentation. This is an independent portfolio prototype, not a paid-client case study.

## Small offline demonstration

Use [Group Canvas at the assessed revision](https://github.com/AGI144348Outlook/Group_Canvas/tree/36d1b1a311c55cdf1ebeec3ef7499945f56186e8), Node.js 24 recommended:

```sh
npm start
```

Open `http://127.0.0.1:8787`, create a canvas, use the offline “Make a game” action, move/resize a widget, then reload. Show restored state. The offline companion follows fixed rules and must be described that way.

This basic demo needs no model key. Provider configuration is a separate, potentially billable path. Do not enter private records or operator credentials while recording. Do not present room-sharing instructions as a demonstrated remote deployment.

## Relevant skills

Stateful interfaces, command validation, persistence, external-agent tool contracts and scoped permissions. An assessment ran 100 passing tests at this revision, including actual SQLite and mocked provider/Cloudflare-shell tests.

The 3D scene code is present, but this assessment did not visually validate its rendering. Accounts, subscription billing, production operations and load capacity are separate work. A concise widget/persistence recording is a stronger initial claim than presenting every experimental feature at once.
