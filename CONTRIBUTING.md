# Contributing

Thanks for considering a contribution to this project!

## Making Changes

To allow us to incorporate your changes, please use the following process:

1. Fork this repository to your personal account.
2. Create a [github ticket][new]
3. Create a branch and make your changes, including tests to verify your change
4. If applicable, test the changes locally/in your personal fork. See section below.
5. Submit a pull request to open a discussion about your proposed changes.
6. The maintainers will talk with you about it and decide to merge or request additional changes.

### Tests
Not all code requires tests. Code meant as example, documentation, or experimental in nature does not need to have matching tests. Code meant to be authoritative or operational however must. Examples types of code that require tests are:

* Code meant to be linked against and used in other peoples projects (library code),
* applications that run operationally,
* code that uses data to generates a product or result that others will then use and trust.

In short, all code which is to be trusted must be tested.

## Commits

Our ticketing and CI/CD tools may be configured to sync statuses amongst each
other. Commits play an important role in this process. Please start all commits
with the Github ticket number associated with your feature, task, or bug. All
commit messages should follow the format "Issue #XXXX: [Your commit message here]"

## Code standards

Python projects should confirm to [PEP 8][pep8] unless stated otherwise. A quick
summery on naming conventions can be found [here][pnames].

## Disclaimer

For now, the CMR development team will be taking a lead on reviewing all pull
requests submitted. Only requests that meet the standard of quality set forth by
existing code, following the patterns set forth by existing code, and adhering
to the design patterns set forth by existing UI elements will be considered
and/or accepted. It is expected that these rules will change and evolve as more
groups become involved.

For general tips on open source contributions, see [Contributing to Open Source][contrib]
on GitHub.

[new]: "https://github.com/nasa/eo-metadata-tools/issues/new/choose" "Create Ticket"
[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[pnames]: https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html "Python Naming Convention"
[contrib]: https://guides.github.com/activities/contributing-to-open-source/ "Contributhing to open source"

