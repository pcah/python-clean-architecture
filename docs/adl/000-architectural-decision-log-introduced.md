# Architectural Decision Log Introduced

* Status: accepted
* Date: 2020-03-10

Technical Story: [#71](https://github.com/pcah/python-clean-architecture/issues/71)

## Context and Problem Statement

An **architecture decision record** (ADR) is a document that captures an important architectural decision made along with its context and consequences.

An **architecture decision** (AD) is a software design choice that addresses a significant requirement.

An **architecture decision log** (ADL) is the collection of all ADRs created and maintained for a particular project (or organization).

An **architecturally-significant requirement** (ASR) is a requirement that has a measurable effect on a software system’s architecture.

All these are within the topic of **architecture knowledge management** (AKM).

## Considered Options

1. Use `docs\adl` in the codebase to store ADRs
2. Use github's wiki to store ADRs
3. Don't write down any documents at all

## Decision Outcome

Chosen option: "1. Use `docs\adl` in the codebase to store ADRs", because it leads to formulate rationale behind each significant decision explicitly and binding them to the actual state of the codebase.

## Pros and Cons of the Options

### 1. Use `docs\adl` in the codebase to store ADRs

* Good, because we're keeping rationale behind each significant decision (ADs) in the library.
* Good, because the decisions are bounded to a concrete state of the code, including the flaws that were an impulse to mark the decision at all.
* Hard, because it takes some effort to state the rationale explicitly.
* A bit harder, because it takes some effort to make code review process around the ADR, while option 2 makes publishing faster and easier.

### 2. Use github's wiki to store ADRs

* All the pros & cons of Option 1.
* Bad, because wiki is a repo on its own, with its own history. You lose the connection between the AD and the state of the code of the project, and therefore the reason you make the decision.
* Good, because posting something on the wiki makes it already published as a web-page:
  * Option 1 (markdown files in the repo) doesn't automatically form a consistent documentation -- no Table of Contents, no search box, no hyper links.
  * You can mitigate the problem with the Option 1 by providing hyper-links on your own. Other solution is making a process that builds documentation from the code and especially the ``docs`` directory and pushes it to the wiki of the project.

### 3. Don't write down any documents at all

* Good, because it's less effort. Obvious.
* Bad, because keeping history of AD is a key knowledge when it comes to evaluate the quality of the project.
* Bad, because it's not easy to find out that there's a AD on some GH issue page. The issue, once closed, is an obscure method to keep knowledge about project's ADs.

## Links

* [_architecture_decision_record_ repository](https://github.com/joelparkerhenderson/architecture_decision_record)
* [Kevin Jalbert, _Start Now: Architecture Decision Records_ (2018)](https://kevinjalbert.com/start-now-architecture-decision-records/)
