from fasthtml.common import *
# KORREKTUR: Expliziter Import der SVG-Elemente, um den NameError zu beheben
from fasthtml.svg import Svg, Line, Text, Polyline

import matplotlib.pyplot as plt
import pandas as pd

# Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, asset_id, model):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name
        
        # Return the output from the
        # parent class's build_component method
        return super().build_component(asset_id, model)
    
    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, asset_id, model):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names()


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, asset_id, model):
        
        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        return H1(model.name.capitalize() if model.name else "")
          

# KORREKTUR: Erbt von BaseComponent und nutzt natives SVG, um Achsenbeschneidung zu verhindern
# Create a subclass of base_components/BaseComponent
# called `LineChart`
class LineChart(BaseComponent):
    
    # Overwrite the parent class's `build_component` method
    def build_component(self, asset_id, model):

        # Pass the `asset_id` argument to the model's `event_counts` method
        df = model.event_counts(asset_id)
        
        # ABSICHERUNG: Falls das DataFrame leer ist oder keine Zeilen hat
        if df is None or df.empty:
            df = pd.DataFrame([['2026-01-01', 0, 0]], columns=['event_date', 'positive_events', 'negative_events'])
        
        # Datentransformation (kumulierte Summen bilden)
        df = df.fillna(0).set_index('event_date').sort_index().cumsum()
        df.columns = ['Positive', 'Negative']
        
        # Datenpunkte für SVG extrahieren
        pos_values = df['Positive'].tolist()
        neg_values = df['Negative'].tolist()
        dates = df.index.tolist()
        
        max_val = max(max(pos_values, default=1), max(neg_values, default=1), 1)
        steps = len(dates)
        
        # Koordinaten-Berechnung für das SVG-Spielfeld
        w, h = 500, 300
        padding = 45
        chart_w = w - 2 * padding
        chart_h = h - 2 * padding
        
        pos_points = []
        neg_points = []
        
        for i in range(steps):
            x = padding + (i * chart_w / max(1, steps - 1))
            y_pos = h - padding - (pos_values[i] * chart_h / max_val)
            y_neg = h - padding - (neg_values[i] * chart_h / max_val)
            pos_points.append(f"{x},{y_pos}")
            neg_points.append(f"{x},{y_neg}")
            
        pos_path = " ".join(pos_points)
        neg_path = " ".join(neg_points)
        
        start_date = str(dates[0]) if dates else ""
        end_date = str(dates[-1]) if dates else ""

        # Rückgabe eines sauberen SVG-Liniendiagramms inklusive Achsen & Labels
        return Div(
            H3('Cumulative Events Over Time', style="font-weight: bold; margin-bottom: 10px; font-size: 1.1rem; text-align: center;"),
            Div(
                Span("— Positive", style="color: #1f77b4; font-weight: bold; margin-right: 15px; font-size: 0.85rem;"),
                Span("— Negative", style="color: #ff7f0e; font-weight: bold; font-size: 0.85rem;"),
                style="display: flex; justify-content: center; margin-bottom: 10px;"
            ),
            Svg(
                # Achsenlinien
                Line(x1=padding, y1=h-padding, x2=w-padding, y2=h-padding, stroke="#ccc", stroke_width="2"),
                Line(x1=padding, y1=padding, x2=padding, y2=h-padding, stroke="#ccc", stroke_width="2"),
                
                # Y-Achsentext
                Text(str(int(max_val)), x=padding-10, y=padding+5, text_anchor="end", font_size="10", fill="#666"),
                Text("0", x=padding-10, y=h-padding+5, text_anchor="end", font_size="10", fill="#666"),
                
                # X-Achsentext
                Text(start_date, x=padding, y=h-padding+20, text_anchor="start", font_size="10", fill="#666"),
                Text(end_date, x=w-padding, y=h-padding+20, text_anchor="end", font_size="10", fill="#666"),
                
                # Linienpfade
                Polyline(points=pos_path, fill="none", stroke="#1f77b4", stroke_width="3", stroke_dasharray="8,4" if steps > 1 else "0"),
                Polyline(points=neg_path, fill="none", stroke="#ff7f0e", stroke_width="3", stroke_dasharray="8,4" if steps > 1 else "0"),
                
                viewBox=f"0 0 {w} {h}",
                style="width: 100%; height: auto;"
            ),
            style="padding: 20px; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%; max-width: 500px; margin: 0 auto;"
        )


# KORREKTUR: Erbt von BaseComponent und nutzt ein sauberes, begrenztes CSS-Layout
# Called `BarChart`
class BarChart(BaseComponent):

    # Create a `predictor` class attribute
    # assign the attribute to the output of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `build_component` method
    def build_component(self, asset_id, model):

        # Using the model and asset_id arguments
        # pass the `asset_id` to the `.model_data` method
        data = model.model_data(asset_id)
        
        # Absicherung für leere Teams / Mitarbeiter ohne Eventdaten
        if data.empty or data.dropna(how='all').empty or data.fillna(0).sum().sum() == 0:
            pred = 0.0
        else:
            data = data.fillna(0)
            predict_proba_output = self.predictor.predict_proba(data)
            risk_prob = predict_proba_output[:, 1]
            pred = risk_prob.mean() if model.name == "team" else risk_prob[0]

        # Prozentwert kalkulieren
        percentage = round(pred * 100, 1)
        
        # Dynamische Ampelfarben je nach Risiko
        if percentage < 30:
            bar_color = "#2ecc71"  # Grün
        elif percentage < 70:
            bar_color = "#f1c40f"  # Gelb
        else:
            bar_color = "#e74c3c"  # Rot

        # Rückgabe eines nativen, modernen HTML-Fortschrittsbalkens mit Breitenbegrenzung
        return Div(
            H3('Predicted Recruitment Risk', style="font-weight: bold; margin-bottom: 15px; font-size: 1.1rem; text-align: center;"),
            Div(
                Div(
                    style=f"width: {percentage}%; background-color: {bar_color}; height: 25px; border-radius: 4px; transition: width 0.5s ease;"
                ),
                style="background-color: #f0f0f0; border-radius: 4px; width: 100%; height: 25px; border: 1px solid #ddd; overflow: hidden; margin-bottom: 8px;"
            ),
            Div(
                Span(f"Wahrscheinlichkeit: {percentage}%", style="font-weight: 500; font-size: 0.9rem; color: #555;"),
                style="display: flex; justify-content: center;"
            ),
            style="padding: 20px; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%; max-width: 450px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center;"
        )
 

# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):

    # Set the `children` class attribute to a list
    # containing an initialized instance of `LineChart` and `BarChart`
    children = [LineChart(), BarChart()]

    # KORREKTUR: Wir erzwingen ein zweispaltiges Grid nebeneinander mit ausreichend Abstand (gap)
    outer_div_type = Div(style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; align-items: stretch; margin: 20px 0;")
            

# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model):
        
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes method. Return the output
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    

# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):

    # Set the `children` class attribute to a list
    # containing initialized instances of the header, dashboard filters,
    # data visualizations, and notes table
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# Initialize a fasthtml app 
app = FastHTML()

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@app.get('/')
def get():
    # Call the initialized report
    # pass the integer 1 and an instance of the Employee class as arguments
    return report(1, Employee())


# Create a route for a get request
# Set the route's path to receive a request for an employee ID
@app.get('/employee/{id}')
def get_employee(id: str):
    # Call the initialized report
    return report(id, Employee())


# Create a route for a get request
# Set the route's path to receive a request for a team ID
@app.get('/team/{id}')
def get_team(id: str):
    # Call the initialized report
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    

serve()