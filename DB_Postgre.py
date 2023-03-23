import psycopg2

# Fixed connection bug by reconnecting

class PostgreDBManager:
    __connection = None
    __cursor = None

    def commit(self, query, args=()):
        # Use for INSERT UPDATE, DELETE statements.
        # Returns: The number of rows affected by the query (a non-negative int).
        self.__connect()
        self.__execute(query, args)
        self.__connection.commit()
        affected_rows = self.__cursor.rowcount
        self.__close_connection()
        return affected_rows

    def fetch(self, query, args=()):
        # Use for SELECT statement.
        # Returns: False if the query failed, or the result of the query if it succeeded.
        query_result = False
        self.__connect()
        if self.__execute(query, args):
            query_result = self.__cursor.fetchall()
        self.__close_connection()
        return query_result

    def execute(self, query, args=()):
        # Use for CREATE, DROP AND ALTER statements.
        self.__connect()
        query_result = self.__execute(query, args)
        self.__close_connection()
        return query_result

    def __connect(self):
        # Opens a connection to the database.
        try:
            self.__connection = psycopg2.connect(
                host="dpg-cfv2o2l3t39doavr2gsg-a.ohio-postgres.render.com",
                database="experiment1",
                user="root",
                password="tf7dK70hk7qsqeZGQgvC9YQhv6gQ1AgS")
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            print(e)

    def __execute(self, query, args=()):
        # Executes a given query with given args, if provided.
        if query:
            try:
                self.__cursor.execute(query, args)
                return True
            except Exception as error:
                print("Query failed with error {}".format(error))
        return False

    def __close_connection(self):
        # Closes an open database connection.
        try:
            if self.__connection is not None and self.__connection.is_connected():
                self.__connection.close()
            if self.__cursor is not None:
                self.__cursor.close()
        except Exception as error:
            print("Failed to close connection with error {}".format(error))


# Creates an instance for the DBManager class for export.
dbManager = PostgreDBManager()
