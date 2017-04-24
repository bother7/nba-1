pg_dump -U nbadb -s $(psql -c "select * FROM listViews" nbadb) nbadb > views.nbadb.sql
