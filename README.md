# redcrab
![redcrabs](https://danuka.files.wordpress.com/2013/06/red-crab-migration-6.jpg)

Crawl through reddit comments using the Reddit API. Save them to a database 
for later analysis.

## Description
Redcrab was envisioned as a way to crawl through all reddit submissions and grab all comments
in those submissions and store them in a database in a totally flat manner. Comments are not
nested in any way, although this could potentially be done with foreign keys or a graph db in
the future. This is good and bad. Bad that we cannot more closely reference the context in 
which information is actually store in reddit but good for our goal of basic information retrieval.

## Usage
Through the command line

    redcrab <subreddit> --user-agent <user agent> --username <reddit username>

A minimal example:

    redcrab funny --user-agent redcrab

If you want to connect to a remote database:

    redcrab funny --user-agent redcrab --db-host mydb-host

## Schema
Right now the schema is very basic. We are simply storing the author name, their comment, and
the comment id. The submission id can be used as a foreign key to link comments to submissions.
This is not necessary however. In fact no concrete schema has been put in place nor has a
postgres table schema file been generated. This is probably the next thing that can be done.

## Caveats
There is one major caveat to using this tool; the rate limiting of the Reddit API. `redcrab`
uses the `praw` library and `praw` limits all Reddit API requests down to 30 a minute or 60
if we have authenticated our user. Reddit claims banning penalties against clients that
go above this limit. As a result `redcrab` can conceivably only grab up to 60 comments a minute
running on a single host. I know this is slow but for now this problem is unavoidable.
