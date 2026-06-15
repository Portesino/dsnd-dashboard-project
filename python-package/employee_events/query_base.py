# Import any dependencies needed to execute sql queries
import pandas as pd
from .sql_execution import QueryMixin  # Importiert das Mixin statt der alten Funktionen

# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
class QueryBase(QueryMixin):  # Erbt jetzt vom QueryMixin, damit self.pandas_query() verfügbar ist

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ""

    # Define a `names` method that receives
    # no passed arguments
    def names(self):
        
        # Return an empty list
        return []


    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id):

        # QUERY 1
        query = f"""
            SELECT ee.event_date
                 , SUM(ee.positive_events) AS total_positive
                 , SUM(ee.negative_events) AS total_negative
            FROM {self.name} t
            JOIN employee_events ee 
                ON t.{self.name}_id = ee.{self.name}_id
            WHERE t.{self.name}_id = {id}
            GROUP BY ee.event_date
            ORDER BY ee.event_date
        """
        
        # Nutzen der Mixin-Methode statt der alten get_connection-Logik
        return self.pandas_query(query)
    

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id):

        # QUERY 2
        query = f"""
            SELECT n.note_date
                 , n.note
            FROM notes n
            JOIN {self.name} t 
                ON n.{self.name}_id = t.{self.name}_id
            WHERE t.{self.name}_id = {id}
        """
        
        # Nutzen der Mixin-Methode statt der alten get_connection-Logik
        return self.pandas_query(query)