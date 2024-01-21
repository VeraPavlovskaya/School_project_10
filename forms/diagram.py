'''from flask_wtf import FlaskForm
from flask import Flask, render_template
import plotly.subplots as sp
import plotly.graph_objects as go
from datetime import date
import plotly.express as px
from main import login_manager


class Event(login_manager.Model):
    id = login_manager.Column(login_manager.Integer, primary_key=True)
    event_date = login_manager.Column(login_manager.Date)
    event_name = login_manager.Column(login_manager.String(100))
    feedback_id = login_manager.Column(login_manager.Integer)
    feedback_score = login_manager.Column(login_manager.Integer)
#class Dash(FlaskForm):
    def histogram(self):
        # Fetch data from the database
        events = Event.query.all()

        # Create a histogram using Plotly
        fig = px.histogram(events, x='event_date', title='Event Frequency per Date Range')

        # Update layout for better visualization
        fig.update_layout(
            xaxis_title='Event Date',
            yaxis_title='Event Frequency',
            bargap=0.2  # Adjust the gap between bars
        )

        # Save the histogram as an HTML file (optional)
        fig.write_html('templates/event_histogram.html')

        return render_template('histogram.html')
    #events = [
     #   {'name': 'Event A', 'date': date(2024, 1, 10), 'attendees': 150, 'revenue': 1},
      #  {'name': 'Event B', 'date': date(2024, 1, 15), 'attendees': 120, 'revenue': 3},
       # {'name': 'Event C', 'date': date(2024, 1, 25), 'attendees': 180, 'revenue': 2},
        # Add more events as needed
   # ]

    # Filter events for this month
    this_month_events = [event for event in events if event['date'].month == date.today().month]

    # Extract event names and attendees/revenue
    event_names = [event['name'] for event in this_month_events]
    attendees_count = [event['attendees'] for event in this_month_events]
    revenue_data = [event['revenue'] for event in this_month_events]

    # Create a subplot with two y-axes
    fig = sp.make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=event_names, y=attendees_count, name='Attendees', marker_color='blue'), secondary_y=False)
    fig.add_trace(
        go.Scatter(x=event_names, y=revenue_data, mode='lines+markers', name='Revenue', line=dict(color='red')),
        secondary_y=True)

    # Update layout to make the chart smaller
    fig.update_layout(
        title_text='Event Dashboard with Two Y-Axes',
        xaxis_title='Event',
        yaxis_title='Attendees',
        yaxis2_title='Revenue',
        height=400,  # Adjust the height
        width=600  # Adjust the width
    )

    # Save the chart as an HTML file
    fig.write_html('templates/combined_chart.html')
'''