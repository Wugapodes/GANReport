# GANReport

Good Article Nomination Report (GANReport) helps Wikipedia volunteers see which articles are waiting for review and where their attention is needed. Running since 2016, it turns the English Wikipedia nomination queue into a public report and a historical record of the backlog, published by [WugBot](https://en.wikipedia.org/wiki/User:WugBot).

Wikipedia's Good Articles are articles that have passed a volunteer review for writing, accuracy, sourcing, neutrality, and coverage. The project began in October 2005 as a way to recognize good work without requiring the breadth of a Featured Article; by 2006, it had developed a more formal nomination and review process. Writing an article and finding someone to review it are different challenges. Concerns about the waiting list appeared by late 2006 and early 2007 when the backlog grep to over 100 nominations. The backlog report was started by May 2007 to help organize the process. 

## Explore the project

- [Read the report](https://en.wikipedia.org/wiki/Wikipedia:Good_article_nominations/Report) for the backlog summary and nominations needing attention.
- [Browse the backlog archive](https://en.wikipedia.org/wiki/Wikipedia:Good_article_nominations/Report/Backlog_archive) for historical observations.
- [Visit Good Article nominations](https://en.wikipedia.org/wiki/Wikipedia:Good_article_nominations) to learn about nominating or reviewing an article.
- [**Taking stock of the Good Article backlog**](https://en.wikipedia.org/wiki/Wikipedia:Wikipedia_Signpost/2016-11-26/Special_report) a 2016 report on review demand, volunteer supply, and editor fatigue in the Good ARticle review process.

## The Good Article Nomination Report

The program reads the nomination page, identifies articles and their review states, and produces a summary that editors can act on. It helps Good Article process participants find:

- **Articles waiting longest:** nominations that have yet to receive a review.
- **Reviews needing attention:** reviews, holds, and second-opinion requests that have remained marked for more than seven days.
- **The shape of the queue:** counts by topic and review stage, plus nominations grouped by nominator.
- **Changes over time:** dated backlog totals preserved in the report archive.
- **Errors to fix:** malformed nominations and reviews causing template or bot errors.

For example, an editor looking for an article to review can consult the oldest-nominations list. Someone organizing a review drive can use the archive to understand how the queue changed before, during, and after an event. Maintainers can find pages where someone formatted the nomination wrong and fix it.

Behind the report is Python code that extracts structured information from Wikipedia's community-maintained text and automates publication through Pywikibot. The project brings together text processing, public reporting, historical data collection, and long-term maintenance of a tool used by a volunteer community.

## Try the code

With Python 3.11 or newer, install from a checkout and view the command-line options:

```sh
python -m pip install -r requirements.txt -e .
ganreport --help
```

Running reports requires Pywikibot configuration and an existing local backlog file. The default dry-run mode leaves wiki pages untouched but updates that local file. The parser can also read saved nomination-page text without publishing anything.

## Ongoing work

The separate [`database` branch](https://github.com/Wugapodes/GANReport/tree/database) extends the project with Django/MariaDB storage of individual nomination observations and an interactive dashboard. It builds on the report archive to support closer study of waiting times, review activity, and the changing backlog.

GANReport is available under the [MIT License](LICENSE.txt).
