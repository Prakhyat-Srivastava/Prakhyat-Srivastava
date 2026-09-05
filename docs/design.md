# Profile design and maintenance

An original **Data Observatory** identity: deep navy, cyan and restrained mint accents, a geometric data network, readable Markdown and repository-hosted graphics. The header animation runs twice and stops; a reduced-motion variant is included. All essential information also appears as text.

## Update the profile

- Edit `README.md` outside the marked generated sections for technical project notes, background and links. Featured descriptions, push dates, stars, forks and the recent-repository list refresh from repository metadata. New public projects appear in the recent list automatically; the four highlighted projects remain deliberately curated.
- Edit `assets/header.svg` and its static counterpart together.
- Refresh statistics with `python3 scripts/update_stats.py`, or run **Refresh public profile statistics** in Actions. Scheduled once daily at 03:17 UTC; GitHub may delay scheduled runs or disable inactive schedules.
- Cards retain their last committed content if a fetch, data validation or workflow run fails. Their dates identify freshness. No external live statistics widgets or personal access tokens are required.
- The workflow uses the repository's short-lived `GITHUB_TOKEN` with only contents write permission. Public data is fetched; no private repositories are inspected. Commits are attributed to the Actions bot.
- `docs/activity.md` and `assets/stats-data.json` expose the definitions and underlying calendar data.
- Review certification validity dates when updating credentials.

## Sources for profile facts

Reviewed September 5, 2026:

- [Current portfolio data](https://github.com/Prakhyat-Srivastava/My_Portfolio/blob/main/js/data.js): education, training, internship, tools and public contact links. Current source superseded an outdated search-engine copy.
- Featured project READMEs, directory trees, Flask application source and movie model-training script: descriptions reflect committed work, not assumed deployments or business impact.
- Certificate images linked in the README: names, credential titles and dates inspected. No unverified skill ratings, ranks, metrics or indexing claims were added.
- [Journal article](https://journal.esrgroups.org/jes/article/view/8003): title, co-authorship, year and DOI verified.

## Design research

- [DenverCoder1](https://github.com/DenverCoder1): separates project evidence, tools and activity.
- [anuraghazra](https://github.com/anuraghazra): concise professional positioning and specific project links.
- [abhisheknaiidu](https://github.com/abhisheknaiidu): recognizable personal visual identity.
- [GitHub accessibility guidance](https://github.blog/developer-skills/github/5-tips-for-making-your-github-profile-page-accessible/): meaningful alt text, native headings and accessible links.
- [GitHub Readme Stats documentation](https://github.com/anuraghazra/github-readme-stats): documents shared-service reliability limits; this design generates its own cached assets instead.

These profiles informed hierarchy and restraint; the artwork and content are original to this profile.

## Graphic attribution

Technology badges were generated with [Shields.io](https://shields.io/) and stored locally. Embedded brand marks are supplied through its [Simple Icons](https://simpleicons.org/) integration and remain trademarks of their owners. Text-only badges are used where no matching mark was selected. Badges represent tools evidenced in public projects or the portfolio, not endorsements. The header and divider are original SVG artwork. The dashboard screenshot belongs to the linked project and remains hosted in its original repository.
