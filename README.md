# redcrab
![redcrabs](https://danuka.files.wordpress.com/2013/06/red-crab-migration-6.jpg)

Crawl through reddit comments using the Reddit API. Save them to a database 
for later analysis.

## Description
Redcrab was envisioned as a way to crawl through all reddit submissions and grab all comments
in those submissions and store them in a database in a totally flat manner. Comments are not
nested in any way, although this could potentially be done with foreign keys or a graph db in
the future. This has upsides and downsides. Downside that we cannot more closely reference the context in 
which information is actually stored in reddit but good for our goal of basic information retrieval.

As of this moment we assume that postgresql is being used as a database although if needed
other backends like MySQL can be created with a bit of extra work.

## Usage
### Setup the database
`redcrab` allows you to automatically to setup the database we want to use without going through all the 
pain of setting the schema up manually

    make_redcrab_db --db-user postgres

### Store Reddit comments
Store Reddit comments through the command line

    redcrab <subreddit> --user-agent <user agent> --username <reddit username> --method <how should we get submissions?>

A minimal example getting all top posts for today:

    redcrab funny --user-agent redcrab --method get_top

If you want to connect to a remote database:

    redcrab funny --user-agent redcrab --db-host mydb-host --method get_hot

If you want to authenticate with a reddit username to increase the number of actions per minute:

    redcrab funny --user-agent redcrab --username foobar --method get_controversial

## Schema
Right now the schema is very basic. We are simply storing the author name, their comment, and
the comment id. The submission id can be used as a foreign key to link comments to submissions.
This is not necessary however. If desired a different schema can be set up through the `postgres_schema.py` file.
At the moment the implementation of storing comments and submissions is rather hard coded but this
can change easily as well.


## Caveats
There is one major caveat to using this tool; the rate limiting of the Reddit API. `redcrab`
uses the `praw` library and `praw` limits all Reddit API requests down to 30 a minute or 60
if we have authenticated our user. Reddit claims banning penalties against clients that
go above this limit. As a result `redcrab` can conceivably only grab up to 60 comments a minute
running on a single host. I know this is slow but for now this problem is unavoidable.
