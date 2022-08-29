# Superset

We have been using [APACHE Superset](https://superset.apache.org) to build dashboards, and return results to users. It is similar to PowerBI and Tableau, but open source and free. It was originally developed by AirBnB. We run a dockererised version of the dashboard on the standard port 8080, and you can reach the log-in page for our instance at http://uclvlddpragae08:8088/. You'll need access to the GAE, and to be familiar with git and docker if you wish to deploy your own version. Don't forget to update the proxy settings before `docker-compose up -d`.

```{image} ../figs/superset-ids-demo.png
:alt: superset-ids-demo
:width: 400px
:align: right
```

Once installed then to build a dashboard, you need the following steps.

1. Log in to Superset
2. Connect a database (e.g. the UDS)
3. Connect to a data set within the database (e.g. a table within a schema)
4. Build a chart using the point and click interface
5. Place the chart on a dashboard

Issues/Todos
- dates need to be cast as timestamps for some charts. You can do this using a calculated column (e.g. `mydate::timestamp`)
- timezone need to be aligned to UTC (e.g. `timestamp('UTC', mytimestamp)`).
- permissions are tricky and as yet I have not been able to find an implementation that doesn't give access to row level data


