import mysql.connector as mysql
import json

from Statics import MySQL_TYPE_MAP, DATABASE_CONFIGURATION
import Statics

class DatabaseInterface():
    def __init__(self):
        self.db_connection, self.db_cursor = self.ConnectToDB()

        if self.db_connection != False:
            self.connected = True
        else:
            self.connected = False

    def LoadDatabaseConfiguration(self, data_path=Statics.DATA_PATH, configuration_file='database_configuration.json'):
        try:
            with open(data_path + configuration_file, 'r') as fh:
                return UnpackHardwareConfiguration(json.load(fh))
        except FileNotFoundError:
            return EMPTY_HARDWARE_CONFIGURATION

    def SaveDatabaseConfiguration(self):
        pass

    def ConnectToDB(self, host='localhost', port=3306, user='raspberrypi', password='password', db=
            Statics.DATABASE_CONFIGURATION['DATABASE_NAME']):
        try:
            db_connection = mysql.connect(host=host, port=port, user=user, password=password)
            c = db_connection.cursor()
            db_connection = self.ConfigureDB(c=c, conn=db_connection, db_name=db)
            print("Database {} connection successful".format(db))
            return db_connection, c
        except mysql.errors.DatabaseError:
            print("Could not connect to database")
            return False, False

    def ConfigureDB(self, c=None, conn=None, db_name=Statics.DATABASE_CONFIGURATION['DATABASE_NAME']):
        #c = conn.cursor()
        c.execute('SHOW DATABASES')
        available_databases = c.fetchall()

        if db_name not in [database[0] for database in available_databases]:
            #ConfigureDB(conn=db_connection, c=c, db_name=db)
            c.execute('CREATE DATABASE ' + db_name)

        conn.config(database=db_name)
        conn.reconnect()

        self.ConfigureTables(c=c)

        return conn

    def ConfigureTables(self, c=None, tables=Statics.DATABASE_CONFIGURATION['TABLES']):
        c.execute('SHOW TABLES')
        existing_tables = [table[0] for table in c.fetchall()]
        for table in tables:
            if table not in existing_tables:
                cols = BuildColumnFormatString(tables[table])
                c.execute("CREATE TABLE " + table + ' ' + cols)

    def InsertData(self, conn=None, c=None, table='', data={}, db_configuration=Statics.DATABASE_CONFIGURATION):
        query = 'INSERT INTO ' + table

        col_string = '('
        val_string = 'VALUES ('
        dataset = []
        for col in data:
            col_string += col + ', '
            val_string += Statics.MySQL_TYPE_MAP[db_configuration['TABLES'][table][col]] + ', '
            dataset += [data[col]]
        col_string = col_string[:-2] + ')'
        val_string = val_string[:-2] + ')'

        dataset = list(map(tuple, zip(*dataset)))

        c.executemany(query + ' ' + col_string + ' ' + val_string, dataset)
        conn.commit()

def BuildColumnFormatString(columns, primary_key=True):
    if primary_key:
        column_string = '(id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, '
    else:
        column_string = '('

    for col in columns:
        column_string += col + ' ' + columns[col] + ', '
    return column_string[:-2] + ')'

# if __name__ == '__main__':
#     conn, c = ConnectToDB()
#     conn = ConfigureDB(c=c, conn=conn)
#     t = time.strftime('%Y-%m-%d %H:%M:%S')
#     InsertData(conn=conn, c=c, table='sensor_data', data={'timestamp': [t,t,t], 'temp1': [11,12,13], 'temp2': [1,2,3], 'highside_pressure': [6,6,7]})
#     InsertData(conn=conn, c=c, table='sensor_data',
#                data={'timestamp': [t, t, t], 'temp1': [11, 12, 13], 'temp2': [1, 2, 3]})
