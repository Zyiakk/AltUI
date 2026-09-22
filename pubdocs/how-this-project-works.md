# How this project works

The pages in this folder describe techniques. This one describes the habits around them: how the repository is laid out, how a change gets from an idea to a release, and how the context behind a decision is kept so that it survives the session it was made in.

It is here because a mod of this size is mostly not a programming problem. The hard part is that six weeks later nobody remembers why a value is 0.6, whether that odd-looking workaround is still needed, or which of two plausible approaches was already tried and abandoned. Everything below exists to answer those questions without archaeology.

## The repository

| Folder | What lives there |
|---|---|
| `assets/gen/` | the generators: Python that describes every asset of the mod |
| `assets/*.json` | what they produce – the description each asset is built from |
| `bpgen/` | the editor plugin that turns those descriptions into assets |
| `scripts/` | the tooling: pak readers and writers, asset readers, the converters, the build chain |
| `tests/unit/` | tests that need neither engine nor game – the ones that only look at generated data finish in under a second |
| `tests/editor/` | tests that run inside an editor session, for things only the engine can answer |
| `uassets/`, `pubdocs/` | what is handed to other modders |
| `versions/<version>/` | exactly the files that were released, with their checksums |
| `build.sh`, `config.example.sh` | the whole chain in one script, and the paths it needs |

Two of those deserve a note.

**`versions/<version>/` is a copy, not a link.** Every release keeps the artefacts that actually went out, because a rebuild does not reproduce them: cooked packages carry identifiers that are drawn fresh on every save, so the same source produces files that differ byte-wise from the ones users have. Keeping the originals is the only way to compare what someone installed against what the repository says that version was.

**`scripts/` has nothing to install.** Plain Python 3, no third-party packages. It makes the tools shippable to players as a single file, and it means a script written a year ago still runs.

## From idea to release

The order is always the same, and the first two steps produce documents rather than code:

1. **A design note.** What is the problem, what did looking into it turn up, which approaches exist, which one was chosen and why. Crucially it also records what was *rejected*, so the same dead end is not explored twice.
2. **A plan.** The design broken into steps small enough that each one ends with something testable, with the exact files and the exact commands. A plan that says "add validation" is not a plan.
3. **Implementation**, one step at a time, with a commit per step.
4. **Tests.** Anything a test can catch must not be caught by playing the game. Unit tests for everything that can be decided from data alone, editor tests for the rest.
5. **An in-game checklist.** The things only a human can see – does it look right, does it feel right, does the camera end up somewhere silly – as a numbered list to walk through before a release. Checked off, with the failures written down.
6. **A release folder**, the changelog entry, and the texts for the places the mod is published.

These notes, plans and checklists live in the working repository rather than in the public one: they are full of half-finished thoughts, dead ends and local details, and the useful parts of them end up here, in the changelog, or in the code as comments.

## Public and private

The public repository is a snapshot of the working one, not the same thing. What stays behind: notes about the game's own data, tooling that repackages other people's mods, local paths, anything unreleased. What comes across is complete enough to build the mod from source.

That split has two rules attached that are worth stealing:

* **Public texts must stand on their own.** No "as discussed", no references to a conversation, an issue or a commit. A reader arriving from a mod page has none of that context.
* **Describe the present.** No promises about what a future version will do. Descriptions of the current state age gracefully; promises do not.

## Keeping the context

Much of the work here is done with an AI coding assistant, which makes the memory problem sharper than usual: every session starts without any recollection of the last one. The answer is the same as it would be for a human returning after a long break – write things down – but it has to be organised enough to be found again.

Three layers do that:

* **The repository itself** for anything that is true of the code: what a value means, why a workaround is there, what a test guards. These belong in comments and commit messages, where they cannot drift away from the thing they describe.
* **The design notes and plans** for the reasoning behind a change: the findings, the alternatives, the decision.
* **A small memory store outside the repository** for what neither of those covers: standing constraints, working preferences, corrections, the state of things that live outside the code – what has been published where, what is waiting for an answer.

That last store is deliberately plain: one file per fact, with a name, a one-line description and a type – who the work is for, how to work, what the project is doing, where things live. One index file lists them, and files reference each other by name. The rules that keep it useful are mostly rules about what *not* to write: nothing the repository already records, nothing that only mattered for one afternoon, and no duplicates – an existing note gets corrected rather than doubled.

None of this is clever. It is the same discipline that makes a codebase survivable by a team, applied to a small project where the "team" is you-in-six-weeks and a program that never remembers anything. The payoff is that a decision taken today can be reviewed tomorrow on its reasons rather than re-argued from scratch, and that the answer to "why is this like this?" is written down somewhere rather than reconstructed.

## Stealing from it

If you take one thing, take the design note: half a page before you start, listing what you found and what you decided against. It costs the least of these habits to adopt.

If you take a second, take the checklist for what only the game can tell you. Everything else can be automated; that part cannot, and doing it from memory means shipping the same mistake twice.
