import psycopg2 # libary connect to databas

#Database management
class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None #attribute connect to data base 
        self.cur = None
        self.open()
    def open(self): #open databse 
        #connet data base with library pycopg2
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cur = self.conn.cursor()#Database stability
    #insert value users table 
    def insert_users(self, chat_id): 
        try:
            self.open()
            self.cur.execute('INSERT INTO users(chat_id) VALUES (%s)', (chat_id,))#query database
            self.conn.commit()#seting qeury to database
        except Exception as e :
            print(f"Error insertong  user: {e}")
            self.conn.rollback()#Remove half operations
        finally :
            self.close()
    #insert value results table 
    def insert_results(self, results_game, chat_id):
            try:
                self.open()
                self.cur.execute("INSERT INTO results(results_game, chat_id) VALUES (%s ,%s)" ,(results_game, chat_id))
                self.conn.commit()
            except Exception as e:
                print(f"Error inserting result: {e} ")
                self.conn.rollback()

            finally:
                self.close()
    #fetch values users table 
    def fetch_users(self):
        try:
            self.open()
            self.cur.execute("SELECT * FROM users")
            users_data = self.cur.fetchall()
            return users_data
        except Exception as e :
            print(f"Error fetching users: {e}")
            return []
        finally:
            self.close()
    #fetch values results table
    def fetch_results(self,chat_id):
        try:
            self.open()
            self.cur.execute("SELECT *  FROM results WHERE chat_id = %s" , (chat_id,))
            results_data = self.cur.fetchall()
            return results_data
        except Exception as e :
            print(f"Error fetching results : {e}")
            return []
        finally:
            self.close()
    #update values results table 
    def update_results(self, chat_id, result_game):
        try:
            self.open()
            all_scores= self.fetch_results(chat_id)#fetch values results table
            self.open()
            if not all_scores:
                self.cur.execute("INSERT INTO results ( lost, chat_id, winner, equal) VALUES (0, %s, 0, 0)", (chat_id,))
                self.conn.commit()
                all_scores = self.fetch_results(chat_id)
                self.open()

            #The correct value setter for the table with update query
            if result_game == 'winner':
                new_score = all_scores[0][3] + 1
                self.cur.execute("UPDATE results SET winner = %s WHERE chat_id = %s", (new_score, chat_id))
            elif result_game == 'lost':
                new_score = all_scores[0][1] + 1
                self.cur.execute("UPDATE results SET lost = %s WHERE chat_id = %s", (new_score ,chat_id))
            else:
                new_score = all_scores[0][4] + 1
                self.cur.execute("UPDATE results SET equal = %s WHERE chat_id = %s", (new_score, chat_id))
            self.conn.commit()
        except Exception as e :
            print(f"Error updating result : {e}")
            self.conn.rollback()
        finally:
            self.close()
    #close of database 
    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__' :
    print('ok file mysql')
