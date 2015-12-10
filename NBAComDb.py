import MySQLdb

class NBAComDb:

    def insert_538player(cursor, myDict):
        placeholders = ', '.join(['%s'] * len(myDict))
        columnstring = ', '.join(myDict.keys())
        sql = "INSERT into %s ( %s ) VALUES ( %s )" % ('projections538', columnstring, placeholders)

        try:
            cursor.execute(sql, myDict.values())

        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)

    def yearly_playerstats():
        try:
            for row_set in result_set['rowSet']:
                player = dict(zip(headers, row_set))
                player['season'] = int(os.path.basename(fn)[0:4])
                placeholders = ', '.join(['%s'] * len(player))
                columns = ', '.join(player.keys())
                logging.debug(player)
          
                if '_basic' in fn:
                    sql = "INSERT into %s ( %s ) VALUES ( %s )" % ('yearly_playerstats_basic', columns, placeholders)
                    cursor.execute(sql, player.values())
                    logging.debug(cursor._last_executed) 

                elif '_advanced' in fn:
                    sql = "INSERT into %s ( %s ) VALUES ( %s )" % ('yearly_playerstats_advanced', columns, placeholders)
                    cursor.execute(sql, player.values())
                    logging.debug(cursor._last_executed) 

                else:
                    logging.debug('filename %s does not contain basic or advanced' % fn)
       
            # if all works, then commit changes
            db.commit()
           
        except MySQLdb.Error, e:
 
            try:
                logging.info(cursor._last_executed) 
                logging.error("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
 
            except IndexError:
                logging.error("MySQL Error: %s" % str(e))
 
            finally:
                db.rollback()      
 
