# import sqlite3

# import pandas as pd
# import matplotlib.pyplot as plt
#from flask_wtf import FlaskForm


#class Diagr(FlaskForm):
 #   conn = sqlite3.connect('db/blogs.db')
  #  query = "SELECT * FROM feedbacks"
   # df = pd.read_sql_query(query, conn)
    #conn.close()
#    df.columns = df.columns.str.lower().str.replace(' ', '_')
 #   df['content'].value_counts().plot(kind='bar')
    # df.hist(column='content')
  #  plt.savefig('diagr_target.png')
   # plt.show()